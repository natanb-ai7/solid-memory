"""Pydantic schemas for API I/O."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field


class SourceStatusCreate(BaseModel):
    source_name: str = Field(..., min_length=1, max_length=255)
    notes: str | None = Field(None, max_length=500)


class SourceStatusRead(BaseModel):
    id: int
    source_name: str
    last_attempted_at: dt.datetime | None
    last_succeeded_at: dt.datetime | None
    status: str
    notes: str | None

    class Config:
        from_attributes = True


class ParseResult(BaseModel):
    success: bool
    notes: str | None = None


class HealthAlert(BaseModel):
    level: str
    message: str
    source_name: str | None = None


class HealthSummary(BaseModel):
    status: str
    sources: list[SourceStatusRead]
    stale_sources: list[str]
    parse_error_rates: dict[str, float]
    alerts: list[HealthAlert]
