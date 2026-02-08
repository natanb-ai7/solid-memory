# Quickstart

## Local run (first time)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
prewire ingest
prewire run --date YYYY-MM-DD
```

## Docker
```bash
docker compose up --build
```

Visit:
- Web UI: http://localhost:8000

## First-run success script
```bash
./scripts/first_run.sh
```
