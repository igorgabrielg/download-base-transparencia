import json
import logging
from pathlib import Path

from app.config import settings
from app.models.checkpoint import Checkpoint

logger = logging.getLogger(__name__)

CHECKPOINT_FILE = Path(settings.diretorio_saida) / "checkpoints.json"


class CheckpointService:
    def save(self, checkpoint: Checkpoint):
        checkpoints = self.load_all()
        key = f"{checkpoint.endpoint.value}_{checkpoint.ano}_{checkpoint.mes}"
        checkpoints[key] = checkpoint.model_dump(mode="json")
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHECKPOINT_FILE.write_text(json.dumps(checkpoints, indent=2, default=str))
        logger.info("Checkpoint salvo: %s", key)

    def load_all(self) -> dict:
        if not CHECKPOINT_FILE.exists():
            return {}
        return json.loads(CHECKPOINT_FILE.read_text())

    def get_last(self, endpoint: str, ano: int, mes: int) -> Checkpoint | None:
        checkpoints = self.load_all()
        key = f"{endpoint}_{ano}_{mes}"
        data = checkpoints.get(key)
        if data:
            return Checkpoint(**data)
        return None
