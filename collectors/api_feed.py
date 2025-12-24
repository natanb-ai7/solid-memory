from __future__ import annotations

import logging
from typing import Any, Optional

from .base import BaseCollector

logger = logging.getLogger(__name__)


class ApiFeedCollector(BaseCollector):
    """Collector for JSON API feeds using bearer or session authentication."""

    def collect(self) -> Optional[dict[str, Any]]:
        response = self.fetch()
        if response is None:
            return None
        try:
            payload = response.json()
        except ValueError:
            logger.error("%s returned non-JSON response", self.source.id)
            return None

        logger.info(
            "Fetched JSON payload with %d top-level keys from %s",
            len(payload) if isinstance(payload, dict) else 1,
            self.source.id,
        )
        return {
            "meta": {
                "status_code": response.status_code,
                "headers": dict(response.headers),
            },
            "data": payload,
        }
