from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import csv
import json

from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from prewire.export import export_all
from prewire.ingest import (
    ingest_portfolio,
    ingest_funding,
    ingest_hedges,
    ingest_market,
    ingest_ma_targets,
    validate_schema,
    REQUIRED_COLUMNS,
    resolve_dataset_path,
)
from prewire.memo import build_memo
from prewire.scoring import DEFAULT_WEIGHTS
from prewire.storage import RunStorage
from prewire.triggers import evaluate_triggers
from prewire.validators import run_three_pass_validation

app = FastAPI(title="IC Memo Pre-Wire")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
storage = RunStorage(Path("data/prewire.db"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    runs = storage.list_runs()
    return templates.TemplateResponse("index.html", {"request": request, "runs": runs})


@app.get("/upload", response_class=HTMLResponse)
def upload_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/manual", response_class=HTMLResponse)
def manual_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("manual.html", {"request": request})


@app.post("/manual")
def manual_entry(dataset: str = Form(...), payload: str = Form(...)) -> RedirectResponse:
    dataset_map = {
        "portfolio_positions": "portfolio_positions.csv",
        "funding_terms": "funding_terms.csv",
        "hedge_book": "hedge_book.csv",
        "market_indicators": "market_indicators.csv",
        "ma_targets": "ma_targets.csv",
    }
    if dataset not in dataset_map:
        return RedirectResponse("/manual", status_code=302)
    file_path = UPLOAD_DIR / dataset_map[dataset]
    record = json.loads(payload)
    write_header = not file_path.exists()
    with file_path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(record.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(record)
    return RedirectResponse("/", status_code=302)


@app.post("/upload")
async def upload_data(
    request: Request,
    portfolio: Optional[UploadFile] = None,
    funding: Optional[UploadFile] = None,
    hedge: Optional[UploadFile] = None,
    market: Optional[UploadFile] = None,
    ma_targets: Optional[UploadFile] = None,
) -> HTMLResponse:
    files = {
        "portfolio_positions": portfolio,
        "funding_terms": funding,
        "hedge_book": hedge,
        "market_indicators": market,
        "ma_targets": ma_targets,
    }
    issues = []
    for name, file in files.items():
        if file:
            data = await file.read()
            suffix = Path(file.filename or "").suffix or ".csv"
            file_path = UPLOAD_DIR / f"{name}{suffix}"
            file_path.write_bytes(data)
            missing = validate_schema(file_path, REQUIRED_COLUMNS[name])
            if missing:
                issues.append(f"{name}: missing columns {', '.join(missing)}")
    if issues:
        return templates.TemplateResponse(
            "run.html",
            {
                "request": request,
                "status": "failed",
                "issues": [
                    {"level": "error", "message": issue, "suggestion": "Update file columns."}
                    for issue in issues
                ],
            },
        )
    return RedirectResponse("/", status_code=302)


@app.post("/run")
def run_today(
    request: Request,
    data_dir: Optional[str] = Form(None),
    redaction: Optional[bool] = Form(False),
) -> HTMLResponse:
    base = Path(data_dir) if data_dir else Path("sample_data")
    positions = ingest_portfolio(resolve_dataset_path(base, "portfolio_positions"))
    funding = ingest_funding(resolve_dataset_path(base, "funding_terms"))
    hedges = ingest_hedges(resolve_dataset_path(base, "hedge_book"))
    market = ingest_market(resolve_dataset_path(base, "market_indicators"))
    ma_targets = ingest_ma_targets(resolve_dataset_path(base, "ma_targets"))
    triggers = evaluate_triggers(positions, funding, hedges)
    memo = build_memo(
        positions,
        funding,
        hedges,
        market,
        ma_targets,
        triggers,
        DEFAULT_WEIGHTS,
        redaction=bool(redaction),
    )
    report = run_three_pass_validation(
        positions,
        funding,
        hedges,
        market,
        DEFAULT_WEIGHTS,
        memo,
        triggers,
    )
    if not report.passed:
        return templates.TemplateResponse(
            "run.html", {"request": request, "status": "failed", "issues": report.issues}
        )
    outputs = export_all(memo, OUTPUT_DIR, Path("app/templates"))
    storage.log_run(
        memo.run_id,
        datetime.utcnow().isoformat(),
        "success",
        str(outputs["html"]),
    )
    return templates.TemplateResponse(
        "run.html", {"request": request, "status": "success", "outputs": outputs}
    )


@app.get("/memo/{run_id}", response_class=HTMLResponse)
def memo_view(request: Request, run_id: str) -> HTMLResponse:
    html_path = OUTPUT_DIR / f"memo_{run_id}.html"
    if not html_path.exists():
        return templates.TemplateResponse(
            "run.html", {"request": request, "status": "missing", "issues": []}
        )
    return HTMLResponse(html_path.read_text(encoding="utf-8"))
