"""Collector service that normalizes source data into the catalog tables."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.config import get_settings
from shared.db import get_session_factory
from shared.models import Make, Model, Trim

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def load_seed_data() -> list[dict]:
    settings = get_settings()
    path = Path(settings.catalog_seed_path)
    if not path.exists():
        raise FileNotFoundError(f"Seed data not found at {path}")

    return json.loads(path.read_text())


def upsert_catalog(session: Session, payload: list[dict]) -> None:
    for make_payload in payload:
        make = session.scalar(select(Make).where(Make.name == make_payload["make"]))
        if make is None:
            make = Make(name=make_payload["make"])
            session.add(make)
            session.flush()

        for model_payload in make_payload.get("models", []):
            model = session.scalar(
                select(Model).where(
                    Model.make_id == make.id, Model.name == model_payload["name"]
                )
            )
            if model is None:
                model = Model(name=model_payload["name"], make=make)
                session.add(model)
                session.flush()

            for trim_name in model_payload.get("trims", []):
                trim = session.scalar(
                    select(Trim).where(Trim.model_id == model.id, Trim.name == trim_name)
                )
                if trim is None:
                    session.add(Trim(name=trim_name, model=model))


def main() -> None:
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        payload = load_seed_data()
        logger.info("Loaded %s makes from seed data", len(payload))
        upsert_catalog(session, payload)
        session.commit()
        logger.info("Catalog upsert complete")
    finally:
        session.close()


if __name__ == "__main__":
    main()
