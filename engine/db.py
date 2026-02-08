from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("SYNERGY_DB_PATH", "data/synergy.db"))


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS targets (
            target_id TEXT PRIMARY KEY,
            legal_name TEXT,
            common_name TEXT,
            segment TEXT,
            geography_footprint TEXT,
            key_products TEXT,
            key_customers_public TEXT,
            ownership_status TEXT,
            website_url TEXT,
            last_touch_date TEXT,
            owner TEXT,
            status TEXT,
            integration_complexity INTEGER,
            strategic_fit_notes TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id TEXT PRIMARY KEY,
            target_id TEXT,
            asof_date TEXT,
            evidence_type TEXT,
            source_url TEXT,
            file_ref TEXT,
            title TEXT,
            excerpt TEXT,
            tags TEXT,
            confidence REAL,
            created_by TEXT,
            created_at TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS signals (
            signal_id TEXT PRIMARY KEY,
            target_id TEXT,
            asof_date TEXT,
            hiring_change_30d REAL,
            news_event_score REAL,
            capital_event_flag INTEGER,
            partnership_signal_score REAL,
            exec_departure_flag INTEGER,
            customer_concentration_pct REAL,
            banker_hired_flag INTEGER,
            litigation_flag INTEGER,
            notes TEXT,
            evidence_ids TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS market_context (
            asof_date TEXT PRIMARY KEY,
            rates_context TEXT,
            sofr_2y REAL,
            sofr_5y REAL,
            sofr_10y REAL,
            cmbx_level_proxy REAL,
            credit_spread_proxy REAL,
            funding_tightness_index REAL,
            evidence_ids TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subscores (
            subscore_id TEXT PRIMARY KEY,
            target_id TEXT,
            asof_date TEXT,
            counterparty_access REAL,
            collateral_eligibility_lift REAL,
            haircut_or_term_benefit REAL,
            surveillance_delta REAL,
            workout_edge REAL,
            early_warning_coverage REAL,
            channel_scale REAL,
            borrower_overlap REAL,
            speed_to_close REAL,
            uniqueness REAL,
            integration_readiness REAL,
            contracts_durability REAL,
            cost_takeout_feasibility REAL,
            process_redundancy REAL,
            evidence_ids TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scoring (
            target_id TEXT,
            asof_date TEXT,
            FES REAL,
            LMS REAL,
            OS REAL,
            DMS REAL,
            OLS REAL,
            TSS REAL,
            drift_5d REAL,
            drift_20d REAL,
            evidence_coverage_pct REAL,
            score_confidence_pct REAL,
            top_levers TEXT,
            top_risks TEXT,
            next_best_actions TEXT,
            bucket_coverage TEXT,
            bucket_confidence TEXT,
            data_freshness_days INTEGER,
            PRIMARY KEY (target_id, asof_date)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS action_log (
            action_id TEXT PRIMARY KEY,
            target_id TEXT,
            asof_date TEXT,
            action_type TEXT,
            action_owner TEXT,
            action_notes TEXT,
            outcome_tag TEXT,
            next_followup_date TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS run_history (
            run_id TEXT PRIMARY KEY,
            asof_date TEXT,
            status TEXT,
            created_at TEXT,
            notes TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def dump_json(value) -> str:
    return json.dumps(value)


def load_json(value: str | None, default):
    if not value:
        return default
    return json.loads(value)
