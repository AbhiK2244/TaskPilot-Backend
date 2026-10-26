from sqlmodel import Session
from datetime import datetime, timezone

from app.core.dates import to_utc_naive, utc_now_naive
from app.models.task import Task
from app.repositories import task_repository
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(session: Session, payload: TaskCreate) -> Task:
    task = Task(
        title=payload.title.strip(),
        description=payload.description,
        priority=payload.priority,
        due_at=payload.due_at,
        estimated_minutes=payload.estimated_minutes,
        status="pending",
    )
    return task_repository.create(session, task)


def get_task(session: Session, task_id: int) -> Task | None:
    return task_repository.get_by_id(session, task_id)


def list_tasks(
    session: Session,
    task_status: str | None = None,
    priority: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Task]:
    return task_repository.list_tasks(session, task_status, priority, limit, offset)


def list_all_tasks(session: Session) -> list[Task]:
    return task_repository.list_tasks(session, limit=10000, offset=0)


def update_task(session: Session, task: Task, payload: TaskUpdate) -> Task:
    updates = payload.model_dump(exclude_unset=True)
    for field in ("title", "status", "priority"):
        if field in updates and updates[field] is None:
            raise ValueError(f"{field} cannot be null")

    if "title" in updates:
        updates["title"] = updates["title"].strip()
        if not updates["title"]:
            raise ValueError("title cannot be empty")

    if "due_at" in updates:
        updates["due_at"] = to_utc_naive(updates["due_at"])

    new_status = updates.get("status", task.status)
    if new_status == "completed" and task.status != "completed":
        task.completed_at = datetime.now(timezone.utc)
    elif new_status != "completed":
        task.completed_at = None

    for field, value in updates.items():
        setattr(task, field, value)
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task: Task) -> None:
    task_repository.delete(session, task)
