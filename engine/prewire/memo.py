from __future__ import annotations

from datetime import datetime
from typing import List, Dict
from uuid import uuid4

from prewire.schemas import (
    PortfolioPosition,
    FundingTerm,
    HedgePosition,
    MarketIndicator,
    MATarget,
    Trigger,
    MemoOutput,
)
from prewire.scoring import (
    compute_risk_scores,
    compute_ma_signal_score,
    compute_fti,
    compute_hedge_hygiene,
)


def _data_freshness(market: List[MarketIndicator]) -> str:
    if not market:
        return "MISSING"
    latest = max(item.asof_date for item in market)
    return f"Market data as of {latest.isoformat()}"


def build_memo(
    positions: List[PortfolioPosition],
    funding: List[FundingTerm],
    hedges: List[HedgePosition],
    market: List[MarketIndicator],
    ma_targets: List[MATarget],
    triggers: List[Trigger],
    weights: Dict[str, float],
    redaction: bool = False,
) -> MemoOutput:
    run_id = uuid4().hex[:12]
    run_date = datetime.utcnow()
    risk_scores = compute_risk_scores(positions, weights)
    top_risks = sorted(risk_scores, key=lambda r: r.score, reverse=True)[:3]
    top_decisions = triggers[:3]
    funding_summary = funding[0] if funding else None
    fti = compute_fti(funding, market)
    hedge_hygiene_calc = compute_hedge_hygiene(positions, hedges)

    decisions = []
    for trigger in top_decisions:
        decisions.append(
            {
                "action": trigger.recommended_action,
                "rationale": trigger.explanation,
                "data": ", ".join(trigger.impacted_items) if trigger.impacted_items else "MISSING",
                "trigger": trigger.impacted_items[0] if trigger.impacted_items else "MISSING",
                "next_step": "Confirm data source and execute playbook step.",
                "confidence": f"{int(trigger.confidence * 100)}%",
            }
        )
    if ma_targets and len(decisions) < 3:
        target = ma_targets[0]
        decisions.append(
            {
                "action": "M&A outreach call",
                "rationale": f"Engage {target.company} on {target.segment} opportunity.",
                "data": target.company if not redaction else "REDACTED",
                "trigger": target.company if not redaction else "REDACTED",
                "next_step": target.next_action,
                "confidence": "60%",
            }
        )
    if not decisions:
        decisions.append(
            {
                "action": "MISSING",
                "rationale": "No triggers fired.",
                "data": "MISSING",
                "trigger": "MISSING",
                "next_step": "Add trigger configuration or update data feeds.",
                "confidence": "0%",
            }
        )

    risks = []
    for risk in top_risks:
        risks.append(
            {
                "what": risk.cusip,
                "why": f"RiskScore {risk.score:.2f}",
                "triggers": ", ".join(
                    f"{key}:{value:.2f}" for key, value in risk.drivers.items()
                ),
                "mitigants": "Evaluate hedge or liquidity buffers.",
                "change_mind": "Improved servicing status or price recovery.",
                "confidence": "70%",
            }
        )
    if not risks:
        risks.append(
            {
                "what": "MISSING",
                "why": "No positions available.",
                "triggers": "MISSING",
                "mitigants": "MISSING",
                "change_mind": "Add portfolio positions.",
                "confidence": "0%",
            }
        )

    summary_text = funding_summary.margin_call_terms if funding_summary else "MISSING"
    eligibility_text = funding_summary.eligible_assets_rules if funding_summary else "MISSING"
    liquidity = {
        "FTI": f"{fti.fti:.2f}" if fti.fti is not None else "MISSING",
        "FTI_direction": "tightening" if fti.fti and fti.fti > 0 else "stable",
        "summary": "REDACTED" if redaction else summary_text,
        "eligibility": "REDACTED" if redaction else eligibility_text,
        "notes": fti.notes,
    }

    portfolio_heat = [
        {
            "cusip": risk.cusip,
            "score": f"{risk.score:.2f}",
            "drivers": ", ".join(
                f"{key}:{value:.2f}" for key, value in risk.drivers.items()
            ),
        }
        for risk in sorted(risk_scores, key=lambda r: r.score, reverse=True)[:10]
    ]

    hedge_hygiene = {
        "drift": f"{hedge_hygiene_calc.hedge_ratio_drift:.2f}"
        if hedge_hygiene_calc.hedge_ratio_drift is not None
        else "MISSING",
        "basis": f"{hedge_hygiene_calc.basis:.2f}"
        if hedge_hygiene_calc.basis is not None
        else "MISSING",
        "concentration": "FLAG" if hedge_hygiene_calc.concentration_flag else "OK",
        "notes": hedge_hygiene_calc.notes,
    }

    special_servicing = [
        {
            "cusip": pos.cusip,
            "status": "Special Servicing" if pos.special_servicing_flag else "Watchlist",
            "comment": pos.comments or "MISSING",
        }
        for pos in positions
        if pos.special_servicing_flag or pos.watchlist_flag
    ][:5]

    ma_calls = []
    for idx, target in enumerate(ma_targets[:5], start=1):
        components = {
            "HiringChange": 0.6,
            "NewsEvent": 0.4,
            "CapitalEvent": 0.3,
            "PartnershipSignal": 0.2,
        }
        score = compute_ma_signal_score(components)
        ma_calls.append(
            {
                "company": f"REDACTED-{idx}" if redaction else target.company,
                "thesis": target.segment,
                "signal": f"{score:.2f}",
                "angle": target.next_action,
            }
        )

    appendix = []
    run_timestamp = run_date.isoformat()
    for pos in positions[:5]:
        appendix.append(
            {
                "metric": f"{pos.cusip} price",
                "value": f"{pos.price}",
                "source": pos.sources.get("price").reference if pos.sources else "MISSING",
                "timestamp": pos.sources.get("price").timestamp.isoformat()
                if pos.sources
                else run_timestamp,
            }
        )
    for idx, term in enumerate(funding[:3], start=1):
        appendix.append(
            {
                "metric": f"{'REDACTED-' + str(idx) if redaction else term.counterparty} haircut",
                "value": f"{term.haircut}",
                "source": term.sources.get("haircut").reference if term.sources else "MISSING",
                "timestamp": term.sources.get("haircut").timestamp.isoformat()
                if term.sources
                else run_timestamp,
            }
        )
    appendix.append(
        {
            "metric": "FTI",
            "value": liquidity["FTI"],
            "source": "calc: Δhaircut + 0.5*Δrepo_spread + 0.3*Δbid_ask + 0.2*ΔCMBX_vol_proxy",
            "timestamp": run_timestamp,
        }
    )
    appendix.append(
        {
            "metric": "Hedge drift",
            "value": hedge_hygiene["drift"],
            "source": "calc: portfolio_cs01 / hedge_cs01 - 1",
            "timestamp": run_timestamp,
        }
    )
    for heat in portfolio_heat:
        appendix.append(
            {
                "metric": f"RiskScore {heat['cusip']}",
                "value": heat["score"],
                "source": "calc: weighted drivers from portfolio_positions.csv",
                "timestamp": run_timestamp,
            }
        )
    for risk in top_risks:
        for key, value in risk.drivers.items():
            appendix.append(
                {
                    "metric": f"{risk.cusip} {key}",
                    "value": f"{value:.2f}",
                    "source": "calc: driver component from portfolio_positions.csv",
                    "timestamp": run_timestamp,
                }
            )

    return MemoOutput(
        run_id=run_id,
        run_date=run_date,
        data_freshness=_data_freshness(market),
        decisions=decisions,
        risks=risks,
        liquidity=liquidity,
        portfolio_heat=portfolio_heat,
        hedge_hygiene=hedge_hygiene,
        special_servicing_movers=special_servicing,
        ma_pipeline=ma_calls,
        appendix=appendix,
    )
