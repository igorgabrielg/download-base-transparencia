import asyncio
import logging
import time
from datetime import datetime

import pytz

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self):
        self.tz = pytz.timezone(settings.fuso_horario)
        self._window_start: float = time.time()
        self._request_count: int = 0
        self._velocidade: int = settings.velocidade_req_min
        self._last_request_time: float = 0.0

    def get_current_limit(self) -> int:
        now = datetime.now(self.tz)
        hour = now.hour
        if 0 <= hour < 6:
            return settings.max_req_madrugada
        return settings.max_req_dia

    def reload_config(self, velocidade: int):
        self._velocidade = velocidade

    def _reset_window_if_needed(self):
        elapsed = time.time() - self._window_start
        if elapsed >= 60:
            self._request_count = 0
            self._window_start = time.time()

    def record_request(self):
        self._reset_window_if_needed()
        self._request_count += 1
        self._last_request_time = time.time()

    @property
    def requests_in_window(self) -> int:
        self._reset_window_if_needed()
        return self._request_count

    @property
    def seconds_until_reset(self) -> float:
        elapsed = time.time() - self._window_start
        return max(0, 60 - elapsed)

    async def wait_if_needed(self):
        self._reset_window_if_needed()

        # Throttle: espaco entre requisicoes baseado na velocidade configurada
        if self._velocidade > 0 and self._last_request_time > 0:
            interval = 60.0 / self._velocidade
            elapsed_since_last = time.time() - self._last_request_time
            if elapsed_since_last < interval:
                wait = interval - elapsed_since_last
                await asyncio.sleep(wait)

        # Limite do periodo (dia/noite): aguarda reset da janela se atingiu
        limite = self.get_current_limit()
        if self._request_count >= limite:
            wait_time = self.seconds_until_reset
            if wait_time > 0:
                logger.info(
                    "Rate limit do periodo atingido (%d/%d). Aguardando %.1fs...",
                    self._request_count,
                    limite,
                    wait_time,
                )
                await asyncio.sleep(wait_time)
                self._request_count = 0
                self._window_start = time.time()
