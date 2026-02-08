from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NewsStub:
    """Stub connector for news feeds (no scraping)."""

    def fetch(self, query: str) -> list[dict]:
        return [
            {
                "title": f"Stub news item for {query}",
                "url": "https://example.com/news",
                "summary": "Manual input required.",
            }
        ]
