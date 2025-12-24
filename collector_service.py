import logging
import time
from pathlib import Path
from typing import Callable, Dict, List, Type

import schedule
import yaml

from collectors.api_feed import ApiFeedCollector
from collectors.base import BaseCollector, RateLimiter, Source
from collectors.dealer_html import DealerHtmlCollector
from collectors.oem_pdf import OemPdfCollector

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


FORMAT_TO_COLLECTOR: Dict[str, Type[BaseCollector]] = {
    "pdf": OemPdfCollector,
    "html": DealerHtmlCollector,
    "json_api": ApiFeedCollector,
}


def load_sources(config_path: Path) -> List[Source]:
    raw_sources = yaml.safe_load(config_path.read_text())
    return [Source(**entry) for entry in raw_sources]


def get_collector(source: Source, rate_limiter: RateLimiter) -> BaseCollector:
    collector_cls = FORMAT_TO_COLLECTOR.get(source.format)
    if collector_cls is None:
        raise ValueError(f"No collector registered for format {source.format}")
    return collector_cls(source=source, rate_limiter=rate_limiter)


def run_collector(source: Source, rate_limiter: RateLimiter) -> None:
    collector = get_collector(source, rate_limiter)
    result = collector.collect()
    if result is None:
        logger.warning("Collector %s finished with no data", source.id)
    else:
        logger.info("Collector %s completed with payload type %s", source.id, type(result))


def schedule_collectors(sources: List[Source]) -> None:
    rate_limiter = RateLimiter()
    cadence_to_job: Dict[str, Callable[[Callable], schedule.Job]] = {
        "daily": schedule.every().day.at("00:30").do,
        "weekly": schedule.every().monday.at("01:00").do,
    }

    for source in sources:
        job = cadence_to_job.get(source.cadence)
        if not job:
            logger.warning("Skipping %s due to unsupported cadence %s", source.id, source.cadence)
            continue
        logger.info("Scheduling %s (%s) with cadence %s", source.id, source.format, source.cadence)
        job(run_collector, source=source, rate_limiter=rate_limiter)


if __name__ == "__main__":
    config_path = Path("sources.yaml")
    sources = load_sources(config_path)
    schedule_collectors(sources)
    logger.info("Starting collector scheduler loop")
    while True:
        schedule.run_pending()
        time.sleep(5)
