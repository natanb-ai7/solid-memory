# Integration Synergy Strategy Tracker (Codex)

Production-ready system for tracking M&A integration synergies for a REIT with subordinate CMBS exposure and capital markets constraints. Designed for daily, auditable scorecards built from public data and user-provided inputs.

## Key Guarantees
- **No proprietary data**: Only public sources + user uploads/manual entries.
- **Auditability**: Every numeric value must link to evidence (URL/file/manual entry with timestamp).
- **Validation gates**: Final exports blocked when auditability fails.

## Architecture
- **/app**: FastAPI + server-rendered templates
- **/engine**: ingestion, scoring, rules, validators, exports
- **/tests**: unit + integration + snapshot tests
- **/docs**: setup, schema, operator playbook, troubleshooting
- **/sample_data**: synthetic CSV inputs

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
./synergy demo
uvicorn app.main:app --reload
```

## Docker
```bash
docker compose up --build
```

## CLI
- `./synergy ingest <file_or_dir>`
- `./synergy run --date YYYY-MM-DD`
- `./synergy export --format pdf|html|json --scope target|daily_brief --date YYYY-MM-DD --target-id <uuid>`
- `./synergy validate --date YYYY-MM-DD`

## Docs
See `docs/quickstart.md`, `docs/schema.md`, `docs/operator_playbook.md`, `docs/troubleshooting.md`.
