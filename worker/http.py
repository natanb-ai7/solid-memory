import time
from urllib.parse import urlparse
import requests
from .config import settings

_last_request: dict[str, float] = {}


def get(url: str, **kwargs) -> requests.Response:
    domain = urlparse(url).netloc
    now = time.time()
    last = _last_request.get(domain, 0)
    wait = settings.request_rate_limit_s - (now - last)
    if wait > 0:
        time.sleep(wait)
    response = requests.get(url, **kwargs)
    _last_request[domain] = time.time()
    return response
