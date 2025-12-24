from __future__ import annotations

import logging
from typing import Optional

from .base import BaseCollector

logger = logging.getLogger(__name__)


class OemPdfCollector(BaseCollector):
    """Collector that downloads OEM-hosted brochures as raw PDF bytes."""

    def collect(self) -> Optional[bytes]:
        response = self.fetch()
        if response is None:
            return None
        content_type = response.headers.get("Content-Type", "")
        if "pdf" not in content_type.lower():
            logger.warning(
                "Expected PDF content for %s but received %s", self.source.id, content_type
            )
        logger.info("Downloaded %d bytes from %s", len(response.content), self.source.url)
        return response.content
