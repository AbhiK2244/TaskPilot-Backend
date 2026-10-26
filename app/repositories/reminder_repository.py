from sqlmodel import Session, select

from app.models.reminder import ReminderLog, ReminderPreference


def get_preference(session: Session) -> ReminderPreference | None:
    return session.get(ReminderPreference, 1)


def save_preference(session: Session, preference: ReminderPreference) -> ReminderPreference:
    print(f"Saving preference: {preference}")
    session.add(preference)
    print("Committing session...")
    session.commit()
    print("Refreshing preference...")
    session.refresh(preference)
    print(f"Preference saved: {preference}")
    return preference


def get_log_by_occurrence(session: Session, occurrence_key: str) -> ReminderLog | None:
    statement = select(ReminderLog).where(ReminderLog.occurrence_key == occurrence_key)
    return session.exec(statement).first()


def save_log(session: Session, log: ReminderLog) -> ReminderLog:
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def get_history(session: Session, limit: int, offset: int) -> list[ReminderLog]:
    statement = select(ReminderLog).order_by(ReminderLog.created_at.desc()).offset(offset).limit(limit)
    return list(session.exec(statement).all())
