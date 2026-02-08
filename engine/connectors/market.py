from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MarketIndexStub:
    """Stub connector for market context."""

    def fetch(self) -> dict:
        return {
            "sofr_2y": None,
            "sofr_5y": None,
            "sofr_10y": None,
            "cmbx_level_proxy": None,
            "credit_spread_proxy": None,
            "funding_tightness_index": None,
            "note": "Manual input required.",
        }
