import hashlib
import re
from bs4 import BeautifulSoup

LOANER_KEYWORDS = ["loaner", "demo", "service loaner", "executive demo"]
VIN_REGEX = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b")
MILES_REGEX = re.compile(r"(\d{1,3}(?:,\d{3})?)\s*(?:mi|miles)", re.IGNORECASE)
PRICE_REGEX = re.compile(r"\$\s?(\d{2,3}(?:,\d{3})+)" )


def hash_listing_id(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]


def detect_loaner(text: str) -> tuple[bool, list[str]]:
    matches = [kw for kw in LOANER_KEYWORDS if kw in text.lower()]
    return bool(matches), matches


def extract_vin(text: str) -> str | None:
    match = VIN_REGEX.search(text)
    return match.group(1) if match else None


def extract_miles(text: str) -> int | None:
    match = MILES_REGEX.search(text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def extract_prices(text: str) -> list[float]:
    return [float(price.replace(",", "")) for price in PRICE_REGEX.findall(text)]


def text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(" ")
