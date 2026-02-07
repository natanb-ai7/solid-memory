from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


@dataclass
class Program:
    make: str
    model: str
    model_year: int
    term_months: int
    mileage: int
    region: str
    effective_from: str
    effective_to: str
    program_name: Optional[str] = None
    apr: Optional[float] = None
    residual_value: Optional[float] = None
    notes: Optional[str] = None
    id: Optional[int] = None


class ProgramRepository:
    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def close(self) -> None:
        self.connection.close()

    def apply_migrations(self) -> None:
        """Apply all SQL migration files in order."""
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS schema_migrations (filename TEXT PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
        applied = {row[0] for row in cursor.execute("SELECT filename FROM schema_migrations")}

        migration_files: Iterable[Path] = sorted(MIGRATIONS_DIR.glob("*.sql"))
        for migration in migration_files:
            if migration.name in applied:
                continue
            with migration.open("r", encoding="utf-8") as handle:
                sql = handle.read()
                cursor.executescript(sql)
                cursor.execute(
                    "INSERT INTO schema_migrations (filename) VALUES (?)",
                    (migration.name,),
                )
        self.connection.commit()

    def upsert_program(self, program: Program) -> Program:
        """Insert or update a program keyed on the natural unique fields."""
        sql = (
            """
            INSERT INTO programs (
                make, model, model_year, term_months, mileage, region,
                effective_from, effective_to, program_name, apr, residual_value, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (make, model, model_year, term_months, mileage, region, effective_from, effective_to)
            DO UPDATE SET
                program_name=excluded.program_name,
                apr=excluded.apr,
                residual_value=excluded.residual_value,
                notes=excluded.notes,
                updated_at=CURRENT_TIMESTAMP
            RETURNING *
            """
        )
        cursor = self.connection.execute(
            sql,
            (
                program.make,
                program.model,
                program.model_year,
                program.term_months,
                program.mileage,
                program.region,
                program.effective_from,
                program.effective_to,
                program.program_name,
                program.apr,
                program.residual_value,
                program.notes,
            ),
        )
        row = cursor.fetchone()
        self.connection.commit()
        return self._row_to_program(row)

    def get_program(self, **filters: str | int) -> Optional[Program]:
        """Retrieve a single program by matching on provided filters."""
        if not filters:
            raise ValueError("At least one filter must be provided")

        clauses = []
        params: List[str | int] = []
        for key, value in filters.items():
            clauses.append(f"{key} = ?")
            params.append(value)

        sql = f"SELECT * FROM programs WHERE {' AND '.join(clauses)} LIMIT 1"
        cursor = self.connection.execute(sql, params)
        row = cursor.fetchone()
        return self._row_to_program(row) if row else None

    def list_programs(self) -> List[Program]:
        cursor = self.connection.execute("SELECT * FROM programs ORDER BY make, model, model_year")
        return [self._row_to_program(row) for row in cursor.fetchall()]

    @staticmethod
    def _row_to_program(row: sqlite3.Row) -> Program:
        return Program(
            id=row["id"],
            make=row["make"],
            model=row["model"],
            model_year=row["model_year"],
            term_months=row["term_months"],
            mileage=row["mileage"],
            region=row["region"],
            effective_from=row["effective_from"],
            effective_to=row["effective_to"],
            program_name=row["program_name"],
            apr=row["apr"],
            residual_value=row["residual_value"],
            notes=row["notes"],
        )
