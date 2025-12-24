from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List
from unittest import TestCase
from unittest.mock import patch

from solid_memory.changelog import Changelog
from solid_memory.collector import Collector
from solid_memory.http import HttpResponse
from solid_memory.models import BackoffConfig, RateLimitConfig, SourceConfig


class CollectorTests(TestCase):
    def _make_response(self, status_code: int) -> HttpResponse:
        return HttpResponse(status_code=status_code, content=b"payload", url="https://example.com/")

    def test_disabled_source_records_status(self) -> None:
        source = SourceConfig(name="disabled", base_url="https://example.com", enabled=False)
        with tempfile.TemporaryDirectory() as tempdir:
            changelog = Changelog(Path(tempdir) / "changelog.jsonl")
            collector = Collector([source], changelog)
            collector.run()
            with open(Path(tempdir) / "changelog.jsonl", encoding="utf-8") as handle:
                lines = handle.readlines()
        record = json.loads(lines[0])
        self.assertEqual(record["status"], "disabled")

    def test_robots_blocked_prevents_fetch(self) -> None:
        source = SourceConfig(name="blocked", base_url="https://blocked.example")
        with tempfile.TemporaryDirectory() as tempdir, patch(
            "solid_memory.collector.is_allowed", return_value=False
        ) as is_allowed:
            changelog = Changelog(Path(tempdir) / "changelog.jsonl")
            collector = Collector([source], changelog)
            collector.run()
            is_allowed.assert_called_once()
            with open(Path(tempdir) / "changelog.jsonl", encoding="utf-8") as handle:
                entry = json.loads(handle.readline())
        self.assertEqual(entry["status"], "robots-blocked")

    def test_rate_limiter_honors_window(self) -> None:
        rate_limit = RateLimitConfig(requests=2, per_seconds=10)
        limiter_source = SourceConfig(
            name="limited",
            base_url="https://limited.example",
            rate_limit=rate_limit,
        )
        with tempfile.TemporaryDirectory() as tempdir:
            changelog = Changelog(Path(tempdir) / "changelog.jsonl")
            collector = Collector([limiter_source], changelog)
            with patch("time.sleep") as sleep, patch(
                "solid_memory.rate_limiter.time.time",
                side_effect=[0, 0, 0.5, 0.5, 0.5, 0.5],
            ):
                limiter = collector.rate_limiters[limiter_source.name]
                limiter.acquire()
                limiter.acquire()
                limiter.acquire()
            sleep.assert_called_once()
            args, _ = sleep.call_args
            self.assertAlmostEqual(args[0], 9.5, places=1)

    def test_backoff_retries_and_records_failure(self) -> None:
        backoff = BackoffConfig(initial_seconds=0.1, max_seconds=0.1, max_attempts=2)
        source = SourceConfig(
            name="flaky",
            base_url="https://flaky.example",
            backoff=backoff,
        )
        responses: List[requests.Response] = [
            self._make_response(500),
            self._make_response(200),
        ]
        with tempfile.TemporaryDirectory() as tempdir, patch(
            "solid_memory.collector._fetch", side_effect=responses
        ) as fetch, patch("solid_memory.collector._backoff_sleep") as sleep, patch(
            "solid_memory.collector.is_allowed", return_value=True
        ):
            changelog = Changelog(Path(tempdir) / "changelog.jsonl")
            collector = Collector([source], changelog)
            collector.run()
            self.assertEqual(fetch.call_count, 2)
            sleep.assert_called_once()
            with open(Path(tempdir) / "changelog.jsonl", encoding="utf-8") as handle:
                record = json.loads(handle.readline())
        self.assertEqual(record["status"], "success")

    def test_changelog_records_parser_version_and_timestamp(self) -> None:
        source = SourceConfig(
            name="example",
            base_url="https://example.com",
            parser_version="v2",
        )
        response = self._make_response(200)
        with tempfile.TemporaryDirectory() as tempdir, patch(
            "solid_memory.collector._fetch", return_value=response
        ), patch("solid_memory.collector.is_allowed", return_value=True):
            changelog = Changelog(Path(tempdir) / "changelog.jsonl")
            collector = Collector([source], changelog)
            collector.run()
            with open(Path(tempdir) / "changelog.jsonl", encoding="utf-8") as handle:
                entry = json.loads(handle.readline())
        self.assertEqual(entry["parser_version"], "v2")
        parsed_timestamp = datetime.fromisoformat(entry["fetched_at"])
        self.assertEqual(parsed_timestamp.tzinfo, timezone.utc)
