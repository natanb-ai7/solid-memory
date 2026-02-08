from __future__ import annotations

from datetime import datetime, date
from typing import Optional, Dict, List

from pydantic import BaseModel, Field


class SourcePointer(BaseModel):
    reference: str
    timestamp: datetime


class PortfolioPosition(BaseModel):
    asof_date: date
    cusip: str
    deal_name: str
    tranche: str
    rating: str
    original_balance: float
    current_balance: float
    price: float
    spread: float
    wal: float
    property_type_mix: str
    top_msas: str
    servicer: str
    special_servicing_flag: bool
    watchlist_flag: bool
    ara_flag: bool
    maturity_bucket: str
    comments: Optional[str] = None
    sources: Dict[str, SourcePointer] = Field(default_factory=dict)


class FundingTerm(BaseModel):
    counterparty: str
    asof_date: date
    haircut: float
    spread: float
    advance_rate: float
    margin_call_terms: str
    eligible_assets_rules: str
    sources: Dict[str, SourcePointer] = Field(default_factory=dict)


class HedgePosition(BaseModel):
    instrument: str
    notional: float
    dv01: float
    cs01_proxy: float
    reference_index: str
    entry_level: float
    current_level: float
    sources: Dict[str, SourcePointer] = Field(default_factory=dict)


class MarketIndicator(BaseModel):
    indicator: str
    asof_date: date
    value: float
    unit: str
    sources: Dict[str, SourcePointer] = Field(default_factory=dict)


class MATarget(BaseModel):
    company: str
    segment: str
    last_touch_date: date
    signal_score_components: str
    notes: str
    owner: str
    next_action: str
    status: str
    sources: Dict[str, SourcePointer] = Field(default_factory=dict)


class Trigger(BaseModel):
    name: str
    severity: str
    impacted_items: List[str]
    recommended_action: str
    confidence: float
    explanation: str


class RiskScore(BaseModel):
    cusip: str
    score: float
    drivers: Dict[str, float]


class FundingTightness(BaseModel):
    fti: Optional[float]
    components: Dict[str, Optional[float]]
    notes: str


class HedgeHygiene(BaseModel):
    hedge_ratio_drift: Optional[float]
    basis: Optional[float]
    concentration_flag: bool
    notes: str


class MemoSection(BaseModel):
    title: str
    content: str


class MemoOutput(BaseModel):
    run_id: str
    run_date: datetime
    data_freshness: str
    decisions: List[Dict[str, str]]
    risks: List[Dict[str, str]]
    liquidity: Dict[str, str]
    portfolio_heat: List[Dict[str, str]]
    hedge_hygiene: Dict[str, str]
    special_servicing_movers: List[Dict[str, str]]
    ma_pipeline: List[Dict[str, str]]
    appendix: List[Dict[str, str]]
