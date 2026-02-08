#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install -e .
prewire ingest
prewire run --date "$(date +%F)"
echo "Memo generated in outputs/"
