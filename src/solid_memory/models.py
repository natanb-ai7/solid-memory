from __future__ import annotations

import dataclasses


@dataclasses.dataclass
class BackoffConfig:
    initial_seconds: float = 1.0
    max_seconds: float = 30.0
    max_attempts: int = 5


@dataclasses.dataclass
class RateLimitConfig:
    requests: int = 5
    per_seconds: float = 60.0


@dataclasses.dataclass
class SourceConfig:
    name: str
    base_url: str
    start_path: str = "/"
    enabled: bool = True
    parser_version: str = "v1"
    rate_limit: RateLimitConfig = dataclasses.field(default_factory=RateLimitConfig)
    backoff: BackoffConfig = dataclasses.field(default_factory=BackoffConfig)

    def full_url(self) -> str:
        return f"{self.base_url.rstrip('/')}{self.start_path}"
