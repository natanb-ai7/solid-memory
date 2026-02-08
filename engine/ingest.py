from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

from engine.db import dump_json, get_connection, init_db


def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]


def _read_xlsx(path: Path, sheet: str) -> list[dict]:
    frame = pd.read_excel(path, sheet_name=sheet)
    return frame.to_dict(orient="records")


def _as_bool(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def _as_float(value):
    if value is None or value == "":
        return None
    return float(value)


def _as_list(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    return [item.strip() for item in str(value).split("|") if item.strip()]


def _ensure_iso_date(value: str | None) -> str | None:
    if not value:
        return None
    return datetime.fromisoformat(str(value)).date().isoformat()


def ingest_directory(path: Path) -> None:
    init_db()
    for file in path.iterdir():
        if file.suffix.lower() in {".csv", ".xlsx"}:
            ingest_file(file)


def ingest_file(path: Path) -> None:
    init_db()
    suffix = path.suffix.lower()
    if suffix == ".csv":
        rows = _read_csv(path)
        name = path.stem
        _insert_rows(name, rows)
    elif suffix == ".xlsx":
        workbook = pd.ExcelFile(path)
        for sheet in workbook.sheet_names:
            rows = _read_xlsx(path, sheet)
            _insert_rows(sheet.lower(), rows)


def _insert_rows(entity: str, rows: Iterable[dict]) -> None:
    conn = get_connection()
    cursor = conn.cursor()

    if entity == "targets":
        for row in rows:
            cursor.execute(
                """
                INSERT OR REPLACE INTO targets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["target_id"],
                    row["legal_name"],
                    row["common_name"],
                    row["segment"],
                    row.get("geography_footprint", ""),
                    row.get("key_products", ""),
                    row.get("key_customers_public", ""),
                    row.get("ownership_status", "unknown"),
                    row.get("website_url"),
                    _ensure_iso_date(row.get("last_touch_date")),
                    row.get("owner", ""),
                    row.get("status", ""),
                    int(row.get("integration_complexity", 3)),
                    row.get("strategic_fit_notes", ""),
                ),
            )
    elif entity == "evidence":
        for row in rows:
            cursor.execute(
                """
                INSERT OR REPLACE INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["evidence_id"],
                    row["target_id"],
                    _ensure_iso_date(row["asof_date"]),
                    row["evidence_type"],
                    row.get("source_url"),
                    row.get("file_ref"),
                    row["title"],
                    row["excerpt"],
                    dump_json(_as_list(row.get("tags"))),
                    float(row["confidence"]),
                    row["created_by"],
                    row.get("created_at") or datetime.utcnow().isoformat(),
                ),
            )
    elif entity == "signals":
        for row in rows:
            cursor.execute(
                """
                INSERT OR REPLACE INTO signals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["signal_id"],
                    row["target_id"],
                    _ensure_iso_date(row["asof_date"]),
                    _as_float(row.get("hiring_change_30d")),
                    _as_float(row.get("news_event_score")),
                    _as_bool(row.get("capital_event_flag")),
                    _as_float(row.get("partnership_signal_score")),
                    _as_bool(row.get("exec_departure_flag")),
                    _as_float(row.get("customer_concentration_pct")),
                    _as_bool(row.get("banker_hired_flag")),
                    _as_bool(row.get("litigation_flag")),
                    row.get("notes", ""),
                    dump_json(_as_list(row.get("evidence_ids"))),
                ),
            )
    elif entity == "market_context":
        for row in rows:
            cursor.execute(
                """
                INSERT OR REPLACE INTO market_context VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    _ensure_iso_date(row["asof_date"]),
                    row.get("rates_context", ""),
                    _as_float(row.get("sofr_2y")),
                    _as_float(row.get("sofr_5y")),
                    _as_float(row.get("sofr_10y")),
                    _as_float(row.get("cmbx_level_proxy")),
                    _as_float(row.get("credit_spread_proxy")),
                    _as_float(row.get("funding_tightness_index")),
                    dump_json(_as_list(row.get("evidence_ids"))),
                ),
            )
    elif entity == "subscores":
        for row in rows:
            cursor.execute(
                """
                INSERT OR REPLACE INTO subscores VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["subscore_id"],
                    row["target_id"],
                    _ensure_iso_date(row["asof_date"]),
                    float(row["counterparty_access"]),
                    float(row["collateral_eligibility_lift"]),
                    float(row["haircut_or_term_benefit"]),
                    float(row["surveillance_delta"]),
                    float(row["workout_edge"]),
                    float(row["early_warning_coverage"]),
                    float(row["channel_scale"]),
                    float(row["borrower_overlap"]),
                    float(row["speed_to_close"]),
                    float(row["uniqueness"]),
                    float(row["integration_readiness"]),
                    float(row["contracts_durability"]),
                    float(row["cost_takeout_feasibility"]),
                    float(row["process_redundancy"]),
                    dump_json(_as_list(row.get("evidence_ids"))),
                ),
            )
    elif entity == "action_log":
        for row in rows:
            cursor.execute(
                """
                INSERT OR REPLACE INTO action_log VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["action_id"],
                    row["target_id"],
                    _ensure_iso_date(row["asof_date"]),
                    row["action_type"],
                    row["action_owner"],
                    row.get("action_notes", ""),
                    row.get("outcome_tag", "unknown"),
                    _ensure_iso_date(row.get("next_followup_date")),
                ),
            )

    conn.commit()
    conn.close()
