from __future__ import annotations

import json
from pathlib import Path

import typer

from engine.db import init_db
from engine.exporter import export_daily_brief, export_json, export_target_scorecard
from engine.ingest import ingest_directory, ingest_file
from engine.run import run_daily
from engine.validators import run_validators
from engine.scoring import load_config

app = typer.Typer(help="Integration Synergy Strategy Tracker CLI")


@app.command()
def ingest(path: Path):
    """Ingest CSV or Excel files."""
    if path.is_dir():
        ingest_directory(path)
    else:
        ingest_file(path)
    typer.echo(f"Ingested data from {path}")


@app.command()
def run(date: str = typer.Option(..., "--date")):
    """Run scoring for a given date (YYYY-MM-DD)."""
    result = run_daily(date)
    typer.echo(json.dumps({"run_id": result["run_id"], "status": result["status"]}, indent=2))


@app.command()
def validate(date: str = typer.Option(..., "--date")):
    """Run validators for a given date."""
    config = load_config()
    results = run_validators(date, config)
    payload = {key: result.status for key, result in results.items()}
    typer.echo(json.dumps(payload, indent=2))


@app.command()
def export(
    format: str = typer.Option(..., "--format"),
    scope: str = typer.Option(..., "--scope"),
    date: str = typer.Option(..., "--date"),
    target_id: str = typer.Option("", "--target-id"),
    final: bool = typer.Option(True, "--final/--draft"),
    redact: bool = typer.Option(False, "--redact/--no-redact"),
):
    """Export scorecards, briefs, or JSON."""
    if format == "json":
        path = export_json(date, target_id=target_id or None, redact=redact)
        typer.echo(str(path))
        return

    if scope == "target":
        if not target_id:
            raise typer.BadParameter("target_id is required for target scope")
        path = export_target_scorecard(date, target_id, fmt=format, final=final, redact=redact)
    elif scope == "daily_brief":
        path = export_daily_brief(date, fmt=format, final=final, redact=redact)
    else:
        raise typer.BadParameter("scope must be target|daily_brief")
    typer.echo(str(path))


@app.command()
def demo():
    """One-command demo: ingest sample data, run scoring, export outputs."""
    init_db()
    ingest_directory(Path("sample_data"))
    demo_date = "2024-08-30"
    run_daily(demo_date)
    export_daily_brief(demo_date, fmt="html", final=False)
    export_daily_brief(demo_date, fmt="pdf", final=False)
    export_json(demo_date)
    typer.echo("Demo complete. Outputs in ./outputs")


if __name__ == "__main__":
    app()
