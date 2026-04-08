from datetime import datetime

import pytz

from app.config import settings


def now_brasilia() -> datetime:
    tz = pytz.timezone(settings.fuso_horario)
    return datetime.now(tz)


def is_madrugada() -> bool:
    hour = now_brasilia().hour
    return 0 <= hour < 6
