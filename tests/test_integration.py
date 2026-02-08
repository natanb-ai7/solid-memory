from pathlib import Path

from prewire.export import export_all
from prewire.ingest import (
    ingest_portfolio,
    ingest_funding,
    ingest_hedges,
    ingest_market,
    ingest_ma_targets,
)
from prewire.memo import build_memo
from prewire.scoring import DEFAULT_WEIGHTS
from prewire.triggers import evaluate_triggers
from prewire.validators import run_three_pass_validation


def test_full_pipeline(tmp_path: Path):
    base = Path("sample_data")
    positions = ingest_portfolio(base / "portfolio_positions.csv")
    funding = ingest_funding(base / "funding_terms.csv")
    hedges = ingest_hedges(base / "hedge_book.csv")
    market = ingest_market(base / "market_indicators.csv")
    ma_targets = ingest_ma_targets(base / "ma_targets.csv")
    triggers = evaluate_triggers(positions, funding, hedges)
    memo = build_memo(positions, funding, hedges, market, ma_targets, triggers, DEFAULT_WEIGHTS)
    report = run_three_pass_validation(
        positions, funding, hedges, market, DEFAULT_WEIGHTS, memo, triggers
    )
    assert report.passed
    outputs = export_all(memo, tmp_path, Path("app/templates"))
    assert outputs["json"].exists()
