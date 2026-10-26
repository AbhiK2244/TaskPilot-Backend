from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.database import get_session
from app.services import analytics_service
from app.schemas.task import TaskRead

router = APIRouter()


@router.get("/summary")
def get_summary(session: Session = Depends(get_session)):
    return analytics_service.get_summary(session)


@router.get("/status-breakdown")
def get_status_breakdown(session: Session = Depends(get_session)):
    return analytics_service.get_status_breakdown(session)


@router.get("/overdue", response_model=list[TaskRead])
def get_overdue_tasks(session: Session = Depends(get_session)):
    return analytics_service.get_overdue_tasks(session)
