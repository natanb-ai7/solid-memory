# i7 Loaner Deal Scanner

Production-ready web app to scan BMW i7 loaner listings in the Southeast, normalize deal terms, rank negotiation leverage, and surface direct dealer VDP links.

## Architecture
- **Backend:** FastAPI for typed, high-performance APIs. (Chosen for rapid schema validation and async-friendly I/O.)
- **Worker:** RQ + Redis for job queue, modular source adapters, and rate-limited scraping.
- **Storage:** Postgres for listings and alerts; Redis for queue.
- **Frontend:** Next.js + Tailwind for dashboard, detail drawer, and playbooks.

## Quick start
```bash
cp .env.example .env

docker compose up --build
```

Run migrations:
```bash
docker compose exec backend alembic upgrade head
```

Visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

## Environment variables
| Variable | Description | Default |
| --- | --- | --- |
| DATABASE_URL | Postgres connection string | postgresql+psycopg://solid:solid@postgres:5432/solid |
| REDIS_URL | Redis connection string | redis://redis:6379/0 |
| SINGLE_USER_MODE | Enables single-user auth bypass | true |
| AUTH_SECRET | Secret for auth tokens | dev-secret |
| REQUEST_RATE_LIMIT_S | Per-domain request spacing | 1.0 |
| GLOBAL_CONCURRENCY | Worker concurrency | 4 |

## Data sources (modular adapters)
- Dealer sites (inventory/VDP pages)
- Aggregator pages (discovery then follow dealer VDP)
- Search results (query-based discovery)
- Manual URL add

Adapters live in `worker/adapters/` and share a `discover()`, `scrape_listing()`, `normalize()` interface.

## Scoring model
- **Discount %** = (MSRP - advertised price) / MSRP
- **Value score** weights:
  - Discount % (highest weight)
  - Mileage (penalize >10k)
  - Trim baseline buckets
  - Incentive stacking
  - Lease structure quality

**Best setup definition:** maximize discount %, incentives, and transparency while keeping miles low and listings recently seen. See `backend/app/scoring.py`.

Negotiation playbooks include target selling price, discount ask, fee/MF/residual requests, and $0 DAS vs MSD fallback.

## Alerts
Configure alert thresholds (Discount %, miles, price, state) via the API. Matching listings are queued for email notification.

## Admin page
Use `/admin/stats` for scrape job status, blocked domains, and failures.

## Comps
Use `/listings/{listing_id}/comps` to fetch 5 nearest comps (trim + MSRP bucket) plus median discount and percentile rank.

## Testing
```bash
cd backend
pytest
```

## How to add a new source adapter
1. Create a new class in `worker/adapters/` implementing `SourceAdapter`.
2. Implement:
   - `discover()` to return listing URLs.
   - `scrape_listing()` to fetch content (respect `robots.txt` via `worker/robots.py`).
   - `normalize()` to map fields into the listing schema.
3. Register the adapter in `worker/main.py`.
4. Add parsing unit tests with HTML fixtures in `backend/tests/fixtures/`.

## How to adjust scoring weights
Open `backend/app/scoring.py` and update `DEFAULT_WEIGHTS` or trim baselines in `TRIM_BASELINES`.

## Screenshots
Placeholder UI is shipped via Tailwind components. Replace with real screenshots after running the frontend.

## Running with clawdbot
If your clawdbot can run shell commands in a repo, share this repository with it and have it execute:

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

Then point it at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs

If clawdbot expects a single startup command, use:

```bash
docker compose up --build
```
