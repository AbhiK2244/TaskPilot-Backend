from datetime import datetime, timezone
from pydantic import NaiveDatetime

from sqlmodel import Field, SQLModel

from app.core.dates import utc_now_naive


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: str = Field(default="pending", index=True, max_length=20)
    priority: str = Field(default="medium", index=True, max_length=20)
    due_at: datetime | None = None
    estimated_minutes: int | None = Field(default=None, ge=1)
    # FIX: Use lambda to generate timezone-aware UTC datetimes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = Field(default=None)
