from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, Query

from .auth import require_auth
from .rate_limit import DEFAULT_LIMITER, rate_limit
from .region import lookup_region

app = FastAPI(title="Solid Memory API")

# Sample in-memory data for demonstration.
PROGRAM_HISTORY: List[Dict[str, Any]] = [
    {"id": "prog-001", "name": "Memory Booster", "version": "1.0.0", "released": "2023-05-01"},
    {"id": "prog-002", "name": "Memory Booster", "version": "1.1.0", "released": "2023-09-15"},
    {"id": "prog-003", "name": "Memory Booster", "version": "1.2.0", "released": "2024-03-30"},
]

MAKES = ["Acme", "Contoso", "Globex", "Initech"]
MODELS = [
    {"id": "model-001", "make": "Acme", "name": "Aurora"},
    {"id": "model-002", "make": "Contoso", "name": "Nimbus"},
    {"id": "model-003", "make": "Globex", "name": "Pulse"},
    {"id": "model-004", "make": "Initech", "name": "Summit"},
]


def _apply_rate_limit(subject: str) -> None:
    rate_limit(subject, DEFAULT_LIMITER)


@app.get("/programs/latest")
def get_latest_program(
    user: str = Depends(require_auth),
    zip_code: Optional[str] = Query(None, description="ZIP code to localize response"),
):
    _apply_rate_limit(user)
    latest = PROGRAM_HISTORY[-1]
    response = {"program": latest}
    if zip_code:
        response["region"] = lookup_region(zip_code)
    return response


@app.get("/programs/history")
def get_program_history(
    user: str = Depends(require_auth),
    zip_code: Optional[str] = Query(None, description="ZIP code to localize response"),
):
    _apply_rate_limit(user)
    response = {"programs": PROGRAM_HISTORY}
    if zip_code:
        response["region"] = lookup_region(zip_code)
    return response


@app.get("/makes")
def list_makes(
    user: str = Depends(require_auth),
    zip_code: Optional[str] = Query(None, description="ZIP code to localize response"),
):
    _apply_rate_limit(user)
    response = {"makes": MAKES}
    if zip_code:
        response["region"] = lookup_region(zip_code)
    return response


@app.get("/models")
def list_models(
    make: Optional[str] = Query(None, description="Filter by make name"),
    user: str = Depends(require_auth),
    zip_code: Optional[str] = Query(None, description="ZIP code to localize response"),
):
    _apply_rate_limit(user)
    models = [m for m in MODELS if make is None or m["make"].lower() == make.lower()]
    response = {"models": models}
    if zip_code:
        response["region"] = lookup_region(zip_code)
    return response


@app.get("/health")
def healthcheck():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

