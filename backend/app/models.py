from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .db import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(32))
    dealer_name: Mapped[str | None] = mapped_column(String(128))
    dealer_group: Mapped[str | None] = mapped_column(String(128))
    dealer_city: Mapped[str | None] = mapped_column(String(64))
    dealer_state: Mapped[str | None] = mapped_column(String(2))
    phone: Mapped[str | None] = mapped_column(String(32))
    dealer_vdp_url: Mapped[str] = mapped_column(Text)
    aggregator_url: Mapped[str | None] = mapped_column(Text)
    stock_no: Mapped[str | None] = mapped_column(String(64))
    vin: Mapped[str | None] = mapped_column(String(32))
    year: Mapped[int | None] = mapped_column(Integer)
    model: Mapped[str] = mapped_column(String(32))
    trim: Mapped[str | None] = mapped_column(String(32))
    exterior: Mapped[str | None] = mapped_column(String(64))
    interior: Mapped[str | None] = mapped_column(String(64))
    is_loaner: Mapped[bool] = mapped_column(Boolean, default=False)
    listing_keywords: Mapped[list[str] | None] = mapped_column(JSON)
    miles: Mapped[int | None] = mapped_column(Integer)
    msrp: Mapped[float | None] = mapped_column(Float)
    advertised_price: Mapped[float | None] = mapped_column(Float)
    stated_discount: Mapped[float | None] = mapped_column(Float)
    dealer_fees: Mapped[float | None] = mapped_column(Float)
    incentives: Mapped[list[dict] | None] = mapped_column(JSON)
    lease_terms: Mapped[dict | None] = mapped_column(JSON)
    date_first_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    date_last_seen: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_scraped_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    listing_status: Mapped[str] = mapped_column(String(16), default="active")
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_email: Mapped[str] = mapped_column(String(128))
    min_discount_percent: Mapped[float | None] = mapped_column(Float)
    max_miles: Mapped[int | None] = mapped_column(Integer)
    max_price: Mapped[float | None] = mapped_column(Float)
    states: Mapped[list[str] | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16), default="queued")
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    failures: Mapped[int] = mapped_column(Integer, default=0)
    blocked_domains: Mapped[list[str] | None] = mapped_column(JSON)
