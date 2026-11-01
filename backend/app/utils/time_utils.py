from datetime import datetime, timezone


def current_epoch_ms() -> int:
    """Return current UTC time in milliseconds."""
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def epoch_ms_to_datetime(ms: int) -> datetime:
    """Convert epoch milliseconds to a UTC datetime object."""
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)


def format_epoch_ms(ms: int, fmt: str = "%Y-%m-%d %H:%M:%S UTC") -> str:
    """Format epoch milliseconds to ISO-like UTC string."""
    dt = epoch_ms_to_datetime(ms)
    return dt.strftime(fmt)


def hours_ago_epoch_ms(hours: int) -> int:
    """Get epoch ms corresponding to N hours ago."""
    now_ms = current_epoch_ms()
    return now_ms - (hours * 3600 * 1000)


def iso_to_epoch_ms(iso_str: str | None) -> int:
    """Convert an ISO-8601 timestamp string to epoch milliseconds UTC.
    Handles 'Z', timezone offsets, and falls back to current_epoch_ms() on parse error.
    """
    if not iso_str:
        return current_epoch_ms()
    try:
        clean = iso_str.strip()
        if clean.endswith("Z"):
            clean = clean[:-1] + "+00:00"
        dt = datetime.fromisoformat(clean)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)
    except Exception:
        return current_epoch_ms()

