from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class Target(BaseModel):
    target_id: UUID
    legal_name: str
    common_name: str
    segment: str
    geography_footprint: str
    key_products: str
    key_customers_public: str
    ownership_status: str
    website_url: Optional[str] = None
    last_touch_date: Optional[date] = None
    owner: str
    status: str
    integration_complexity: int
    strategic_fit_notes: str


class Evidence(BaseModel):
    evidence_id: UUID
    target_id: UUID
    asof_date: date
    evidence_type: str
    source_url: Optional[str] = None
    file_ref: Optional[str] = None
    title: str
    excerpt: str = Field(max_length=500)
    tags: List[str]
    confidence: float
    created_by: str
    created_at: datetime


class Signals(BaseModel):
    signal_id: UUID
    target_id: UUID
    asof_date: date
    hiring_change_30d: Optional[float] = None
    news_event_score: Optional[float] = None
    capital_event_flag: Optional[bool] = None
    partnership_signal_score: Optional[float] = None
    exec_departure_flag: Optional[bool] = None
    customer_concentration_pct: Optional[float] = None
    banker_hired_flag: Optional[bool] = None
    litigation_flag: Optional[bool] = None
    notes: str
    evidence_ids: List[UUID]


class MarketContext(BaseModel):
    asof_date: date
    rates_context: str
    sofr_2y: Optional[float] = None
    sofr_5y: Optional[float] = None
    sofr_10y: Optional[float] = None
    cmbx_level_proxy: Optional[float] = None
    credit_spread_proxy: Optional[float] = None
    funding_tightness_index: Optional[float] = None
    evidence_ids: List[UUID]


class SubScoreInput(BaseModel):
    subscore_id: UUID
    target_id: UUID
    asof_date: date
    counterparty_access: float
    collateral_eligibility_lift: float
    haircut_or_term_benefit: float
    surveillance_delta: float
    workout_edge: float
    early_warning_coverage: float
    channel_scale: float
    borrower_overlap: float
    speed_to_close: float
    uniqueness: float
    integration_readiness: float
    contracts_durability: float
    cost_takeout_feasibility: float
    process_redundancy: float
    evidence_ids: List[UUID]


class ActionItem(BaseModel):
    action: str
    owner: str
    due_date: date


class Scoring(BaseModel):
    target_id: UUID
    asof_date: date
    FES: float
    LMS: float
    OS: float
    DMS: float
    OLS: float
    TSS: float
    drift_5d: float
    drift_20d: float
    evidence_coverage_pct: float
    score_confidence_pct: float
    top_levers: List[str]
    top_risks: List[str]
    next_best_actions: List[ActionItem]
    bucket_coverage: dict
    bucket_confidence: dict
    data_freshness_days: int


class ActionLog(BaseModel):
    action_id: UUID
    target_id: UUID
    asof_date: date
    action_type: str
    action_owner: str
    action_notes: str
    outcome_tag: str
    next_followup_date: Optional[date] = None
