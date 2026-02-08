from prewire.scoring import compute_ma_signal_score, compute_risk_scores, DEFAULT_WEIGHTS
from prewire.schemas import PortfolioPosition


def test_compute_ma_signal_score():
    score = compute_ma_signal_score(
        {"HiringChange": 1, "NewsEvent": 0.5, "CapitalEvent": 0.2, "PartnershipSignal": 0}
    )
    assert round(score, 2) == 0.4 * 1 + 0.3 * 0.5 + 0.2 * 0.2


def test_compute_risk_scores_defaults():
    positions = [
        PortfolioPosition(
            asof_date="2024-01-01",
            cusip="123",
            deal_name="Test",
            tranche="A1",
            rating="AAA",
            original_balance=100,
            current_balance=90,
            price=95,
            spread=200,
            wal=2.5,
            property_type_mix="Office",
            top_msas="NY",
            servicer="Servicer",
            special_servicing_flag=False,
            watchlist_flag=True,
            ara_flag=False,
            maturity_bucket="0-2",
            comments=None,
            sources={},
        )
    ]
    scores = compute_risk_scores(positions, DEFAULT_WEIGHTS)
    assert scores[0].cusip == "123"
    assert 0 <= scores[0].score <= 1
