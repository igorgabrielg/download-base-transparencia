import logging
from pathlib import Path

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)


class CsvWriter:
    def __init__(self):
        self.output_dir = Path(settings.diretorio_saida)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def set_output_dir(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write(self, data: list[dict], endpoint: str, ano: int, mes: int):
        if not data:
            return

        filename = f"{endpoint}_{ano}_{mes:02d}.csv"
        filepath = self.output_dir / filename

        df = pd.DataFrame(data)

        if filepath.exists():
            df.to_csv(filepath, mode="a", header=False, index=False)
        else:
            df.to_csv(filepath, index=False)

        logger.info("Escritos %d registros em %s", len(data), filename)
