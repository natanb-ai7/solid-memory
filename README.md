# IC Memo Pre-Wire

Production-ready “IC Memo Pre-Wire” system for a Director of Capital Markets at a public REIT with a subordinate CMBS portfolio and active M&A sourcing.

## What it does
- Ingests public + user-provided data (CSV/XLSX/manual inputs).
- Generates a daily one-page memo (HTML/PDF), dashboard, and JSON output.
- Runs a **three-pass validation** (source, calculation, narrative) and blocks output if it fails.

## Repo layout
```
/app            FastAPI web UI (dashboard + memo preview)
/engine         Data ingestion + scoring + memo generation
/tests          Unit + integration tests
/docs           Setup, schemas, workflow guides
/sample_data    Synthetic input data
```

## Quickstart (local)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
prewire ingest
prewire run --date YYYY-MM-DD
```

## Quickstart (Docker)
```bash
docker compose up --build
```
Web UI: http://localhost:8000

## CLI
- `prewire ingest`
- `prewire run --date YYYY-MM-DD`
- `prewire export RUN_ID --format pdf|html|json --output-dir outputs`

## First-run success
```bash
./scripts/first_run.sh
```

## Documentation
- `docs/quickstart.md`
- `docs/data_schema.md`
- `docs/operator_playbook.md`
- `docs/troubleshooting.md`
