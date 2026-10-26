from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.task import TaskCreate, TaskPriority, TaskRead, TaskStatus, TaskUpdate
from app.services import task_service

router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, session: SessionDep):
    return task_service.create_task(session, payload)


@router.get("", response_model=list[TaskRead])
def list_tasks(
    session: SessionDep,
    task_status: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return task_service.list_tasks(session, task_status, priority, limit, offset)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: SessionDep):
    task = task_service.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(task_id: int, payload: TaskUpdate, session: SessionDep):
    task = task_service.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if not payload.model_fields_set:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")

    for field in ("title", "status", "priority"):
        if field in payload.model_fields_set and getattr(payload, field) is None:
            raise HTTPException(status_code=422, detail=f"{field} cannot be null")

    try:
        return task_service.update_task(session, task, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, session: SessionDep):
    task = task_service.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_service.delete_task(session, task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
