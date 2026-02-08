from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from engine.db import get_connection, load_json


@dataclass
class ValidationResult:
    status: str
    errors: list[str]
    warnings: list[str]
    fixit: dict[str, Any]


def auditability_validator(asof_date: str, config: dict) -> ValidationResult:
    conn = get_connection()
    errors = []
    warnings = []
    fixit = {"missing_evidence": [], "market_context": []}

    min_cov = config["thresholds"]["min_evidence_coverage_pct"]
    scores = conn.execute("SELECT * FROM scoring WHERE asof_date = ?", (asof_date,)).fetchall()
    for row in scores:
        if row["evidence_coverage_pct"] < min_cov:
            errors.append(
                f"Target {row['target_id']} evidence coverage {row['evidence_coverage_pct']} < {min_cov}"
            )
            fixit["missing_evidence"].append(
                {
                    "target_id": row["target_id"],
                    "required_pct": min_cov,
                    "current_pct": row["evidence_coverage_pct"],
                }
            )

    market_row = conn.execute(
        "SELECT * FROM market_context WHERE asof_date = ?", (asof_date,)
    ).fetchone()
    if market_row:
        evidence_ids = load_json(market_row["evidence_ids"], [])
        for field in [
            "sofr_2y",
            "sofr_5y",
            "sofr_10y",
            "cmbx_level_proxy",
            "credit_spread_proxy",
            "funding_tightness_index",
        ]:
            if market_row[field] is not None and not evidence_ids:
                errors.append(f"Market context {field} missing evidence on {asof_date}")
                fixit["market_context"].append({"field": field, "asof_date": asof_date})
    else:
        warnings.append("Market context row missing.")

    conn.close()
    status = "pass" if not errors else "fail"
    return ValidationResult(status=status, errors=errors, warnings=warnings, fixit=fixit)


def calculation_validator(asof_date: str, config: dict) -> ValidationResult:
    conn = get_connection()
    errors = []
    warnings = []
    fixit = {"calculation": []}
    scores = conn.execute("SELECT * FROM scoring WHERE asof_date = ?", (asof_date,)).fetchall()
    for row in scores:
        tss = row["TSS"]
        if not 0 <= tss <= 10:
            errors.append(f"TSS out of bounds for {row['target_id']}")
        if any(row[field] < 0 or row[field] > 10 for field in ["FES", "LMS", "OS", "DMS", "OLS"]):
            errors.append(f"Bucket score out of bounds for {row['target_id']}")

        recomputed = round(
            row["FES"] * config["weights"]["TSS"]["FES"]
            + row["LMS"] * config["weights"]["TSS"]["LMS"]
            + row["OS"] * config["weights"]["TSS"]["OS"]
            + row["DMS"] * config["weights"]["TSS"]["DMS"]
            + row["OLS"] * config["weights"]["TSS"]["OLS"],
            2,
        )
        if abs(recomputed - row["TSS"]) > 0.01:
            errors.append(f"TSS mismatch for {row['target_id']}")

    weights = config["weights"]["TSS"]
    if any(weight < 0 for weight in weights.values()):
        errors.append("Negative TSS weight")
    if abs(sum(weights.values()) - 1) > 0.02:
        errors.append("TSS weights do not sum to 1")

    conn.close()
    status = "pass" if not errors else "fail"
    return ValidationResult(status=status, errors=errors, warnings=warnings, fixit=fixit)


def narrative_validator(asof_date: str) -> ValidationResult:
    conn = get_connection()
    errors = []
    warnings = []
    fixit = {"narrative": []}
    rows = conn.execute("SELECT * FROM scoring WHERE asof_date = ?", (asof_date,)).fetchall()
    for row in rows:
        top_levers = load_json(row["top_levers"], [])
        if not top_levers:
            warnings.append(f"No top levers for {row['target_id']}")
        for lever in top_levers:
            if "QUALITATIVE" not in lever and not any(char.isdigit() for char in lever):
                errors.append(f"Lever lacks metric for {row['target_id']}")

    conn.close()
    status = "pass" if not errors else "fail"
    return ValidationResult(status=status, errors=errors, warnings=warnings, fixit=fixit)


def run_validators(asof_date: str, config: dict) -> dict:
    audit = auditability_validator(asof_date, config)
    calc = calculation_validator(asof_date, config)
    narrative = narrative_validator(asof_date)
    return {
        "auditability": audit,
        "calculation": calc,
        "narrative": narrative,
    }
