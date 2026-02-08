from __future__ import annotations

from pathlib import Path


def test_scorecard_section_order():
    html = Path("app/templates/scorecard.html").read_text(encoding="utf-8")
    expected = [
        "A) Header",
        "B) TSS + Drift + Confidence + Evidence Coverage",
        "C) Bucket Breakdown",
        "D) Top 3 Synergy Levers",
        "E) Top 3 Integration Risks",
        "F) Next Best Actions",
        "G) What changed since yesterday?",
        "H) Appendix: Evidence Table",
    ]
    last_index = -1
    for section in expected:
        idx = html.find(section)
        assert idx > last_index
        last_index = idx
