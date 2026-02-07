from datetime import datetime
from .base import SourceAdapter
from ..parsing import hash_listing_id
from ..confidence import compute_confidence


class ManualAdapter(SourceAdapter):
    source_name = "manual"

    def __init__(self, urls: list[str]):
        self.urls = urls

    def discover(self) -> list[str]:
        return self.urls

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
