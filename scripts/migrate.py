"""Apply database schema migrations (initial table creation)."""
from __future__ import annotations

import logging

from shared.db import Base, get_engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    engine = get_engine()
    logger.info("Creating database schema if missing")
    Base.metadata.create_all(engine)
    logger.info("Migration complete")


if __name__ == "__main__":
    main()
