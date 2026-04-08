import logging
from pathlib import Path

from app.config import settings
from app.models.schemas import LogEntryResponse

logger = logging.getLogger(__name__)


class LogService:
    def __init__(self):
        self.log_dir = Path(settings.diretorio_logs)

    def get_logs(self, level: str | None = None, limit: int = 100) -> list[LogEntryResponse]:
        # TODO: implementar leitura de arquivos de log
        return []
