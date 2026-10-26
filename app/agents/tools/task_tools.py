import json
from typing import Literal
from datetime import datetime

from langchain_core.tools import tool
from sqlmodel import Session

from app.core.dates import parse_iso_datetime
from app.db.database import engine
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import analytics_service, task_service

TaskStatusValue = Literal["pending", "in_progress", "completed"]
TaskPriorityValue = Literal["low", "medium", "high"]


def _task_dict(task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_at_utc": task.due_at.isoformat() if task.due_at else None,
        "estimated_minutes": task.estimated_minutes,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@tool
def create_task(
    title: str,
    description: str | None = None,
    priority: TaskPriorityValue = "medium",
    due_at: str | None = None,
    estimated_minutes: int | None = None,
) -> str:
    """Create a task. Use an ISO-8601 due_at value with timezone offset, or omit it when there is no deadline."""
    try:
        parsed_due_at = parse_iso_datetime(due_at) if due_at else None
        payload = TaskCreate(
            title=title,
            description=description,
            priority=priority,
            due_at=parsed_due_at,
            estimated_minutes=estimated_minutes,
        )
        with Session(engine) as session:
            task = task_service.create_task(session, payload)
            return json.dumps({"success": True, "task": _task_dict(task)})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@tool
def list_tasks(
    status: TaskStatusValue | None = None,
    priority: TaskPriorityValue | None = None,
    limit: int = 50,
) -> str:
    """List tasks, optionally filtered by status or priority."""
    try:
        with Session(engine) as session:
            tasks = task_service.list_tasks(session, status, priority, max(1, min(limit, 100)), 0)
            return json.dumps({"count": len(tasks), "tasks": [_task_dict(task) for task in tasks]})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@tool
def get_task(task_id: int) -> str:
    """Get the full details of one task by its integer ID."""
    with Session(engine) as session:
        task = task_service.get_task(session, task_id)
        if not task:
            return json.dumps({"success": False, "error": f"Task {task_id} was not found."})
        return json.dumps({"success": True, "task": _task_dict(task)})


@tool
def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    status: TaskStatusValue | None = None,
    priority: TaskPriorityValue | None = None,
    due_at: datetime | None = None,
    estimated_minutes: int | None = None,
) -> str:
    """Update a task. Pass due_at='clear' to remove its deadline; omit fields that should not change."""
    try:
        with Session(engine) as session:
            task = task_service.get_task(session, task_id)
            if not task:
                return json.dumps({"success": False, "error": f"Task {task_id} was not found."})

            updates = {}
            for key, value in {
                "title": title,
                "description": description,
                "status": status,
                "priority": priority,
                "estimated_minutes": estimated_minutes,
            }.items():
                if value is not None:
                    updates[key] = value
            if due_at is not None:
                updates["due_at"] = None if due_at.strip().lower() == "clear" else parse_iso_datetime(due_at)

            if not updates:
                return json.dumps({"success": False, "error": "Provide at least one field to update."})
            payload = TaskUpdate(**updates)
            updated = task_service.update_task(session, task, payload)
            return json.dumps({"success": True, "task": _task_dict(updated)})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@tool
def delete_task(task_id: int, confirm: bool = False) -> str:
    """Delete a task only after asking for explicit confirmation. Call with confirm=false first."""
    try:
        with Session(engine) as session:
            task = task_service.get_task(session, task_id)
            if not task:
                return json.dumps({"success": False, "error": f"Task {task_id} was not found."})
            if not confirm:
                return json.dumps({
                    "success": False,
                    "confirmation_required": True,
                    "task_id": task_id,
                    "title": task.title,
                    "message": "Ask the user to confirm before calling this tool again with confirm=true.",
                })
            title = task.title
            task_service.delete_task(session, task)
            return json.dumps({"success": True, "deleted_task_id": task_id, "title": title})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@tool
def task_progress_summary() -> str:
    """Summarize current task counts, including overdue tasks and completion percentage."""
    try:
        with Session(engine) as session:
            return json.dumps(analytics_service.get_summary(session))
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


task_tools = [create_task, list_tasks, get_task, update_task, delete_task, task_progress_summary]
