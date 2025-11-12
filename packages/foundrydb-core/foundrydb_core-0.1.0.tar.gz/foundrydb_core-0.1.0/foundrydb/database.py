"""
Database module for FoundryDB.
Phase 1 - 2 stub: provides a minimal in-process database interface.
"""

from __future__ import annotations
from pathlib import Path
from foundrydb.storage import StorageEngine
from foundrydb.catalog import Catalog


class Database:
    """
    Represents a FoundryDB database instance.

    Responsibilities (current phase):
    - Manage file locations for the database
    - Initialize core subsystems (catalog, storage engine)
    - Provide a simple `.execute()` stub for later SQL expansion
    """

    def __init__(self, path: str | Path):
        """
        Create or open a database directory.
        :param path: Directory path for this database instance.
        """
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)

        # Core components
        self.catalog = Catalog(self.path / "catalog.meta")
        self.storage = StorageEngine(self.path)

        print(f"✅ FoundryDB initialized at {self.path}")

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def execute(self, sql: str):
        """
        Execute a SQL string.

        Phase 1–2: only parses simple INSERT or SELECT statements
        with crude string handling.
        """
        sql = sql.strip().rstrip(";").upper()
        if sql.startswith("INSERT"):
            # Example: INSERT INTO users VALUES {"id":1, "name":"Alice"}
            return self._handle_insert(sql)
        elif sql.startswith("SELECT"):
            return self._handle_select(sql)
        else:
            print(f"[WARN] Unrecognized SQL: {sql}")
            return []

    # ------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------
    def _handle_insert(self, sql: str):
        """
        Very naive insert handler:
        INSERT INTO users VALUES {"id":1, "name":"Alice"}
        """
        try:
            _, _, table_part, *rest = sql.split(maxsplit=3)
            table_name = table_part.lower()
            json_text = rest[-1].split("VALUES", 1)[-1].strip()
            # Strip enclosing braces if missing
            if not json_text.startswith("{"):
                print("⚠️  Expected JSON-style object after VALUES.")
                return []
            # Evaluate JSON safely
            import json

            row = json.loads(json_text.replace("'", '"'))
            self.storage.insert(table_name, row)
            print(f"Inserted row into '{table_name}': {row}")
        except Exception as e:
            print(f"[ERROR] Failed to insert: {e}")
        return []

    def _handle_select(self, sql: str):
        """
        Very naive SELECT handler:
        SELECT * FROM users
        """
        tokens = sql.split()
        try:
            from_index = tokens.index("FROM")
            table_name = tokens[from_index + 1].lower()
            rows = list(self.storage.scan(table_name))
            print(f"{len(rows)} rows selected from '{table_name}'")
            return rows
        except Exception as e:
            print(f"[ERROR] SELECT failed: {e}")
            return []
