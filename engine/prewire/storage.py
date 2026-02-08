from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Dict


class RunStorage:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS run_history (
                    run_id TEXT PRIMARY KEY,
                    run_date TEXT,
                    status TEXT,
                    output_path TEXT
                )
                """
            )

    def log_run(self, run_id: str, run_date: str, status: str, output_path: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO run_history VALUES (?, ?, ?, ?)",
                (run_id, run_date, status, output_path),
            )

    def list_runs(self) -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT run_id, run_date, status, output_path FROM run_history")
            return [
                {
                    "run_id": row[0],
                    "run_date": row[1],
                    "status": row[2],
                    "output_path": row[3],
                }
                for row in cursor.fetchall()
            ]
