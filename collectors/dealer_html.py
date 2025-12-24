from __future__ import annotations

import logging
from typing import Optional

from bs4 import BeautifulSoup

from .base import BaseCollector

logger = logging.getLogger(__name__)


class DealerHtmlCollector(BaseCollector):
    """Collector that scrapes dealer HTML inventory pages."""

    def collect(self) -> Optional[dict]:
        response = self.fetch()
        if response is None:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        title = (soup.title.string if soup.title else "").strip()
        listings = [
            link.get("href")
            for link in soup.select("a")
            if link.get("href") and "inventory" in link.get("href", "")
        ]
        logger.info(
            "Parsed dealer HTML for %s with %d inventory links", self.source.id, len(listings)
        )
        return {
            "title": title,
            "inventory_links": listings,
            "raw_html": response.text,
        }
