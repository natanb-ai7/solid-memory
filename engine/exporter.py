from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from engine.db import get_connection, load_json
from engine.validators import run_validators
from engine.scoring import load_config

TEMPLATE_DIR = Path("app/templates")
OUTPUT_DIR = Path("outputs")


def _env() -> Environment:
    return Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)


def _audit_state(asof_date: str) -> dict:
    config = load_config()
    validators = run_validators(asof_date, config)
    status = (
        "FINAL"
        if all(result.status == "pass" for result in validators.values())
        else "DRAFT"
    )
    return {"status": status, "validators": validators}


def _change_summary(conn, target_id: str, asof_date: str) -> list[str]:
    current = conn.execute(
        "SELECT * FROM scoring WHERE target_id = ? AND asof_date = ?",
        (target_id, asof_date),
    ).fetchone()
    prev = conn.execute(
        "SELECT * FROM scoring WHERE target_id = ? AND asof_date < ? ORDER BY asof_date DESC LIMIT 1",
        (target_id, asof_date),
    ).fetchone()
    if not current or not prev:
        return ["No prior score to compare."]

    changes = []
    for bucket in ["FES", "LMS", "OS", "DMS", "OLS"]:
        delta = round(current[bucket] - prev[bucket], 2)
        if abs(delta) >= 0.5:
            changes.append(f"{bucket} changed by {delta:+.2f} vs yesterday")

    signals = conn.execute(
        "SELECT * FROM signals WHERE target_id = ? AND asof_date = ?",
        (target_id, asof_date),
    ).fetchone()
    if signals:
        for flag in ["exec_departure_flag", "banker_hired_flag", "capital_event_flag", "litigation_flag"]:
            if signals[flag]:
                changes.append(f"New signal flag: {flag.replace('_', ' ')}")

    market = conn.execute("SELECT * FROM market_context WHERE asof_date = ?", (asof_date,)).fetchone()
    if market and market["funding_tightness_index"] is not None:
        changes.append("Market FTI provided for today")

    return changes if changes else ["No material changes detected."]


def _redact_target(target_row, target_id: str):
    if not target_row:
        return target_row
    payload = dict(target_row)
    payload["legal_name"] = f"REDACTED TARGET {target_id}"
    payload["common_name"] = f"REDACTED TARGET {target_id}"
    payload["strategic_fit_notes"] = "REDACTED"
    return payload


def _run_id(conn, asof_date: str) -> str:
    row = conn.execute(
        "SELECT run_id FROM run_history WHERE asof_date = ? ORDER BY created_at DESC LIMIT 1",
        (asof_date,),
    ).fetchone()
    return row["run_id"] if row else "N/A"


def export_target_scorecard(
    asof_date: str, target_id: str, fmt: str = "html", final: bool = True, redact: bool = False
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    score = conn.execute(
        "SELECT * FROM scoring WHERE target_id = ? AND asof_date = ?",
        (target_id, asof_date),
    ).fetchone()
    target = conn.execute("SELECT * FROM targets WHERE target_id = ?", (target_id,)).fetchone()
    evidence = conn.execute("SELECT * FROM evidence WHERE target_id = ?", (target_id,)).fetchall()

    audit = _audit_state(asof_date)
    if final and audit["status"] == "DRAFT":
        conn.close()
        raise RuntimeError("Auditability checks failed. Export blocked.")

    score_dict = dict(score)
    score_dict["top_levers"] = load_json(score_dict.get("top_levers"), [])
    score_dict["top_risks"] = load_json(score_dict.get("top_risks"), [])
    score_dict["next_best_actions"] = load_json(score_dict.get("next_best_actions"), [])
    score_dict["bucket_coverage"] = load_json(score_dict.get("bucket_coverage"), {})
    score_dict["bucket_confidence"] = load_json(score_dict.get("bucket_confidence"), {})
    change_summary = _change_summary(conn, target_id, asof_date)
    run_id = _run_id(conn, asof_date)
    conn.close()

    target_payload = _redact_target(target, target_id) if redact else target

    env = _env()
    template = env.get_template("scorecard.html")
    rendered = template.render(
        target=target_payload,
        score=score_dict,
        evidence=evidence,
        audit_state=audit["status"],
        run_id=run_id,
        generated_at=datetime.utcnow().isoformat(),
        change_summary=change_summary,
    )

    html_path = OUTPUT_DIR / f"scorecard_{target_id}_{asof_date}.html"
    html_path.write_text(rendered, encoding="utf-8")
    if fmt == "html":
        return html_path

    pdf_path = OUTPUT_DIR / f"scorecard_{target_id}_{asof_date}.pdf"
    HTML(string=rendered).write_pdf(pdf_path)
    return pdf_path


def export_daily_brief(
    asof_date: str, fmt: str = "html", final: bool = True, redact: bool = False
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    audit = _audit_state(asof_date)
    if final and audit["status"] == "DRAFT":
        raise RuntimeError("Auditability checks failed. Export blocked.")

    conn = get_connection()
    scores = conn.execute(
        "SELECT t.common_name, t.segment, s.* FROM scoring s JOIN targets t ON s.target_id = t.target_id WHERE s.asof_date = ? ORDER BY s.TSS DESC",
        (asof_date,),
    ).fetchall()
    market = conn.execute("SELECT * FROM market_context WHERE asof_date = ?", (asof_date,)).fetchone()
    conn.close()

    score_dicts = []
    for row in scores:
        payload = dict(row)
        if redact:
            payload["common_name"] = f"REDACTED TARGET {payload['target_id']}"
        payload["next_best_actions"] = load_json(payload.get("next_best_actions"), [])
        score_dicts.append(payload)

    env = _env()
    template = env.get_template("daily_brief.html")
    rendered = template.render(
        asof_date=asof_date,
        scores=score_dicts,
        market=market,
        audit_state=audit["status"],
        generated_at=datetime.utcnow().isoformat(),
    )

    html_path = OUTPUT_DIR / f"daily_brief_{asof_date}.html"
    html_path.write_text(rendered, encoding="utf-8")
    if fmt == "html":
        return html_path

    pdf_path = OUTPUT_DIR / f"daily_brief_{asof_date}.pdf"
    HTML(string=rendered).write_pdf(pdf_path)
    return pdf_path


def export_json(asof_date: str, target_id: str | None = None, redact: bool = False) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = get_connection()
    if target_id:
        targets = conn.execute(
            "SELECT t.*, s.* FROM targets t JOIN scoring s ON t.target_id = s.target_id WHERE s.asof_date = ? AND t.target_id = ?",
            (asof_date, target_id),
        ).fetchall()
    else:
        targets = conn.execute(
            "SELECT t.*, s.* FROM targets t JOIN scoring s ON t.target_id = s.target_id WHERE s.asof_date = ?",
            (asof_date,),
        ).fetchall()
    conn.close()
    payload = []
    for row in targets:
        item = dict(row)
        if redact:
            item["legal_name"] = f"REDACTED TARGET {item['target_id']}"
            item["common_name"] = f"REDACTED TARGET {item['target_id']}"
            item["strategic_fit_notes"] = "REDACTED"
        for field in ["top_levers", "top_risks", "next_best_actions", "bucket_coverage", "bucket_confidence"]:
            item[field] = load_json(item.get(field), []) if field in item else item.get(field)
        payload.append(item)
    out_path = OUTPUT_DIR / (
        f"target_{target_id}_{asof_date}.json" if target_id else f"daily_{asof_date}.json"
    )
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path
