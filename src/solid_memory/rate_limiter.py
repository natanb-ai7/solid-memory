from __future__ import annotations

import time
from collections import deque


class RateLimiter:
    def __init__(self, max_calls: int, per_seconds: float) -> None:
        self.max_calls = max_calls
        self.per_seconds = per_seconds
        self.calls = deque()

    def acquire(self) -> None:
        now = time.time()
        while self.calls and now - self.calls[0] > self.per_seconds:
            self.calls.popleft()
        if len(self.calls) >= self.max_calls:
            sleep_for = self.per_seconds - (now - self.calls[0])
            if sleep_for > 0:
                time.sleep(sleep_for)
        self.calls.append(time.time())
