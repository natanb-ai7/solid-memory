from urllib.parse import urlparse
from .adapters.search import SearchAdapter

AGGREGATOR_DOMAINS = {
    "autotrader.com",
    "cars.com",
    "cargurus.com",
    "carfax.com",
    "edmunds.com",
    "truecar.com",
}


def discover_dealer_urls(queries: list[str]) -> list[str]:
    adapter = SearchAdapter(queries)
    results = adapter.discover()
    dealer_urls = []
    for url in results:
        domain = urlparse(url).netloc.lower()
        if any(domain.endswith(agg) for agg in AGGREGATOR_DOMAINS):
            continue
        if "bmw" not in domain:
            continue
        dealer_urls.append(url)
    return list(dict.fromkeys(dealer_urls))
