from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app import models
from app.scoring import compute_value_score
from app.playbook import build_playbook


def test_end_to_end_insert_and_score():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    db = SessionLocal()
    listing = models.Listing(
        listing_id="abc123",
        source="dealer_site",
        dealer_vdp_url="https://example.com/vdp",
        model="BMW i7",
        msrp=120000,
        advertised_price=102000,
        miles=4200,
        is_loaner=True,
    )
    db.add(listing)
    db.commit()

    saved = db.query(models.Listing).first()
    score = compute_value_score(saved.__dict__)
    playbook = build_playbook(saved.__dict__)

    assert score["score"] > 0
    assert playbook["target_selling_price"] > 0
