"""Time helpers. Everything is stored in UTC; IST is only for display."""
from datetime import datetime, timedelta, timezone

TS_FORMAT = "%Y-%m-%d %H:%M:%S"  # sortable text, so SQL can compare times
IST = timezone(timedelta(hours=5, minutes=30))


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_text(moment: datetime) -> str:
    """Datetime -> 'YYYY-MM-DD HH:MM:SS' in UTC."""
    return moment.astimezone(timezone.utc).strftime(TS_FORMAT)


def parse_utc(text: str) -> str:
    """Check a user-supplied UTC time and return it in the stored format."""
    try:
        return datetime.strptime(text, TS_FORMAT).strftime(TS_FORMAT)
    except ValueError:
        raise ValueError(f"bad time '{text}', use 'YYYY-MM-DD HH:MM:SS' (UTC)") from None


def utc_text_to_ist(text: str) -> str:
    """Stored UTC text -> IST text for display."""
    utc_time = datetime.strptime(text, TS_FORMAT).replace(tzinfo=timezone.utc)
    return utc_time.astimezone(IST).strftime(TS_FORMAT)
