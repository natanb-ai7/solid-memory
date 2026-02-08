from prewire.schemas import PortfolioPosition, FundingTerm, HedgePosition
from prewire.triggers import evaluate_triggers


def test_trigger_flags():
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
            special_servicing_flag=True,
            watchlist_flag=True,
            ara_flag=True,
            maturity_bucket="0-2",
            comments=None,
            sources={},
        )
    ]
    funding = [
        FundingTerm(
            counterparty="Repo",
            asof_date="2024-01-01",
            haircut=0.4,
            spread=200,
            advance_rate=0.6,
            margin_call_terms="Daily",
            eligible_assets_rules="AAA",
            sources={},
        )
    ]
    hedges = [
        HedgePosition(
            instrument="CMBX",
            notional=100,
            dv01=1,
            cs01_proxy=1,
            reference_index="CMBX",
            entry_level=100,
            current_level=98,
            sources={},
        )
    ]
    triggers = evaluate_triggers(positions, funding, hedges)
    assert len(triggers) >= 3
