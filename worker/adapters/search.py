from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .base import SourceAdapter
from ..parsing import hash_listing_id
from ..confidence import compute_confidence
from ..http import get
from ..robots import allowed


class SearchAdapter(SourceAdapter):
    source_name = "search"

    def __init__(self, queries: list[str]):
        self.queries = queries

    def discover(self) -> list[str]:
        results: list[str] = []
        for query in self.queries:
            url = f"https://www.bing.com/search?q={quote_plus(query)}"
            if not allowed(url):
                continue
            response = get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for link in soup.select("li.b_algo h2 a"):
                href = link.get("href")
                if href and "i7" in href.lower():
                    results.append(href)
        return results

    def scrape_listing(self, url: str) -> dict:
        return {"url": url, "scraped_at": datetime.utcnow()}

    def normalize(self, raw: dict) -> dict:
        normalized = {
            "listing_id": hash_listing_id(raw["url"]),
            "source": self.source_name,
            "dealer_vdp_url": raw["url"],
            "model": "BMW i7",
            "date_last_seen": raw["scraped_at"],
            "last_scraped_at": raw["scraped_at"],
        }
        normalized["confidence_score"] = compute_confidence(normalized)
        return normalized
