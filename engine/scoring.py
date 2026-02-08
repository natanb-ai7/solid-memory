from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from statistics import mean
from typing import Any
from uuid import uuid4

import yaml

from engine.db import dump_json, get_connection, load_json


@dataclass
class ScoreResult:
    target_id: str
    asof_date: str
    FES: float
    LMS: float
    OS: float
    DMS: float
    OLS: float
    TSS: float
    drift_5d: float
    drift_20d: float
    evidence_coverage_pct: float
    score_confidence_pct: float
    top_levers: list[str]
    top_risks: list[str]
    next_best_actions: list[dict[str, Any]]
    bucket_coverage: dict[str, float]
    bucket_confidence: dict[str, float]
    data_freshness_days: int


def load_config(config_path: str = "engine/config/defaults.yaml") -> dict:
    with open(config_path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _weighted_score(values: dict[str, float], weights: dict[str, float]) -> float:
    return round(sum(values[key] * weights[key] for key in weights), 2)


def _evidence_coverage(subscores: dict[str, float], evidence_ids: list[str], evidence_map: dict) -> float:
    covered = 0
    total = len(subscores)
    for _key in subscores:
        if any(evidence_map.get(eid, 0) >= 0.6 for eid in evidence_ids):
            covered += 1
    return round(100 * covered / total, 2) if total else 0


def _freshness_days(conn, asof_date: str) -> int:
    cursor = conn.execute(
        "SELECT MAX(asof_date) as latest FROM market_context WHERE asof_date <= ?",
        (asof_date,),
    )
    row = cursor.fetchone()
    if not row or not row["latest"]:
        return 999
    latest = datetime.fromisoformat(row["latest"]).date()
    return (datetime.fromisoformat(asof_date).date() - latest).days


def compute_scores(asof_date: str, config: dict) -> list[ScoreResult]:
    conn = get_connection()
    cursor = conn.execute("SELECT * FROM targets")
    targets = cursor.fetchall()
    evidence_cursor = conn.execute("SELECT evidence_id, confidence FROM evidence")
    evidence_map = {row["evidence_id"]: row["confidence"] for row in evidence_cursor}

    results = []
    for target in targets:
        subscore_row = conn.execute(
            "SELECT * FROM subscores WHERE target_id = ? AND asof_date = ?",
            (target["target_id"], asof_date),
        ).fetchone()
        if not subscore_row:
            continue

        subscores = dict(subscore_row)
        evidence_ids = load_json(subscores.get("evidence_ids"), [])
        fes_values = {
            "counterparty_access": subscores["counterparty_access"],
            "collateral_eligibility_lift": subscores["collateral_eligibility_lift"],
            "haircut_or_term_benefit": subscores["haircut_or_term_benefit"],
        }
        lms_values = {
            "surveillance_delta": subscores["surveillance_delta"],
            "workout_edge": subscores["workout_edge"],
            "early_warning_coverage": subscores["early_warning_coverage"],
        }
        os_values = {
            "channel_scale": subscores["channel_scale"],
            "borrower_overlap": subscores["borrower_overlap"],
            "speed_to_close": subscores["speed_to_close"],
        }
        dms_values = {
            "uniqueness": subscores["uniqueness"],
            "integration_readiness": subscores["integration_readiness"],
            "contracts_durability": subscores["contracts_durability"],
        }
        ols_values = {
            "cost_takeout_feasibility": subscores["cost_takeout_feasibility"],
            "process_redundancy": subscores["process_redundancy"],
        }

        fes = _weighted_score(fes_values, config["weights"]["FES"])
        lms = _weighted_score(lms_values, config["weights"]["LMS"])
        os_score = _weighted_score(os_values, config["weights"]["OS"])
        dms = _weighted_score(dms_values, config["weights"]["DMS"])
        ols = _weighted_score(ols_values, config["weights"]["OLS"])

        tss = round(
            fes * config["weights"]["TSS"]["FES"]
            + lms * config["weights"]["TSS"]["LMS"]
            + os_score * config["weights"]["TSS"]["OS"]
            + dms * config["weights"]["TSS"]["DMS"]
            + ols * config["weights"]["TSS"]["OLS"],
            2,
        )

        history_rows = conn.execute(
            "SELECT TSS FROM scoring WHERE target_id = ? AND asof_date < ? ORDER BY asof_date DESC",
            (target["target_id"], asof_date),
        ).fetchall()
        history = [row["TSS"] for row in history_rows]
        avg_5 = mean(history[:5]) if history[:5] else tss
        avg_20 = mean(history[:20]) if history[:20] else tss
        drift_5d = round(tss - avg_5, 2)
        drift_20d = round(tss - avg_20, 2)

        bucket_coverage = {
            "FES": _evidence_coverage(fes_values, evidence_ids, evidence_map),
            "LMS": _evidence_coverage(lms_values, evidence_ids, evidence_map),
            "OS": _evidence_coverage(os_values, evidence_ids, evidence_map),
            "DMS": _evidence_coverage(dms_values, evidence_ids, evidence_map),
            "OLS": _evidence_coverage(ols_values, evidence_ids, evidence_map),
        }
        evidence_coverage_pct = round(mean(bucket_coverage.values()), 2)

        freshness_days = _freshness_days(conn, asof_date)
        freshness_full = config["rules"]["freshness_full_days"]
        freshness_max = config["rules"]["freshness_max_days"]
        if freshness_days <= freshness_full:
            freshness_score = 100
        elif freshness_days >= freshness_max:
            freshness_score = 0
        else:
            freshness_score = round(
                100 * (1 - (freshness_days - freshness_full) / (freshness_max - freshness_full)),
                2,
            )

        score_confidence_pct = round(0.7 * evidence_coverage_pct + 0.3 * freshness_score, 2)
        bucket_confidence = {
            bucket: round(0.7 * coverage + 0.3 * freshness_score, 2)
            for bucket, coverage in bucket_coverage.items()
        }

        results.append(
            ScoreResult(
                target_id=target["target_id"],
                asof_date=asof_date,
                FES=fes,
                LMS=lms,
                OS=os_score,
                DMS=dms,
                OLS=ols,
                TSS=tss,
                drift_5d=drift_5d,
                drift_20d=drift_20d,
                evidence_coverage_pct=evidence_coverage_pct,
                score_confidence_pct=score_confidence_pct,
                top_levers=[],
                top_risks=[],
                next_best_actions=[],
                bucket_coverage=bucket_coverage,
                bucket_confidence=bucket_confidence,
                data_freshness_days=freshness_days,
            )
        )

    conn.close()
    return results


def persist_scores(scores: list[ScoreResult]) -> None:
    conn = get_connection()
    for score in scores:
        conn.execute(
            """
            INSERT OR REPLACE INTO scoring VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                score.target_id,
                score.asof_date,
                score.FES,
                score.LMS,
                score.OS,
                score.DMS,
                score.OLS,
                score.TSS,
                score.drift_5d,
                score.drift_20d,
                score.evidence_coverage_pct,
                score.score_confidence_pct,
                dump_json(score.top_levers),
                dump_json(score.top_risks),
                dump_json(score.next_best_actions),
                dump_json(score.bucket_coverage),
                dump_json(score.bucket_confidence),
                score.data_freshness_days,
            ),
        )
    conn.commit()
    conn.close()


def update_run_history(asof_date: str, status: str, notes: str = "") -> str:
    conn = get_connection()
    run_id = str(uuid4())
    conn.execute(
        "INSERT OR REPLACE INTO run_history VALUES (?, ?, ?, ?, ?)",
        (run_id, asof_date, status, datetime.utcnow().isoformat(), notes),
    )
    conn.commit()
    conn.close()
    return run_id
