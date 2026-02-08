from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader

from engine.db import get_connection, init_db
from engine.scoring import load_config

app = FastAPI(title="Integration Synergy Strategy Tracker")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


env = Environment(loader=FileSystemLoader("app/templates"), autoescape=True)


def _render(template_name: str, **context) -> HTMLResponse:
    template = env.get_template(template_name)
    return HTMLResponse(template.render(**context))


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    conn = get_connection()
    rows = conn.execute(
        "SELECT t.common_name, t.segment, t.status, s.* FROM scoring s JOIN targets t ON s.target_id = t.target_id ORDER BY s.TSS DESC"
    ).fetchall()
    conn.close()
    return _render("dashboard.html", scores=rows)


@app.get("/targets", response_class=HTMLResponse)
def targets():
    conn = get_connection()
    rows = conn.execute(
        "SELECT t.common_name, t.segment, t.status, s.* FROM scoring s JOIN targets t ON s.target_id = t.target_id ORDER BY s.TSS DESC"
    ).fetchall()
    conn.close()
    return _render("targets.html", scores=rows)


@app.get("/targets/{target_id}", response_class=HTMLResponse)
def target_detail(target_id: str):
    conn = get_connection()
    target = conn.execute("SELECT * FROM targets WHERE target_id = ?", (target_id,)).fetchone()
    scores = conn.execute(
        "SELECT * FROM scoring WHERE target_id = ? ORDER BY asof_date DESC LIMIT 30",
        (target_id,),
    ).fetchall()
    evidence = conn.execute(
        "SELECT * FROM evidence WHERE target_id = ? ORDER BY asof_date DESC", (target_id,)
    ).fetchall()
    conn.close()
    return _render(
        "target_detail.html", target=target, scores=scores, evidence=evidence
    )


@app.get("/daily-brief", response_class=HTMLResponse)
def daily_brief():
    conn = get_connection()
    scores = conn.execute(
        "SELECT t.common_name, t.segment, s.* FROM scoring s JOIN targets t ON s.target_id = t.target_id ORDER BY s.TSS DESC"
    ).fetchall()
    market = conn.execute("SELECT * FROM market_context ORDER BY asof_date DESC LIMIT 1").fetchone()
    conn.close()
    return _render("daily_brief.html", scores=scores, market=market, asof_date="latest")


@app.get("/evidence", response_class=HTMLResponse)
def evidence():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM evidence ORDER BY asof_date DESC").fetchall()
    conn.close()
    return _render("evidence.html", evidence=rows)


@app.get("/config", response_class=HTMLResponse)
def config_page():
    config = load_config()
    return _render("config.html", config=config)


@app.get("/runs", response_class=HTMLResponse)
def run_history():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM run_history ORDER BY created_at DESC").fetchall()
    conn.close()
    return _render("runs.html", runs=rows)
