from datetime import datetime, timezone as tz
from uuid import uuid4
from zoneinfo import ZoneInfo

from sqlmodel import Session

from app.core.config import settings
from app.core.dates import to_utc_naive, utc_naive_to_local, utc_now_naive
from app.models.reminder import ReminderLog, ReminderPreference
from app.repositories import reminder_repository
from app.schemas.reminder import ReminderSettingsUpdate
from app.services.email_service import send_daily_digest
from app.services.task_service import list_all_tasks


def make_timezone_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=tz.utc)
    return value.astimezone(tz.utc)


def get_or_create_settings(session: Session) -> ReminderPreference:
    preference = reminder_repository.get_preference(session)
    if preference:
        return preference

    email = settings.reminder_email.strip() or None
    preference = ReminderPreference(
        id=1,
        email=email,
        enabled=bool(email),  # If email is set, reminders are enabled
        reminder_times=["12:00", "18:00", "23:00"],
        timezone=settings.timezone,
    )
    return reminder_repository.save_preference(session, preference)


def get_settings(session: Session) -> ReminderPreference:
    return get_or_create_settings(session)


def update_settings(session: Session, payload: ReminderSettingsUpdate) -> ReminderPreference:
    preference = get_or_create_settings(session)
    preference.email = str(payload.email) if payload.email else None
    preference.enabled = payload.enabled
    preference.reminder_times = payload.reminder_times
    preference.timezone = payload.timezone
    return reminder_repository.save_preference(session, preference)


def get_history(session: Session, limit: int = 50, offset: int = 0) -> list[ReminderLog]:
    return reminder_repository.get_history(session, limit, offset)


def _task_summary(task, timezone_name: str) -> dict:
    due = utc_naive_to_local(task.due_at, timezone_name) if task.due_at else None
    return {
        "id": task.id,
        "title": task.title,
        "priority": task.priority,
        "status": task.status,
        "due_at": due.strftime("%d %b %Y, %I:%M %p") if due else "No deadline",
    }


def send_reminder(
    session: Session,
    occurrence_key: str,
    scheduled_for: datetime,
    force: bool = False,
) -> dict:
    existing = reminder_repository.get_log_by_occurrence(session, occurrence_key)
    if existing and existing.status in {"sent", "skipped"}:
        return {"status": "skipped", "message": "This reminder occurrence was already processed.", "log_id": existing.id}

    if existing:
        log = existing
        log.attempt_count += 1
        log.error_message = None
        log.status = "processing"
        log.scheduled_for = scheduled_for
    else:
        scheduled_for = make_timezone_aware(scheduled_for)
        log = ReminderLog(
            scheduled_for=scheduled_for,
            occurrence_key=occurrence_key,
            status="processing",
            attempt_count=1,
        )
        session.add(log)
    session.commit()
    session.refresh(log)

    preference = get_or_create_settings(session)
    if not force and not preference.enabled:
        log.status = "skipped"
        log.error_message = "Reminders are disabled in settings."
        reminder_repository.save_log(session, log)
        return {"status": log.status, "message": log.error_message, "log_id": log.id}

    if not preference.email:
        log.status = "skipped"
        log.error_message = "Set a reminder email address in /reminders/settings first."
        reminder_repository.save_log(session, log)
        return {"status": log.status, "message": log.error_message, "log_id": log.id}

    tasks = [task for task in list_all_tasks(session) if task.status != "completed"]
    if not tasks:
        log.status = "skipped"
        log.error_message = "No outstanding tasks to remind you about."
        reminder_repository.save_log(session, log)
        return {"status": log.status, "message": log.error_message, "log_id": log.id}

    timezone_name = preference.timezone
    local_now = datetime.now(ZoneInfo(timezone_name))
    overdue, due_today, upcoming = [], [], []

    for task in tasks:
        formatted = _task_summary(task, timezone_name)
        if task.due_at is None:
            upcoming.append(formatted)
            continue
        due_local = utc_naive_to_local(task.due_at, timezone_name)
        if due_local < local_now:
            overdue.append(formatted)
        elif due_local.date() == local_now.date():
            due_today.append(formatted)
        else:
            upcoming.append(formatted)

    try:
        send_daily_digest(preference.email, timezone_name, overdue, due_today, upcoming)
        log.status = "sent"
        log.error_message = None
        reminder_repository.save_log(session, log)
        return {
            "status": "sent",
            "message": f"Reminder email sent to {preference.email}.",
            "log_id": log.id,
            "task_count": len(tasks),
        }
    except Exception as exc:
        log.status = "failed"
        log.error_message = str(exc)[:1900]
        reminder_repository.save_log(session, log)
        return {"status": "failed", "message": log.error_message, "log_id": log.id}


def trigger_now(session: Session) -> dict:
    now = datetime.now(tz.utc)
    return send_reminder(
        session,
        occurrence_key=f"manual:{uuid4()}",
        scheduled_for=now,
        force=True,
    )


def run_scheduled_reminder(hour: int, minute: int, timezone_name: str) -> dict:
    from app.db.database import engine

    local_now = datetime.now(ZoneInfo(timezone_name)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    scheduled_for = to_utc_naive(local_now, timezone_name)
    occurrence_key = f"schedule:{timezone_name}:{local_now:%Y-%m-%dT%H:%M}"
    with Session(engine) as session:
        return send_reminder(session, occurrence_key, scheduled_for, force=False)
