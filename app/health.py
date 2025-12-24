"""Health-check helpers for summarizing source status and alerts."""

from __future__ import annotations

import datetime as dt
from typing import Iterable, Tuple

from .metrics import (
    DEFAULT_ERROR_THRESHOLD,
    DEFAULT_STALE_THRESHOLD_HOURS,
    PARSE_ERROR_RATE,
    STALE_SOURCES,
    compute_error_rates,
)
from .models import SourceStatus
from .schemas import HealthAlert, HealthSummary, SourceStatusRead


def detect_stale_sources(sources: Iterable[SourceStatus], hours: int) -> list[str]:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours)
    stale: list[str] = []
    for source in sources:
        last = source.last_succeeded_at or source.last_attempted_at
        if last and last < cutoff:
            stale.append(source.source_name)
            STALE_SOURCES.labels(source=source.source_name).set(1)
        else:
            STALE_SOURCES.labels(source=source.source_name).set(0)
    return stale


def build_health_summary(
    sources: Iterable[SourceStatus],
    *,
    stale_hours: int = DEFAULT_STALE_THRESHOLD_HOURS,
    error_threshold: float = DEFAULT_ERROR_THRESHOLD,
) -> HealthSummary:
    error_rates = compute_error_rates()
    stale = detect_stale_sources(sources, stale_hours)
    alerts = _collect_alerts(sources, stale, error_rates, error_threshold)

    status = "ok"
    if alerts:
        status = "degraded" if all(alert.level != "critical" for alert in alerts) else "critical"

    return HealthSummary(
        status=status,
        sources=[SourceStatusRead.model_validate(source) for source in sources],
        stale_sources=stale,
        parse_error_rates=error_rates,
        alerts=alerts,
    )


def _collect_alerts(
    sources: Iterable[SourceStatus],
    stale: list[str],
    error_rates: dict[str, float],
    error_threshold: float,
) -> list[HealthAlert]:
    alerts: list[HealthAlert] = []

    for source_name, rate in error_rates.items():
        if rate >= error_threshold:
            alerts.append(
                HealthAlert(
                    level="critical" if rate >= 2 * error_threshold else "warning",
                    message=f"Parse error rate {rate:.2%} exceeds threshold {error_threshold:.2%}",
                    source_name=source_name,
                )
            )
            PARSE_ERROR_RATE.labels(source=source_name).set(rate)

    for source_name in stale:
        alerts.append(
            HealthAlert(
                level="warning",
                message="Source has not succeeded within the allowed window",
                source_name=source_name,
            )
        )

    # If we have no data on a source at all, highlight it.
    for source in sources:
        if source.last_succeeded_at is None and source.last_attempted_at is None:
            alerts.append(
                HealthAlert(
                    level="warning",
                    message="Source has never reported a run",
                    source_name=source.source_name,
                )
            )

    return alerts
