# solid-memory

A lightweight scraping orchestrator with per-source safety controls and data lineage logging.

## Features

- **Robots.txt enforcement**: Every source checks its robots.txt rules before fetching.
- **Rate limiting and backoff**: Configure per-source request budgets and retry windows.
- **Feature flags**: Toggle individual sources on/off without code changes.
- **Changelog logging**: Append fetch metadata (source, URL, parser version, timestamp, status) to `data/changelog.jsonl`.

## Usage

Run the default collector sources:

```bash
python -m solid_memory.main
```

The default configuration lives in `solid_memory.main.DEFAULT_SOURCES`. Update or replace it with your own `SourceConfig` instances to control:

- `rate_limit`: `requests` per `per_seconds` window.
- `backoff`: `initial_seconds`, `max_seconds`, and `max_attempts` for retrying transient failures.
- `enabled`: flip to `False` to disable a source quickly.

Each execution appends entries to `data/changelog.jsonl`, providing a durable log of source URL, fetch time, parser version, and outcome.
