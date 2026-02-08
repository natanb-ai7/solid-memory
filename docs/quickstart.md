# Quickstart

## Local (Python)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

# One-command demo
./synergy demo

# Start API/UI
uvicorn app.main:app --reload
```

## Docker
```bash
docker compose up --build
```

Visit http://localhost:8000 for the UI.

## First-run success
```bash
./synergy demo
```
This ingests `sample_data/`, runs scoring for 2024-08-30, and exports HTML/PDF/JSON to `./outputs`.
