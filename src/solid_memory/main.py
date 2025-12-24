from __future__ import annotations

from pathlib import Path

from .changelog import Changelog
from .collector import Collector
from .models import BackoffConfig, RateLimitConfig, SourceConfig


DEFAULT_SOURCES = [
    SourceConfig(
        name="Example",
        base_url="https://example.com",
        start_path="/",
        parser_version="v1",
        rate_limit=RateLimitConfig(requests=2, per_seconds=5),
        backoff=BackoffConfig(initial_seconds=1, max_seconds=4, max_attempts=3),
    )
]


def run(changelog_path: Path = Path("data/changelog.jsonl")) -> None:
    changelog = Changelog(changelog_path)
    collector = Collector(DEFAULT_SOURCES, changelog)
    collector.run()


if __name__ == "__main__":
    run()
