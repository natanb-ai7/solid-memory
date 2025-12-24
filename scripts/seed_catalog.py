"""Seed the database with reference catalog data."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from collector.main import upsert_catalog
from shared.config import get_settings
from shared.db import get_session_factory

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_seed_payload() -> list[dict]:
    settings = get_settings()
    payload_path = Path(settings.catalog_seed_path)
    if not payload_path.exists():
        raise FileNotFoundError(f"Seed data missing at {payload_path}")
    return json.loads(payload_path.read_text())


def main() -> None:
    SessionLocal = get_session_factory()
    session: Session = SessionLocal()
    try:
        payload = load_seed_payload()
        logger.info("Seeding catalog with %s makes", len(payload))
        upsert_catalog(session, payload)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
