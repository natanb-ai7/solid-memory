"""Minimal FastAPI application exposing catalog data."""
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.db import get_session_factory
from shared.models import Make, Model, Trim

app = FastAPI(title="Vehicle Catalog API")


def get_db():
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/healthz")
async def healthcheck():
    return {"status": "ok"}


@app.get("/catalog")
def read_catalog(db: Session = Depends(get_db)):  # noqa: B008 - FastAPI dependency injection
    makes = db.scalars(select(Make).order_by(Make.name)).all()
    if not makes:
        raise HTTPException(status_code=404, detail="Catalog not seeded")

    def serialize_trim(trim: Trim):
        return {"id": trim.id, "name": trim.name}

    def serialize_model(model: Model):
        return {
            "id": model.id,
            "name": model.name,
            "trims": [
                serialize_trim(trim)
                for trim in sorted(model.trims, key=lambda t: t.name)
            ],
        }

    payload = []
    for make in makes:
        payload.append(
            {
                "id": make.id,
                "name": make.name,
                "models": [
                    serialize_model(model)
                    for model in sorted(make.models, key=lambda m: m.name)
                ],
            }
        )

    return payload
