from pathlib import Path

from prewire.export import render_html
from prewire.memo import build_memo
from prewire.scoring import DEFAULT_WEIGHTS


def test_memo_structure_snapshot():
    memo = build_memo([], [], [], [], [], [], DEFAULT_WEIGHTS)
    html = render_html(memo, Path("app/templates"))
    required_sections = [
        "Header",
        "Today’s Top 3 Decisions",
        "Today’s Top 3 Risks",
        "Liquidity & Funding Readiness",
        "Portfolio Risk Heat",
        "Hedge Hygiene",
        "Special Servicing & Refi Movers",
        "M&A Pipeline: Today’s 5 Calls",
        "Appendix: Sources & Calculations",
    ]
    for section in required_sections:
        assert section in html
