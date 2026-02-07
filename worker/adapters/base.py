from abc import ABC, abstractmethod


class SourceAdapter(ABC):
    source_name: str

    @abstractmethod
    def discover(self) -> list[str]:
        """Return list of listing URLs to scrape."""

    @abstractmethod
    def scrape_listing(self, url: str) -> dict:
        """Fetch listing data from URL."""

    @abstractmethod
    def normalize(self, raw: dict) -> dict:
        """Normalize raw scrape data to listing schema."""
