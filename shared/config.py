"""Configuration helpers for shared services."""
from __future__ import annotations

import os
from functools import lru_cache


class Settings:
    """Runtime configuration for services."""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        self.app_env = os.getenv("APP_ENV", "development")
        self.catalog_seed_path = os.getenv("CATALOG_SEED_PATH", "data/catalog_seed.json")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
