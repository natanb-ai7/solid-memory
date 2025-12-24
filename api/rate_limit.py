import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, status


class RateLimiter:
    """Simple in-memory sliding window rate limiter."""

    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.access_log: Dict[str, Deque[float]] = defaultdict(deque)

    def check(self, identifier: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        events = self.access_log[identifier]

        while events and events[0] < window_start:
            events.popleft()

        if len(events) >= self.limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
            )

        events.append(now)


def rate_limit(identifier: str, limiter: RateLimiter) -> None:
    limiter.check(identifier)


# Global limiter instance for simplicity.
DEFAULT_LIMITER = RateLimiter(limit=30, window_seconds=60)

