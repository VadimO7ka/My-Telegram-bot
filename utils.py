# utils.py
from dateutil import parser
from datetime import datetime, timezone, timedelta
import os

DEFAULT_TZ = os.getenv("DEFAULT_TZ", "UTC")

def parse_user_datetime(text: str, user_tz: str | None = None) -> datetime:
    """
    Попытка распарсить произвольную строку даты/времени пользовательского ввода.
    Возвращает timezone-aware datetime в UTC.
    """
    dt = parser.parse(text, fuzzy=True)
    # если dt наивный, предположим таймзону пользователя (или DEFAULT_TZ)
    if dt.tzinfo is None:
        import zoneinfo
        tz_name = user_tz or DEFAULT_TZ
        tz = zoneinfo.ZoneInfo(tz_name)
        dt = dt.replace(tzinfo=tz)
    # привести к UTC
    return dt.astimezone(timezone.utc)

def format_local(dt_utc: datetime, tz_name: str) -> str:
    import zoneinfo
    local = dt_utc.astimezone(zoneinfo.ZoneInfo(tz_name))
    return local.strftime("%Y-%m-%d %H:%M")

