"""ORM models for the Solid Memory service."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class SourceStatus(Base):
    """Represents the latest status for an upstream source."""

    __tablename__ = "source_status"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    last_attempted_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_succeeded_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown")
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def mark_attempt(self) -> None:
        self.last_attempted_at = dt.datetime.now(dt.timezone.utc)
        self.status = "running"

    def mark_success(self) -> None:
        now = dt.datetime.now(dt.timezone.utc)
        self.last_attempted_at = now
        self.last_succeeded_at = now
        self.status = "healthy"
        self.notes = None

    def mark_failure(self, notes: str | None = None) -> None:
        self.last_attempted_at = dt.datetime.now(dt.timezone.utc)
        self.status = "failed"
        self.notes = notes
