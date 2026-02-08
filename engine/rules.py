from __future__ import annotations

from datetime import datetime, timedelta
from statistics import mean

from engine.db import get_connection, load_json


def _fti_zscore(conn, asof_date: str) -> float | None:
    rows = conn.execute(
        "SELECT funding_tightness_index FROM market_context WHERE asof_date <= ? ORDER BY asof_date DESC LIMIT 20",
        (asof_date,),
    ).fetchall()
    values = [row["funding_tightness_index"] for row in rows if row["funding_tightness_index"] is not None]
    if len(values) < 3:
        return None
    avg = mean(values)
    variance = mean([(value - avg) ** 2 for value in values])
    std = variance**0.5
    if std == 0:
        return 0.0
    return (values[0] - avg) / std


def next_best_actions(score_row, config: dict) -> list[dict]:
    conn = get_connection()
    target_id = score_row["target_id"]
    asof_date = score_row["asof_date"]
    signal_row = conn.execute(
        "SELECT * FROM signals WHERE target_id = ? AND asof_date = ?",
        (target_id, asof_date),
    ).fetchone()
    target_row = conn.execute("SELECT * FROM targets WHERE target_id = ?", (target_id,)).fetchone()

    actions = []

    if (
        score_row["TSS"] >= config["thresholds"]["accelerate_tss"]
        and score_row["drift_5d"] >= config["thresholds"]["accelerate_drift_5d"]
        and score_row["score_confidence_pct"] >= config["thresholds"]["accelerate_confidence_pct"]
    ):
        actions.extend(
            [
                "Schedule principal call within 72h",
                "Request data room lite: customer list, KPIs, top contracts",
                "Draft IC mini-memo (1 page)",
            ]
        )

    fti_z = _fti_zscore(conn, asof_date)
    if fti_z is not None and (
        fti_z > config["rules"]["structure_reprice_fti_z"]
        and score_row["FES"] < config["rules"]["structure_reprice_fes"]
    ):
        actions.extend(
            [
                "Consider structure with earnout / seller note",
                "Delay signing until funding window improves",
                "Run downside synergy scenario",
            ]
        )

    if (
        score_row["TSS"] <= config["thresholds"]["deprioritize_tss"]
        or score_row["drift_5d"] <= config["thresholds"]["deprioritize_drift_5d"]
        or score_row["score_confidence_pct"] < config["thresholds"]["min_confidence_pct"]
    ):
        actions.extend(
            [
                "Pause outreach; set reminder in 14 days",
                "Identify 2 missing evidence items that would change the view",
            ]
        )

    if signal_row is not None:
        complexity = target_row["integration_complexity"] if target_row else 1
        if (signal_row["exec_departure_flag"] and complexity >= config["rules"]["risk_review_complexity"]) or (
            signal_row["litigation_flag"]
        ):
            actions.extend(
                [
                    "Legal diligence screen",
                    "Integration plan stress test",
                    "Reference call set (2 customers, 1 former employee)",
                ]
            )

    conn.close()
    due_date = (datetime.fromisoformat(asof_date) + timedelta(days=3)).date().isoformat()
    owner = target_row["owner"] if target_row else "Unassigned"
    return [
        {"action": action, "owner": owner, "due_date": due_date} for action in dict.fromkeys(actions)
    ]
