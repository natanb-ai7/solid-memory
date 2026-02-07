from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from loguru import logger
from .db import get_db
from .auth import require_auth
from . import models, schemas, scoring, playbook

# FastAPI chosen for fast async APIs with minimal overhead and strong typing for scraping pipelines.
app = FastAPI(title="i7 Loaner Deal Scanner")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/listings", response_model=list[schemas.DealWithScore])
async def list_listings(
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_auth),
):
    listings = db.query(models.Listing).filter(models.Listing.listing_status == "active").all()
    results = []
    for listing in listings:
        score = scoring.compute_value_score(listing.__dict__)
        playbook_data = playbook.build_playbook(listing.__dict__)
        results.append(
            schemas.DealWithScore(
                **listing.__dict__,
                score=schemas.DealScore(
                    **score,
                    negotiation_playbook=playbook_data,
                ),
            )
        )
    return results


@app.get("/listings/{listing_id}", response_model=schemas.DealWithScore)
async def get_listing(
    listing_id: str,
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_auth),
):
    listing = db.query(models.Listing).filter(models.Listing.listing_id == listing_id).first()
    if not listing:
        return schemas.DealWithScore(
            listing_id=listing_id,
            source="unknown",
            model="BMW i7",
            dealer_vdp_url="",
            score=schemas.DealScore(
                score=0,
                discount_percent=0,
                value_components={},
                negotiation_playbook={},
            ),
            id=0,
            date_first_seen=datetime.utcnow(),
            date_last_seen=datetime.utcnow(),
            last_scraped_at=datetime.utcnow(),
        )
    score = scoring.compute_value_score(listing.__dict__)
    playbook_data = playbook.build_playbook(listing.__dict__)
    return schemas.DealWithScore(
        **listing.__dict__,
        score=schemas.DealScore(
            **score,
            negotiation_playbook=playbook_data,
        ),
    )


@app.post("/alerts", response_model=schemas.Alert)
async def create_alert(
    alert: schemas.AlertCreate,
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_auth),
):
    record = models.Alert(**alert.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.get("/admin/stats", response_model=schemas.AdminStats)
async def admin_stats(
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_auth),
):
    active_count = db.query(models.Listing).filter(models.Listing.listing_status == "active").count()
    job = db.query(models.ScrapeJob).order_by(models.ScrapeJob.id.desc()).first()
    blocked = job.blocked_domains if job and job.blocked_domains else []
    failures = {domain: job.failures for domain in blocked}
    last_updated = job.finished_at if job else None
    logger.info("Admin stats fetched")
    return schemas.AdminStats(
        active_listings=active_count,
        blocked_domains=blocked,
        failures_by_domain=failures,
        last_updated=last_updated,
    )


@app.get("/listings/{listing_id}/comps", response_model=schemas.CompsResponse)
async def get_comps(
    listing_id: str,
    db: Session = Depends(get_db),
    _auth: bool = Depends(require_auth),
):
    listing = db.query(models.Listing).filter(models.Listing.listing_id == listing_id).first()
    if not listing:
        return schemas.CompsResponse(
            listing_id=listing_id,
            comps=[],
            median_discount_percent=0,
            percentile=0,
        )
    msrp_bucket = (listing.msrp or 0) // 10000
    comps = (
        db.query(models.Listing)
        .filter(models.Listing.trim == listing.trim)
        .filter((models.Listing.msrp // 10000) == msrp_bucket)
        .limit(5)
        .all()
    )
    comps_scored = []
    discounts = []
    for comp in comps:
        score = scoring.compute_value_score(comp.__dict__)
        playbook_data = playbook.build_playbook(comp.__dict__)
        discounts.append(score["discount_percent"])
        comps_scored.append(
            schemas.DealWithScore(
                **comp.__dict__,
                score=schemas.DealScore(
                    **score,
                    negotiation_playbook=playbook_data,
                ),
            )
        )
    median_discount = sorted(discounts)[len(discounts) // 2] if discounts else 0
    listing_discount = scoring.compute_value_score(listing.__dict__)["discount_percent"]
    percentile = (
        sum(1 for discount in discounts if discount <= listing_discount) / len(discounts) * 100
        if discounts
        else 0
    )
    return schemas.CompsResponse(
        listing_id=listing_id,
        comps=comps_scored,
        median_discount_percent=median_discount,
        percentile=round(percentile, 2),
    )
