from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from app.core.config import settings


def utc_now_naive() -> datetime:
    """Return UTC time without tzinfo for consistent database storage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(value: datetime | None, timezone_name: str | None = None) -> datetime | None:
    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo(timezone_name or settings.timezone))

    return value.astimezone(timezone.utc).replace(tzinfo=None)


def utc_naive_to_local(value: datetime, timezone_name: str) -> datetime:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(ZoneInfo(timezone_name))


def local_day_bounds_utc_naive(timezone_name: str) -> tuple[datetime, datetime]:
    local_now = datetime.now(ZoneInfo(timezone_name))
    start_local = datetime.combine(local_now.date(), time.min, tzinfo=ZoneInfo(timezone_name))
    end_local = start_local + timedelta(days=1)
    return to_utc_naive(start_local), to_utc_naive(end_local)


def parse_iso_datetime(value: str) -> datetime:
    """Parse the ISO datetime string used by the AI tools."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
