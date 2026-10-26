from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class ReminderSettingsUpdate(BaseModel):
    email: EmailStr | None = None
    enabled: bool = False
    reminder_times: list[str] = Field(default_factory=lambda: ["12:00", "18:00", "23:00"])
    timezone: str = "Asia/Kolkata"

    @field_validator("reminder_times")
    @classmethod
    def validate_reminder_times(cls, values: list[str]) -> list[str]:
        if not values:
            raise ValueError("Provide at least one reminder time")
        if len(set(values)) != len(values):
            raise ValueError("Reminder times must not contain duplicates")
        for value in values:
            try:
                hour, minute = value.split(":")
                if len(hour) != 2 or len(minute) != 2:
                    raise ValueError
                if not 0 <= int(hour) <= 23 or not 0 <= int(minute) <= 59:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError(f"Invalid reminder time '{value}'. Use HH:MM, for example 18:00.")
        return values

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("timezone must be a valid IANA timezone, for example Asia/Kolkata")
        return value

    @model_validator(mode="after")
    def require_email_when_enabled(self):
        if self.enabled and not self.email:
            raise ValueError("Set a valid email address before enabling reminders")
        return self


class ReminderSettingsRead(BaseModel):
    email: EmailStr | None
    enabled: bool
    reminder_times: list[str]
    timezone: str
    created_at: datetime


class ReminderLogRead(BaseModel):
    id: int
    scheduled_for: datetime
    occurrence_key: str
    status: str
    attempt_count: int
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
