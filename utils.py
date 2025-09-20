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
    import re
    import zoneinfo

    text = text.strip().lower()
    now = datetime.now(timezone.utc)

    # Обработка относительного времени
    if "через" in text:
        # Паттерны для парсинга относительного времени
        patterns = [
            (r'через\s+(\d+)\s+секунд[уы]?', lambda m: timedelta(seconds=int(m.group(1)))),
            (r'через\s+(\d+)\s+минут[уы]?', lambda m: timedelta(minutes=int(m.group(1)))),
            (r'через\s+(\d+)\s+час[а]?[ов]?', lambda m: timedelta(hours=int(m.group(1)))),
            (r'через\s+(\d+)\s+дн[ейя]', lambda m: timedelta(days=int(m.group(1)))),
        ]

        for pattern, delta_func in patterns:
            match = re.search(pattern, text)
            if match:
                delta = delta_func(match)
                result_time = now + delta
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"PARSE_TIME: Текст='{text}', Паттерн='{pattern}', Найдено='{match.group()}', Дельта={delta}, Результат={result_time}")
                return result_time

        # Если ни один паттерн не сработал
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"PARSE_TIME: Не найден паттерн для текста '{text}'")

    # Если не относительное время, используем стандартный парсер
    try:
        dt = parser.parse(text, fuzzy=True)
        # если dt наивный, предположим таймзону пользователя (или DEFAULT_TZ)
        if dt.tzinfo is None:
            tz_name = user_tz or DEFAULT_TZ
            tz = zoneinfo.ZoneInfo(tz_name)
            dt = dt.replace(tzinfo=tz)
        # привести к UTC
        return dt.astimezone(timezone.utc)
    except:
        # Если ничего не получилось, возвращаем время через 1 минуту
        return now + timedelta(minutes=1)

def format_local(dt_utc: datetime, tz_name: str) -> str:
    import zoneinfo
    local = dt_utc.astimezone(zoneinfo.ZoneInfo(tz_name))
    return local.strftime("%Y-%m-%d %H:%M")

