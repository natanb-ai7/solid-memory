# solid-memory

Reference deployment assets for the catalog API and collector services.

## Services
- **API (FastAPI)** exposes the normalized make/model/trim catalog.
- **Collector** ingests reference seed data on a schedule and normalizes it into the database.

## Local development
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt -r requirements-dev.txt
   ```
2. Run migrations and seeds locally (SQLite by default):
   ```bash
   DATABASE_URL=sqlite:///./app.db python scripts/migrate.py
   DATABASE_URL=sqlite:///./app.db python scripts/seed_catalog.py
   ```
3. Start the API:
   ```bash
   uvicorn api.main:app --reload
   ```
4. Lint and test:
   ```bash
   ruff check .
   pytest
   ```

## Docker
Build images for each service:
```bash
docker build -f Dockerfile.api -t solid-memory-api .
docker build -f Dockerfile.collector -t solid-memory-collector .
```

Compose stack (includes Postgres, migrations, API, and scheduled collector):
```bash
docker compose up --build
```

## Kubernetes manifests
The `k8s/` directory provides:
- `api-deployment.yaml`: Deployment and Service for the API.
- `collector-cronjob.yaml`: hourly CronJob to refresh the catalog via the collector.
- `migrate-job.yaml`: Job to apply migrations and seed data.
- `postgres.yaml`: simple Postgres Deployment, PVC, and Service.

Apply manifests:
```bash
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/migrate-job.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/collector-cronjob.yaml
```

## CI
GitHub Actions runs linting (ruff) and tests (pytest) on push/PR to ensure migrations, seeds, and services stay healthy.
