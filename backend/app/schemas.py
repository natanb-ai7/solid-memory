from pydantic import BaseModel
from datetime import datetime
from typing import Any


class ListingBase(BaseModel):
    listing_id: str
    source: str
    dealer_name: str | None = None
    dealer_group: str | None = None
    dealer_city: str | None = None
    dealer_state: str | None = None
    phone: str | None = None
    dealer_vdp_url: str
    aggregator_url: str | None = None
    stock_no: str | None = None
    vin: str | None = None
    year: int | None = None
    model: str
    trim: str | None = None
    exterior: str | None = None
    interior: str | None = None
    is_loaner: bool = False
    listing_keywords: list[str] | None = None
    miles: int | None = None
    msrp: float | None = None
    advertised_price: float | None = None
    stated_discount: float | None = None
    dealer_fees: float | None = None
    incentives: list[dict] | None = None
    lease_terms: dict | None = None
    listing_status: str = "active"
    confidence_score: float = 0.0


class Listing(ListingBase):
    id: int
    date_first_seen: datetime
    date_last_seen: datetime
    last_scraped_at: datetime


class Alert(BaseModel):
    id: int
    user_email: str
    min_discount_percent: float | None = None
    max_miles: int | None = None
    max_price: float | None = None
    states: list[str] | None = None
    created_at: datetime


class AlertCreate(BaseModel):
    user_email: str
    min_discount_percent: float | None = None
    max_miles: int | None = None
    max_price: float | None = None
    states: list[str] | None = None


class AdminStats(BaseModel):
    active_listings: int
    blocked_domains: list[str]
    failures_by_domain: dict[str, int]
    last_updated: datetime | None


class DealScore(BaseModel):
    score: float
    discount_percent: float
    value_components: dict[str, float]
    negotiation_playbook: dict[str, Any]


class DealWithScore(Listing):
    score: DealScore


class CompsResponse(BaseModel):
    listing_id: str
    comps: list[DealWithScore]
    median_discount_percent: float
    percentile: float
