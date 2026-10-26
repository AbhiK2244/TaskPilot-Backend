from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.dates import utc_now_naive


class Conversation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    thread_id: str = Field(unique=True, index=True, max_length=200)
    created_at: datetime = Field(default_factory=utc_now_naive)
