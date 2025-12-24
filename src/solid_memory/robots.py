from __future__ import annotations

import urllib.robotparser
from urllib.parse import urljoin


def is_allowed(base_url: str, path: str, user_agent: str = "solid-memory-collector") -> bool:
    """Return True if robots.txt allows fetching the given path.

    The robots.txt file is fetched relative to the provided base_url.
    """
    robots_url = urljoin(base_url.rstrip("/") + "/", "robots.txt")
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)
    parser.read()
    target = urljoin(base_url, path)
    return parser.can_fetch(user_agent, target)
