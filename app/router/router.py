from fastapi import APIRouter

from app.router import analytics, chat, reminders, tasks

api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Assistant"])
api_router.include_router(reminders.router, prefix="/reminders", tags=["Reminders"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
