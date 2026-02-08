from __future__ import annotations

from engine.exporter import export_daily_brief, export_json, export_target_scorecard
from engine.run import run_daily
from engine.db import get_connection


def test_end_to_end_exports(sample_db, tmp_path):
    run_daily("2024-08-30")
    conn = get_connection()
    target_id = conn.execute("SELECT target_id FROM targets LIMIT 1").fetchone()[0]
    conn.close()
    html_path = export_target_scorecard("2024-08-30", target_id, fmt="html", final=False)
    assert html_path.exists()
    pdf_path = export_daily_brief("2024-08-30", fmt="pdf", final=False)
    assert pdf_path.exists()
    json_path = export_json("2024-08-30")
    assert json_path.exists()
