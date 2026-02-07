from datetime import datetime
from loguru import logger
from rq import Queue
from redis import Redis
from sqlalchemy.orm import Session
from .config import settings
from .db import SessionLocal
from .models import Listing, ScrapeJob, Alert
from .adapters.dealer_site import DealerSiteAdapter
from .adapters.aggregator import AggregatorAdapter
from .adapters.search import SearchAdapter
from .adapters.manual import ManualAdapter
from .notifications import send_email


redis_conn = Redis.from_url(settings.redis_url)
queue = Queue(connection=redis_conn)


def meets_alert(alert: Alert, listing: Listing) -> bool:
    if alert.min_discount_percent and listing.msrp and listing.advertised_price:
        discount = (listing.msrp - listing.advertised_price) / listing.msrp * 100
        if discount < alert.min_discount_percent:
            return False
    if alert.max_miles and listing.miles and listing.miles > alert.max_miles:
        return False
    if alert.max_price and listing.advertised_price and listing.advertised_price > alert.max_price:
        return False
    if alert.states and listing.dealer_state and listing.dealer_state not in alert.states:
        return False
    return True


def run_scrape_job():
    db: Session = SessionLocal()
    job = ScrapeJob(source="all", status="running", started_at=datetime.utcnow())
    db.add(job)
    db.commit()
    db.refresh(job)

    blocked_domains: list[str] = []
    failures = 0
    adapters = [
        DealerSiteAdapter([]),
        AggregatorAdapter([]),
        SearchAdapter(["BMW i7 loaner \"service loaner\""]),
        ManualAdapter([]),
    ]

    for adapter in adapters:
        for url in adapter.discover():
            try:
                raw = adapter.scrape_listing(url)
                normalized = adapter.normalize(raw)
                if normalized.get("blocked"):
                    blocked_domains.append(url)
                    continue
                listing = Listing(**normalized)
                db.merge(listing)
                db.commit()

                alerts = db.query(Alert).all()
                for alert in alerts:
                    if meets_alert(alert, listing):
                        send_email(
                            alert.user_email,
                            f\"New i7 loaner deal: {listing.dealer_name or 'Dealer'}\",
                            f\"Deal link: {listing.dealer_vdp_url}\",
                        )
            except Exception as exc:
                failures += 1
                logger.exception("Failed to scrape %s: %s", url, exc)

    job.status = "completed"
    job.finished_at = datetime.utcnow()
    job.failures = failures
    job.blocked_domains = blocked_domains
    db.commit()
    db.close()


def enqueue_scrape_job():
    queue.enqueue(run_scrape_job)


if __name__ == "__main__":
    run_scrape_job()
