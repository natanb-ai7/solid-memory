import logging
import time
import threading
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
from urllib import robotparser

import requests


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class Source:
    id: str
    oem: str
    brand: str
    region: str
    url: str
    format: str
    cadence: str
    auth: str
    description: Optional[str] = None


class RateLimiter:
    """Simple thread-safe rate limiter keyed by hostname."""

    def __init__(self, min_interval_seconds: float = 1.0):
        self.min_interval = min_interval_seconds
        self._lock = threading.Lock()
        self._last_request: dict[str, float] = {}

    def wait(self, url: str) -> None:
        hostname = urlparse(url).hostname
        if not hostname:
            return
        with self._lock:
            last = self._last_request.get(hostname)
            now = time.time()
            if last is not None:
                elapsed = now - last
                if elapsed < self.min_interval:
                    sleep_time = self.min_interval - elapsed
                    logger.debug("Rate limiting %s for %.2fs", hostname, sleep_time)
                    time.sleep(sleep_time)
            self._last_request[hostname] = time.time()


_robot_cache: dict[str, robotparser.RobotFileParser] = {}


def is_allowed_by_robots(url: str, user_agent: str = "CollectorBot") -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = _robot_cache.get(robots_url)
    if parser is None:
        parser = robotparser.RobotFileParser()
        parser.set_url(robots_url)
        try:
            parser.read()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to read robots.txt from %s: %s", robots_url, exc)
            # When unsure, default to disallow to avoid violations.
            _robot_cache[robots_url] = parser
            return False
        _robot_cache[robots_url] = parser
    allowed = parser.can_fetch(user_agent, url)
    if not allowed:
        logger.info("Robots.txt disallows access to %s", url)
    return allowed


class BaseCollector:
    """Base collector responsible for validating robots and rate limiting."""

    user_agent = "CollectorBot"

    def __init__(self, source: Source, session: Optional[requests.Session] = None, rate_limiter: Optional[RateLimiter] = None):
        self.source = source
        self.session = session or requests.Session()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session.headers.setdefault("User-Agent", self.user_agent)

    def fetch(self) -> Optional[requests.Response]:
        if not is_allowed_by_robots(self.source.url, self.user_agent):
            logger.warning("Skipping %s due to robots.txt", self.source.id)
            return None
        self.rate_limiter.wait(self.source.url)
        try:
            response = self.session.get(self.source.url, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            logger.error("Failed to fetch %s: %s", self.source.id, exc)
            return None

    def collect(self) -> Optional[bytes]:
        """Override in subclasses to process response content."""
        raise NotImplementedError
