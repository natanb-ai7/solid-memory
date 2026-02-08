from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from engine.db import dump_json, get_connection, load_json
from engine.rules import next_best_actions
from engine.scoring import ScoreResult, compute_scores, load_config, persist_scores, update_run_history
from engine.validators import run_validators


SUBSCORE_LABELS = {
    "counterparty_access": "Counterparty access",
    "collateral_eligibility_lift": "Collateral eligibility lift",
    "haircut_or_term_benefit": "Haircut/term benefit",
    "surveillance_delta": "Surveillance delta",
    "workout_edge": "Workout edge",
    "early_warning_coverage": "Early warning coverage",
    "channel_scale": "Channel scale",
    "borrower_overlap": "Borrower overlap",
    "speed_to_close": "Speed to close",
    "uniqueness": "Data uniqueness",
    "integration_readiness": "Integration readiness",
    "contracts_durability": "Contracts durability",
    "cost_takeout_feasibility": "Cost takeout feasibility",
    "process_redundancy": "Process redundancy",
}


def _top_levers(subscores: dict, count: int = 3) -> list[str]:
    items = sorted(
        [(key, value) for key, value in subscores.items() if key in SUBSCORE_LABELS],
        key=lambda item: item[1],
        reverse=True,
    )
    return [f"{SUBSCORE_LABELS[key]} at {value:.1f} (QUALITATIVE)" for key, value in items[:count]]


def _top_risks(subscores: dict, count: int = 3) -> list[str]:
    items = sorted(
        [(key, value) for key, value in subscores.items() if key in SUBSCORE_LABELS],
        key=lambda item: item[1],
    )
    return [f"{SUBSCORE_LABELS[key]} at {value:.1f} (QUALITATIVE)" for key, value in items[:count]]


def run_daily(asof_date: str) -> dict:
    config = load_config()
    scores = compute_scores(asof_date, config)

    conn = get_connection()
    enriched_scores: list[ScoreResult] = []
    for score in scores:
        subscore_row = conn.execute(
            "SELECT * FROM subscores WHERE target_id = ? AND asof_date = ?",
            (score.target_id, asof_date),
        ).fetchone()
        subscores = dict(subscore_row) if subscore_row else {}
        top_levers = _top_levers(subscores)
        top_risks = _top_risks(subscores)
        score_row = {
            "target_id": score.target_id,
            "asof_date": score.asof_date,
            "FES": score.FES,
            "LMS": score.LMS,
            "OS": score.OS,
            "DMS": score.DMS,
            "OLS": score.OLS,
            "TSS": score.TSS,
            "drift_5d": score.drift_5d,
            "score_confidence_pct": score.score_confidence_pct,
        }
        actions = next_best_actions(score_row, config)

        enriched_scores.append(
            ScoreResult(
                **{
                    **score.__dict__,
                    "top_levers": top_levers,
                    "top_risks": top_risks,
                    "next_best_actions": actions,
                }
            )
        )

    persist_scores(enriched_scores)

    validator_results = run_validators(asof_date, config)
    status = (
        "pass"
        if all(result.status == "pass" for result in validator_results.values())
        else "fail"
    )
    if status == "fail":
        fixit = {
            key: {
                "errors": result.errors,
                "warnings": result.warnings,
                "fixit": result.fixit,
            }
            for key, result in validator_results.items()
        }
        Path("outputs").mkdir(parents=True, exist_ok=True)
        Path(f"outputs/fixit_{asof_date}.json").write_text(
            json.dumps(fixit, indent=2), encoding="utf-8"
        )
    run_id = update_run_history(asof_date, status)

    conn.close()
    return {
        "run_id": run_id,
        "status": status,
        "validators": validator_results,
    }
