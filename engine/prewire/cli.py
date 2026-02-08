from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

from prewire.export import export_all
from prewire.ingest import (
    ingest_portfolio,
    ingest_funding,
    ingest_hedges,
    ingest_market,
    ingest_ma_targets,
    resolve_dataset_path,
)
from prewire.memo import build_memo
from prewire.scoring import DEFAULT_WEIGHTS
from prewire.storage import RunStorage
from prewire.triggers import evaluate_triggers
from prewire.validators import run_three_pass_validation
from prewire.schemas import MemoOutput

app = typer.Typer(help="IC Memo Pre-Wire CLI")


def _data_dir(data_dir: Optional[Path]) -> Path:
    return data_dir or Path("sample_data")


@app.command()
def ingest(data_dir: Optional[Path] = typer.Argument(None)) -> None:
    base = _data_dir(data_dir)
    _ = ingest_portfolio(resolve_dataset_path(base, "portfolio_positions"))
    _ = ingest_funding(resolve_dataset_path(base, "funding_terms"))
    _ = ingest_hedges(resolve_dataset_path(base, "hedge_book"))
    _ = ingest_market(resolve_dataset_path(base, "market_indicators"))
    _ = ingest_ma_targets(resolve_dataset_path(base, "ma_targets"))
    typer.echo(f"Ingested data from {base.resolve()}")


@app.command()
def run(
    date: str = typer.Option(datetime.utcnow().date().isoformat(), "--date"),
    data_dir: Optional[Path] = typer.Option(None, "--data-dir"),
    output_dir: Path = typer.Option(Path("outputs"), "--output-dir"),
    redact: bool = typer.Option(False, "--redact"),
) -> None:
    base = _data_dir(data_dir)
    positions = ingest_portfolio(resolve_dataset_path(base, "portfolio_positions"))
    funding = ingest_funding(resolve_dataset_path(base, "funding_terms"))
    hedges = ingest_hedges(resolve_dataset_path(base, "hedge_book"))
    market = ingest_market(resolve_dataset_path(base, "market_indicators"))
    ma_targets = ingest_ma_targets(resolve_dataset_path(base, "ma_targets"))
    triggers = evaluate_triggers(positions, funding, hedges)
    memo = build_memo(
        positions, funding, hedges, market, ma_targets, triggers, DEFAULT_WEIGHTS, redaction=redact
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
        typer.echo("Validation failed. Fix-it report:")
        for issue in report.issues:
            typer.echo(f"- [{issue.level}] {issue.message} -> {issue.suggestion}")
        raise typer.Exit(code=1)
    outputs = export_all(memo, output_dir, Path("app/templates"))
    storage = RunStorage(Path("data/prewire.db"))
    storage.log_run(memo.run_id, date, "success", str(outputs["html"]))
    typer.echo(f"Run complete. Outputs: {outputs}")


@app.command()
def export(
    run_id: str = typer.Argument(...),
    output_dir: Path = typer.Option(Path("outputs"), "--output-dir"),
    format: str = typer.Option("pdf", "--format"),
) -> None:
    json_path = output_dir / f"memo_{run_id}.json"
    if not json_path.exists():
        typer.echo("Run output not found.")
        raise typer.Exit(code=1)
    memo_data = json_path.read_text(encoding="utf-8")
    memo = MemoOutput.model_validate_json(memo_data)
    if format == "json":
        typer.echo(json_path.read_text(encoding="utf-8"))
        return
    if format == "html":
        export_all(memo, output_dir, Path("app/templates"))
        typer.echo("HTML exported.")
        return
    export_all(memo, output_dir, Path("app/templates"))
    typer.echo("PDF exported.")


if __name__ == "__main__":
    app()
