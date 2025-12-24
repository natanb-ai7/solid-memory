from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Iterable

from .changelog import Changelog, ChangelogEntry
from .http import HttpResponse, fetch
from .models import BackoffConfig, RateLimitConfig, SourceConfig
from .rate_limiter import RateLimiter
from .robots import is_allowed

USER_AGENT = "solid-memory-collector"


def _build_rate_limiter(rate_limit: RateLimitConfig) -> RateLimiter:
    return RateLimiter(rate_limit.requests, rate_limit.per_seconds)


def _backoff_sleep(attempt: int, backoff: BackoffConfig) -> None:
    delay = min(backoff.initial_seconds * (2 ** (attempt - 1)), backoff.max_seconds)
    time.sleep(delay)


def _fetch(url: str) -> HttpResponse:
    return fetch(url, user_agent=USER_AGENT)


class Collector:
    def __init__(
        self,
        sources: Iterable[SourceConfig],
        changelog: Changelog,
    ) -> None:
        self.sources = list(sources)
        self.changelog = changelog
        self.rate_limiters = {
            source.name: _build_rate_limiter(source.rate_limit) for source in self.sources
        }

    def run(self) -> None:
        for source in self.sources:
            self._collect_source(source)

    def _collect_source(self, source: SourceConfig) -> None:
        if not source.enabled:
            self._record(source, "disabled")
            return

        if not is_allowed(source.base_url, source.start_path, user_agent=USER_AGENT):
            self._record(source, "robots-blocked")
            return

        limiter = self.rate_limiters[source.name]
        limiter.acquire()

        response = self._fetch_with_backoff(source)
        status = "success" if response is not None and response.ok else "failed"
        self._record(source, status)

    def _fetch_with_backoff(self, source: SourceConfig) -> HttpResponse | None:
        backoff = source.backoff
        url = source.full_url()
        attempt = 0
        while attempt < backoff.max_attempts:
            attempt += 1
            response = _fetch(url)
            if response.status_code in (429, 500, 502, 503, 504):
                _backoff_sleep(attempt, backoff)
                continue
            return response
        return None

    def _record(self, source: SourceConfig, status: str) -> None:
        entry = ChangelogEntry(
            source=source.name,
            url=source.full_url(),
            parser_version=source.parser_version,
            status=status,
            fetched_at=datetime.now(timezone.utc),
        )
        self.changelog.append(entry)
