from __future__ import annotations

from datetime import UTC, datetime


def parse_iso_datetime(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise ValueError("Datetime cannot be empty")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    parsed = datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def parse_optional_iso_datetime(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    return parse_iso_datetime(text)


def to_iso_seconds_utc(value: datetime) -> str:
    dt = value if value.tzinfo else value.replace(tzinfo=UTC)
    return dt.isoformat(timespec="seconds")


def to_iso_datetime_text(value: object) -> str:
    if value is None:
        return ""

    if isinstance(value, datetime):
        return to_iso_seconds_utc(value)

    to_pydatetime = getattr(value, "to_pydatetime", None)
    if callable(to_pydatetime):
        dt = to_pydatetime()
        if isinstance(dt, datetime):
            return to_iso_seconds_utc(dt)

    return str(value).strip()
