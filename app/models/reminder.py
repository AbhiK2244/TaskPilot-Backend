from datetime import datetime, timezone as tz

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.core.dates import utc_now_naive


class ReminderPreference(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str | None = Field(default=None, max_length=320)
    enabled: bool = Field(default=False)
    reminder_times: list[str] = Field(
        default_factory=lambda: ["12:00", "18:00", "23:00"],
        sa_column=Column(JSON, nullable=False),
    )
    timezone: str = Field(default="Asia/Kolkata", max_length=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz.utc))


class ReminderLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    scheduled_for: datetime = Field(index=True)
    occurrence_key: str = Field(unique=True, index=True, max_length=200)
    status: str = Field(default="processing", max_length=20)
    attempt_count: int = Field(default=1, ge=1)
    error_message: str | None = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz.utc))
