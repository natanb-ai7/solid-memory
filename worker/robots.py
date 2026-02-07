import urllib.robotparser
from urllib.parse import urlparse


_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def allowed(url: str, user_agent: str = "i7-scanner") -> bool:
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    parser = _cache.get(base)
    if not parser:
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(f"{base}/robots.txt")
        try:
            parser.read()
        except Exception:
            return False
        _cache[base] = parser
    return parser.can_fetch(user_agent, url)
