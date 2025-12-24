# solid-memory

A lightweight collector service for pulling OEM brochures, dealer HTML pages, and JSON API feeds on a scheduled cadence.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure sources in `sources.yaml`. Each entry includes OEM, brand, region, format, cadence, and auth metadata.

## Running collectors

Run the scheduler locally to execute collectors based on cadence:

```bash
python collector_service.py
```

Collectors respect `robots.txt` and apply per-host rate limiting to avoid overwhelming upstream systems.
