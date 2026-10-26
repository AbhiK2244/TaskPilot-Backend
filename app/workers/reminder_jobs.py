from sqlmodel import Session

from app.db.database import engine
from app.services.reminder_service import get_or_create_settings, run_scheduled_reminder


def sync_reminder_jobs(scheduler) -> None:
    with Session(engine) as session:
        preference = get_or_create_settings(session)
        enabled = preference.enabled and bool(preference.email)
        times = list(preference.reminder_times) if enabled else []
        timezone_name = preference.timezone

    desired = set()
    for value in times:
        hour_text, minute_text = value.split(":")
        hour, minute = int(hour_text), int(minute_text)
        zone_key = timezone_name.replace("/", "_")
        job_id = f"reminder-{zone_key}-{hour:02d}{minute:02d}"
        desired.add(job_id)

        if scheduler.get_job(job_id) is None:
            from apscheduler.triggers.cron import CronTrigger
            from zoneinfo import ZoneInfo

            scheduler.add_job(
                run_scheduled_reminder,
                trigger=CronTrigger(hour=hour, minute=minute, timezone=ZoneInfo(timezone_name)),
                id=job_id,
                args=[hour, minute, timezone_name],
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )

    for job in scheduler.get_jobs():
        if job.id.startswith("reminder-") and job.id not in desired:
            scheduler.remove_job(job.id)
