from datetime import datetime, timezone
from sqlmodel import Session

from app.core.dates import local_day_bounds_utc_naive, utc_now_naive
from app.core.config import settings
from app.services.task_service import list_all_tasks


def get_overdue_tasks(session: Session):
    now = datetime.now(timezone.utc)
    tasks = list_all_tasks(session)
    return [task for task in tasks if task.status != "completed" and task.due_at is not None and task.due_at < now]


def get_summary(session: Session) -> dict:
    tasks = list_all_tasks(session)
    now = datetime.now(timezone.utc)
    # day_start, day_end = local_day_bounds_utc_naive(settings.timezone)

    # 2. Get the naive bounds, and attach UTC timezone info to them
    naive_day_start, naive_day_end = local_day_bounds_utc_naive(settings.timezone)
    day_start = naive_day_start.replace(tzinfo=timezone.utc)
    day_end = naive_day_end.replace(tzinfo=timezone.utc)

    total = len(tasks)
    pending = sum(task.status == "pending" for task in tasks)
    in_progress = sum(task.status == "in_progress" for task in tasks)
    completed = sum(task.status == "completed" for task in tasks)
    overdue = sum(
        task.status != "completed" and task.due_at is not None and task.due_at < now
        for task in tasks
    )
    due_today = sum(
        task.status != "completed" and task.due_at is not None and day_start <= task.due_at < day_end
        for task in tasks
    )

    return {
        "total_tasks": total,
        "pending_tasks": pending,
        "in_progress_tasks": in_progress,
        "completed_tasks": completed,
        "overdue_tasks": overdue,
        "tasks_due_today": due_today,
        "completion_percentage": round(completed * 100 / total, 2) if total else 0.0,
    }


def get_status_breakdown(session: Session) -> dict:
    tasks = list_all_tasks(session)
    counts = {"pending": 0, "in_progress": 0, "completed": 0}
    for task in tasks:
        counts[task.status] = counts.get(task.status, 0) + 1
    return {"total_tasks": len(tasks), "statuses": counts}
