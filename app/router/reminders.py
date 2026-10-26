from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.database import get_session
from app.schemas.reminder import ReminderLogRead, ReminderSettingsRead, ReminderSettingsUpdate
from app.services import reminder_service

router = APIRouter()


@router.get("/settings", response_model=ReminderSettingsRead)
def get_reminder_settings(session: Session = Depends(get_session)):
    return reminder_service.get_settings(session)


@router.put("/settings", response_model=ReminderSettingsRead)
def update_reminder_settings(
    payload: ReminderSettingsUpdate,
    session: Session = Depends(get_session),
):
    return reminder_service.update_settings(session, payload)


@router.get("/history", response_model=list[ReminderLogRead])
def get_reminder_history(
    session: Session = Depends(get_session),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return reminder_service.get_history(session, limit, offset)


@router.post("/trigger")
def trigger_reminder(session: Session = Depends(get_session)):
    result = reminder_service.trigger_now(session)
    if result["status"] == "failed":
        raise HTTPException(status_code=502, detail=result)
    return result
