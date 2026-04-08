import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_DIR = Path("./data")
DB_NAME = "transparencia.db"


class SqliteWriter:
    def __init__(self):
        self._db_path = DB_DIR / DB_NAME
        self._conn: sqlite3.Connection | None = None

    def _close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
        return self._conn

    def _ensure_table(self, table_name: str, columns: list[str]):
        conn = self._get_conn()
        cols_def = ", ".join(f'"{col}" TEXT' for col in columns)
        conn.execute(
            f'CREATE TABLE IF NOT EXISTS "{table_name}" ('
            f"id INTEGER PRIMARY KEY AUTOINCREMENT, "
            f"{cols_def}, "
            f"_ano INTEGER, _mes INTEGER, _pagina INTEGER, "
            f"_importado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            f")"
        )
        conn.execute(
            f'CREATE INDEX IF NOT EXISTS "idx_{table_name}_ano_mes" '
            f'ON "{table_name}" (_ano, _mes)'
        )
        conn.commit()

    def write(self, data: list[dict], endpoint: str, ano: int, mes: int, pagina: int = 0):
        if not data:
            return

        table_name = endpoint
        columns = list(data[0].keys())

        self._ensure_table(table_name, columns)

        conn = self._get_conn()
        placeholders = ", ".join(["?"] * (len(columns) + 3))
        col_names = ", ".join(f'"{c}"' for c in columns)
        col_names += ", _ano, _mes, _pagina"

        sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders})'

        rows = []
        for row in data:
            values = [row.get(col, "") for col in columns]
            values.extend([ano, mes, pagina])
            rows.append(values)

        conn.executemany(sql, rows)
        conn.commit()
        logger.info(
            "SQLite: %d registros inseridos em '%s' (ano=%d, mes=%02d)",
            len(data), table_name, ano, mes,
        )

    @property
    def db_path(self) -> str:
        return str(self._db_path)

    def close(self):
        self._close()
