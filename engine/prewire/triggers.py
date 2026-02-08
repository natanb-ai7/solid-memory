from __future__ import annotations

from typing import Dict, List

from prewire.schemas import PortfolioPosition, FundingTerm, Trigger, HedgePosition


DEFAULT_TRIGGERS = {
    "watchlist_flag": {"severity": "med", "action": "Review servicing update and model loss."},
    "special_servicing_flag": {
        "severity": "high",
        "action": "Escalate to asset workout and confirm ARA status.",
    },
    "ara_flag": {"severity": "high", "action": "Confirm ARA amount and adjust cashflow."},
    "price_drop": {"severity": "med", "action": "Check bid-ask and reassess exit plan."},
    "haircut_increase": {"severity": "high", "action": "Review funding headroom and margins."},
}


def evaluate_triggers(
    positions: List[PortfolioPosition],
    funding: List[FundingTerm],
    hedges: List[HedgePosition],
    trigger_config: Dict[str, Dict] | None = None,
) -> List[Trigger]:
    trigger_config = trigger_config or DEFAULT_TRIGGERS
    triggered: List[Trigger] = []
    for position in positions:
        if position.watchlist_flag:
            cfg = trigger_config["watchlist_flag"]
            triggered.append(
                Trigger(
                    name="Watchlist flag on",
                    severity=cfg["severity"],
                    impacted_items=[position.cusip],
                    recommended_action=cfg["action"],
                    confidence=0.8,
                    explanation="Watchlist flag turned on (threshold: True).",
                )
            )
        if position.special_servicing_flag:
            cfg = trigger_config["special_servicing_flag"]
            triggered.append(
                Trigger(
                    name="Special servicing flag on",
                    severity=cfg["severity"],
                    impacted_items=[position.cusip],
                    recommended_action=cfg["action"],
                    confidence=0.9,
                    explanation="Special servicing flag turned on (threshold: True).",
                )
            )
        if position.ara_flag:
            cfg = trigger_config["ara_flag"]
            triggered.append(
                Trigger(
                    name="ARA flag on",
                    severity=cfg["severity"],
                    impacted_items=[position.cusip],
                    recommended_action=cfg["action"],
                    confidence=0.85,
                    explanation="ARA flag turned on (threshold: True).",
                )
            )
    for term in funding:
        if term.haircut >= 0.35:
            cfg = trigger_config["haircut_increase"]
            triggered.append(
                Trigger(
                    name="Repo haircut elevated",
                    severity=cfg["severity"],
                    impacted_items=[term.counterparty],
                    recommended_action=cfg["action"],
                    confidence=0.75,
                    explanation="Haircut above 35% (threshold: >= 0.35).",
                )
            )
    if hedges:
        drift = sum(hedge.cs01_proxy for hedge in hedges)
        if drift == 0:
            return triggered
    return triggered
