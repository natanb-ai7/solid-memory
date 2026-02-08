from __future__ import annotations

from typing import Dict, List

from prewire.schemas import PortfolioPosition, RiskScore
from prewire.schemas import FundingTightness, FundingTerm, HedgeHygiene, HedgePosition, MarketIndicator


DEFAULT_WEIGHTS = {
    "servicing_momentum": 0.25,
    "refi_stress": 0.25,
    "cashflow_shock": 0.2,
    "liquidity_penalty": 0.15,
    "concentration_penalty": 0.15,
}


def _normalize(value: float, max_value: float) -> float:
    if max_value == 0:
        return 0.0
    return max(0.0, min(1.0, value / max_value))


def compute_risk_scores(
    positions: List[PortfolioPosition],
    weights: Dict[str, float] | None = None,
) -> List[RiskScore]:
    weights = weights or DEFAULT_WEIGHTS
    scores: List[RiskScore] = []
    for position in positions:
        servicing_momentum = 1.0 if position.special_servicing_flag else 0.0
        servicing_momentum += 0.5 if position.watchlist_flag else 0.0
        servicing_momentum += 0.5 if position.ara_flag else 0.0
        refi_stress = 1.0 if "0-2" in position.maturity_bucket else 0.4
        cashflow_shock = 0.8 if position.ara_flag else 0.2
        liquidity_penalty = _normalize(max(0.0, 100 - position.price), 30)
        concentration_penalty = 0.7 if "office" in position.property_type_mix.lower() else 0.2

        drivers = {
            "servicing_momentum": servicing_momentum,
            "refi_stress": refi_stress,
            "cashflow_shock": cashflow_shock,
            "liquidity_penalty": liquidity_penalty,
            "concentration_penalty": concentration_penalty,
        }
        score = sum(drivers[key] * weights.get(key, 0.0) for key in drivers)
        scores.append(RiskScore(cusip=position.cusip, score=score, drivers=drivers))
    return scores


def compute_ma_signal_score(signal_components: Dict[str, float]) -> float:
    return (
        0.4 * signal_components.get("HiringChange", 0.0)
        + 0.3 * signal_components.get("NewsEvent", 0.0)
        + 0.2 * signal_components.get("CapitalEvent", 0.0)
        + 0.1 * signal_components.get("PartnershipSignal", 0.0)
    )


def compute_fti(
    funding: List[FundingTerm],
    market: List[MarketIndicator],
) -> FundingTightness:
    components: Dict[str, float | None] = {
        "delta_haircut": None,
        "delta_repo_spread": None,
        "delta_bid_ask": None,
        "delta_cmbx_vol": None,
    }
    notes = []
    if len(funding) >= 2:
        haircuts = [term.haircut for term in funding]
        spreads = [term.spread for term in funding]
        components["delta_haircut"] = max(haircuts) - min(haircuts)
        components["delta_repo_spread"] = max(spreads) - min(spreads)
    else:
        notes.append("Need at least two funding rows to compute haircuts/spread deltas.")

    market_map = {}
    for indicator in market:
        market_map.setdefault(indicator.indicator, []).append(indicator.value)
    if market_map.get("BID_ASK_PROXY"):
        values = market_map["BID_ASK_PROXY"]
        components["delta_bid_ask"] = max(values) - min(values)
    else:
        notes.append("Missing BID_ASK_PROXY for bid-ask delta.")
    if market_map.get("CMBX_VOL_PROXY"):
        values = market_map["CMBX_VOL_PROXY"]
        components["delta_cmbx_vol"] = max(values) - min(values)
    else:
        notes.append("Missing CMBX_VOL_PROXY for CMBX vol delta.")

    available = [value for value in components.values() if value is not None]
    fti = None
    if available:
        fti = (
            (components["delta_haircut"] or 0)
            + 0.5 * (components["delta_repo_spread"] or 0)
            + 0.3 * (components["delta_bid_ask"] or 0)
            + 0.2 * (components["delta_cmbx_vol"] or 0)
        )
    return FundingTightness(fti=fti, components=components, notes="; ".join(notes) or "OK")


def compute_hedge_hygiene(
    positions: List[PortfolioPosition],
    hedges: List[HedgePosition],
) -> HedgeHygiene:
    if not positions or not hedges:
        return HedgeHygiene(
            hedge_ratio_drift=None,
            basis=None,
            concentration_flag=False,
            notes="MISSING hedge or portfolio data.",
        )
    portfolio_cs01 = sum(pos.current_balance * (pos.spread / 10000) for pos in positions)
    hedge_cs01 = sum(hedge.cs01_proxy for hedge in hedges)
    drift = (portfolio_cs01 / hedge_cs01) - 1 if hedge_cs01 else None
    basis = None
    property_totals: Dict[str, float] = {}
    for pos in positions:
        property_totals[pos.property_type_mix] = property_totals.get(pos.property_type_mix, 0) + pos.current_balance
    total_balance = sum(property_totals.values())
    concentration_flag = any(
        (balance / total_balance) > 0.3 for balance in property_totals.values() if total_balance
    )
    notes = "Monitor drift and rebalance if >10%."
    return HedgeHygiene(
        hedge_ratio_drift=drift,
        basis=basis,
        concentration_flag=concentration_flag,
        notes=notes,
    )
