from sqlmodel import Session, select

from app.models.task import Task


def create(session: Session, task: Task) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_by_id(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)


def list_tasks(
    session: Session,
    task_status: str | None = None,
    priority: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Task]:
    statement = select(Task)
    if task_status:
        statement = statement.where(Task.status == task_status)
    if priority:
        statement = statement.where(Task.priority == priority)
    statement = statement.order_by(Task.created_at.desc()).offset(offset).limit(limit)
    return list(session.exec(statement).all())


def delete(session: Session, task: Task) -> None:
    session.delete(task)
    session.commit()
