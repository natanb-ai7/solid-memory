from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict

from prewire.schemas import (
    PortfolioPosition,
    FundingTerm,
    HedgePosition,
    MarketIndicator,
    MemoOutput,
    Trigger,
)


@dataclass
class ValidationIssue:
    level: str
    message: str
    suggestion: str


@dataclass
class ValidationReport:
    passed: bool
    issues: List[ValidationIssue]


def validate_sources(
    positions: List[PortfolioPosition],
    funding: List[FundingTerm],
    hedges: List[HedgePosition],
    market: List[MarketIndicator],
    max_age_hours: int = 24,
) -> ValidationReport:
    issues: List[ValidationIssue] = []
    cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
    for collection in (positions, funding, hedges, market):
        for record in collection:
            if not record.sources:
                issues.append(
                    ValidationIssue(
                        level="error",
                        message=f"Missing sources for {record}",
                        suggestion="Re-ingest with source tracking.",
                    )
                )
            for source in record.sources.values():
                if source.timestamp < cutoff:
                    issues.append(
                        ValidationIssue(
                            level="warning",
                            message=f"Stale data source {source.reference}",
                            suggestion="Refresh market data or update timestamp.",
                        )
                    )
    return ValidationReport(passed=not any(i.level == "error" for i in issues), issues=issues)


def validate_calculations(
    weights: Dict[str, float],
    positions: List[PortfolioPosition] | None = None,
    funding: List[FundingTerm] | None = None,
) -> ValidationReport:
    issues: List[ValidationIssue] = []
    weight_sum = sum(weights.values())
    if weight_sum < 0.95 or weight_sum > 1.05:
        issues.append(
            ValidationIssue(
                level="error",
                message="Risk score weights out of range.",
                suggestion="Adjust weights to sum to 1.0.",
            )
        )
    for key, value in weights.items():
        if value < 0 or value > 1:
            issues.append(
                ValidationIssue(
                    level="error",
                    message=f"Weight {key} out of bounds: {value}",
                    suggestion="Set weight between 0 and 1.",
                )
            )
    for position in positions or []:
        if position.price < 0:
            issues.append(
                ValidationIssue(
                    level="error",
                    message=f"Negative price for {position.cusip}",
                    suggestion="Check pricing input.",
                )
            )
        if position.spread < 0:
            issues.append(
                ValidationIssue(
                    level="error",
                    message=f"Negative spread for {position.cusip}",
                    suggestion="Check spread input.",
                )
            )
    for term in funding or []:
        if term.haircut < 0 or term.haircut > 1:
            issues.append(
                ValidationIssue(
                    level="error",
                    message=f"Haircut out of range for {term.counterparty}",
                    suggestion="Set haircut between 0 and 1.",
                )
            )
        if term.spread < 0:
            issues.append(
                ValidationIssue(
                    level="error",
                    message=f"Negative repo spread for {term.counterparty}",
                    suggestion="Check repo spread input.",
                )
            )
    return ValidationReport(passed=not issues, issues=issues)


def validate_narrative(
    memo: MemoOutput,
    triggers: List[Trigger],
) -> ValidationReport:
    issues: List[ValidationIssue] = []
    trigger_items = {item for trigger in triggers for item in trigger.impacted_items}
    for decision in memo.decisions:
        if decision["action"] == "M&A outreach call":
            continue
        if decision["trigger"] not in trigger_items and decision["trigger"] != "MISSING":
            issues.append(
                ValidationIssue(
                    level="error",
                    message=f"Decision trigger mismatch: {decision['trigger']}",
                    suggestion="Ensure decisions reference fired triggers.",
                )
            )
    if memo.liquidity.get("FTI_direction") == "tightening" and "loose" in memo.liquidity.get(
        "summary", ""
    ).lower():
        issues.append(
            ValidationIssue(
                level="error",
                message="Liquidity narrative contradicts FTI direction.",
                suggestion="Update liquidity summary wording.",
            )
        )
    ambiguous_terms = ["material", "significant"]
    narrative_text = " ".join(
        [decision.get("rationale", "") for decision in memo.decisions]
        + [risk.get("why", "") for risk in memo.risks]
    ).lower()
    for term in ambiguous_terms:
        if term in narrative_text:
            issues.append(
                ValidationIssue(
                    level="warning",
                    message=f"Ambiguous term used: {term}",
                    suggestion="Quantify the statement or remove the term.",
                )
            )
    return ValidationReport(passed=not issues, issues=issues)


def run_three_pass_validation(
    positions: List[PortfolioPosition],
    funding: List[FundingTerm],
    hedges: List[HedgePosition],
    market: List[MarketIndicator],
    weights: Dict[str, float],
    memo: MemoOutput,
    triggers: List[Trigger],
) -> ValidationReport:
    reports = [
        validate_sources(positions, funding, hedges, market),
        validate_calculations(weights, positions, funding),
        validate_narrative(memo, triggers),
    ]
    issues = [issue for report in reports for issue in report.issues]
    return ValidationReport(passed=all(report.passed for report in reports), issues=issues)
