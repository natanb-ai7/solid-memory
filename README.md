# Solid Memory

A lightweight FastAPI service that tracks the freshness of upstream data sources and surfaces health, logging, and metrics suitable for Prometheus/OpenTelemetry pipelines.

## Features

- **Source status table** backed by SQLite (configurable via `DATABASE_URL`).
- **Health endpoint** (`/health`) summarizing last successes, parse error rates, and alert conditions for stale or failing sources.
- **Prometheus metrics** exposed at `/metrics` including parse counts, error rates, and stale source gauges.
- **OpenTelemetry tracing and log context** with optional OTLP export via `OTEL_EXPORTER_OTLP_ENDPOINT`.

## Running locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Key endpoints

- `POST /sources` – register a new source `{ "source_name": "foo" }`.
- `POST /sources/{source_name}/parse` – report a parse attempt `{ "success": true, "notes": "optional" }`.
- `GET /sources` – list known sources and their last attempts.
- `GET /health` – returns combined freshness/parse error alerts.
- `GET /metrics` – Prometheus exposition format for scraping.

### Alert thresholds

- Parse error rate threshold: `PARSE_ERROR_RATE_THRESHOLD` (default `0.2`).
- Stale window for last success: `STALE_THRESHOLD_HOURS` (default `24`).

Prometheus alerting rules can target `parse_error_rate` and `stale_source_total` gauges emitted per source.
