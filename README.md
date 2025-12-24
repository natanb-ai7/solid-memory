# solid-memory

## API

A lightweight FastAPI service lives in `api/` with endpoints:

- `GET /programs/latest` – latest program release, optional `zip_code` to include region.
- `GET /programs/history` – historical program releases, optional `zip_code` to include region.
- `GET /makes` – supported makes, optional `zip_code` to include region.
- `GET /models` – supported models, optional `make` filter and `zip_code` for region info.
- `GET /health` – health check.

Requests require either an `X-API-Key` header (default `demo-key`) or `Authorization: Bearer <jwt>` signed with `JWT_SECRET` (default `demo-secret`). Basic rate limiting (30/minute per key) protects the endpoints.

### Running locally

```bash
pip install -r requirements.txt
API_KEYS=demo-key JWT_SECRET=demo-secret uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

