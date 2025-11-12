from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Generator, Any


class StorageEngine:
    """
    Minimal storage engine.
    Each table is a .tbl file in the database directory.
    Rows are stored as JSON lines.
    """

    def __init__(self, base_path: str | Path):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------

    def _table_path(self, table_name: str) -> Path:
        """Return the filesystem path for a table."""
        return self.base_path / f"{table_name}.tbl"

    def insert(self, table_name: str, row: Dict[str, Any]) -> None:
        """
        Append a row (dict) to a table file.
        Creates the table file if it does not exist.
        """
        path = self._table_path(table_name)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    def scan(self, table_name: str) -> Generator[Dict[str, Any], None, None]:
        """
        Yield all rows from a table sequentially.
        If table does not exist, yield nothing.
        """
        path = self._table_path(table_name)
        if not path.exists():
            return
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    # stop reading on corrupt line
                    break
