"""Prometheus metrics and helpers."""

from __future__ import annotations

import os
from collections import defaultdict
from typing import DefaultDict

from prometheus_client import Counter, Gauge

# Prometheus counters to track parse attempts and errors by source.
PARSE_ATTEMPTS = Counter("parse_attempt_total", "Total parse attempts", ["source"])
PARSE_ERRORS = Counter("parse_error_total", "Total parse errors", ["source"])

# Gauges for alerting surfaces.
STALE_SOURCES = Gauge(
    "stale_source_total", "Number of sources whose last success is stale", ["source"]
)
PARSE_ERROR_RATE = Gauge(
    "parse_error_rate", "Rolling parse error rate per source", ["source"]
)

DEFAULT_ERROR_THRESHOLD = float(os.getenv("PARSE_ERROR_RATE_THRESHOLD", "0.2"))
DEFAULT_STALE_THRESHOLD_HOURS = int(os.getenv("STALE_THRESHOLD_HOURS", "24"))


def record_parse_result(source: str, success: bool) -> None:
    """Record the outcome of a parse attempt and update metrics."""
    PARSE_ATTEMPTS.labels(source=source).inc()
    if not success:
        PARSE_ERRORS.labels(source=source).inc()
    _recalculate_rates()


def _recalculate_rates() -> None:
    """Recompute error rates for all known sources and update gauges."""
    # prometheus_client does not expose counters by label easily; track manually.
    attempts: DefaultDict[str, float] = defaultdict(float)
    errors: DefaultDict[str, float] = defaultdict(float)

    for sample in PARSE_ATTEMPTS.collect()[0].samples:
        attempts[sample.labels["source"]] = sample.value
    for sample in PARSE_ERRORS.collect()[0].samples:
        errors[sample.labels["source"]] = sample.value

    for source, attempt_count in attempts.items():
        error_count = errors.get(source, 0)
        rate = (error_count / attempt_count) if attempt_count else 0.0
        PARSE_ERROR_RATE.labels(source=source).set(rate)


def compute_error_rates() -> dict[str, float]:
    """Return a mapping of source name to current error rate."""
    _recalculate_rates()
    rates: dict[str, float] = {}
    for sample in PARSE_ERROR_RATE.collect()[0].samples:
        rates[sample.labels["source"]] = sample.value
    return rates
