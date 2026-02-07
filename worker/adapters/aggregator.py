from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .base import SourceAdapter
from ..parsing import text_from_html, extract_miles, extract_prices, extract_vin, detect_loaner, hash_listing_id
from ..confidence import compute_confidence
from ..robots import allowed
from ..http import get


class AggregatorAdapter(SourceAdapter):
    source_name = "aggregator"

    def __init__(self, seed_urls: list[str]):
        self.seed_urls = seed_urls

    def discover(self) -> list[str]:
        return self.seed_urls

    def scrape_listing(self, url: str) -> dict:
        if not allowed(url):
            return {"blocked": True, "url": url}
        response = get(url, timeout=15)
        response.raise_for_status()
        return {"url": url, "html": response.text, "scraped_at": datetime.utcnow()}

    def normalize(self, raw: dict) -> dict:
        if raw.get("blocked"):
            return {"blocked": True, "url": raw["url"]}
        soup = BeautifulSoup(raw["html"], "html.parser")
        dealer_link = soup.find("a", string=lambda text: text and "dealer" in text.lower())
        dealer_url = dealer_link["href"] if dealer_link else None
        text = text_from_html(raw["html"])
        is_loaner, keywords = detect_loaner(text)
        prices = extract_prices(text)
        vin = extract_vin(text)
        if not dealer_url and vin:
            query = quote_plus(f"{vin} dealer vehicle detail page")
            dealer_url = f"https://www.bing.com/search?q={query}"
        dealer_url = dealer_url or raw["url"]
        normalized = {
            "listing_id": hash_listing_id(dealer_url),
            "source": self.source_name,
            "dealer_vdp_url": dealer_url,
            "aggregator_url": raw["url"],
            "model": "BMW i7",
            "is_loaner": is_loaner,
            "listing_keywords": keywords,
            "miles": extract_miles(text),
            "vin": vin,
            "msrp": max(prices) if prices else None,
            "advertised_price": min(prices) if prices else None,
            "date_last_seen": raw["scraped_at"],
            "last_scraped_at": raw["scraped_at"],
        }
        normalized["confidence_score"] = compute_confidence(normalized)
        return normalized
