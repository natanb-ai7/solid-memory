# OpenClaw Grafana + Prometheus Monitoring Stack

Production-lean monitoring stack for OpenClaw with strict bloat/cost controls and no AI/background recommendation features.

## Quick start

```bash
docker-compose up -d
```

Run from this folder:

```bash
cd grafana-monitoring
docker-compose up -d
```

## URLs

- Grafana: http://localhost:3000
- Grafana (via nginx subpath): http://localhost:8443/grafana/
- Prometheus: http://localhost:9090
- Prometheus (via nginx subpath): http://localhost:8443/prometheus/
- Loki API: http://localhost:3100

## First step after startup

Change Grafana admin password from the default `admin/admin`.

## Pinned versions

This stack uses pinned tags only:

- `grafana/grafana:10.4.5`
- `prom/prometheus:v2.51.2`
- `prom/node-exporter:v1.7.0`
- `nginx:1.25.4-alpine`
- `grafana/loki:2.9.6`
- `grafana/promtail:2.9.6`
- exporter base: `python:3.11.8-slim`

## Bloat and cost controls

- No per-session labels or high-cardinality labels in Prometheus.
- Exporter labels are hard-capped to top-N model/provider values; overflow is aggregated into `other`.
- Prometheus scrape interval is 30s.
- Prometheus retention is 30d.
- Loki retention is 7d (`168h`) with minimal filesystem single-node config.
- Promtail ships only `nginx` error logs. Access logs are intentionally excluded to reduce noise.
- Docker log rotation on every service: `max-size=10m`, `max-file=3`.
- Exporter enforces `MAX_FILE_MB` and refuses oversized files, increments parse error counter, and continues serving last good values.

## Exporter notes

The exporter reads `SESSIONS_JSON` and inspects runtime structure without fabricating missing fields.

If these fields are absent in your `sessions.json`, related metrics remain `0`:

- API calls: `api_calls`, `call_count`, `requests`
- input tokens: `input_tokens`, `prompt_tokens`
- output tokens: `output_tokens`, `completion_tokens`
- cost: `cost`, `cost_dollars`
- context bytes: `context_bytes`
- active sessions: `sessions` list length or `active_sessions`
- cron jobs active: `cron_jobs_active`

## Alerting

Grafana Unified Alerting is enabled in `grafana.ini`.

Recommended minimal alert rules:

1. **Prometheus target down**
   - Query: `up == 0`
   - For: `2m`
2. **Exporter parse errors increasing**
   - Query: `increase(openclaw_exporter_parse_errors_total[10m]) > 0`
3. **Disk usage critical**
   - Query: `(1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes{fstype!~"tmpfs|overlay"})) * 100 > 90`
   - For: `5m`
4. **Projected monthly spend exceeds threshold**
   - Query: `((sum(increase(openclaw_cost_dollars_total[7d])) / 7) * 30) > 500`

To change spend threshold, edit the constant in query from `500` to your budget.

### Contact points without committing secrets

Configure contact points via environment variables at runtime (example shell exports):

```bash
export SMTP_HOST="smtp.example.com:587"
export SMTP_USER="alerts@example.com"
export SMTP_PASSWORD="***"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

Then create one Grafana contact point with those values in the UI once; do not commit secret values.

## Validation checklist

- `docker-compose config` validates.
- Prometheus targets include `node-exporter` and `openclaw-exporter`.
- Grafana auto-provisions Prometheus + Loki datasources and dashboard JSON files.
- Grafana works under `http://localhost:8443/grafana/`.
- Exporter exposes no per-session metric labels.
- Poll interval default `10s`, scrape interval `30s`.
- Loki retention set to `7d`; promtail excludes access logs.
- Alert rules are defined above for minimal setup.

## Troubleshooting

- **Prometheus target health**: open `http://localhost:9090/targets`.
- **Exporter parsing issues**: inspect `openclaw_exporter_parse_errors_total`.
- **Mount permissions**: verify `${HOME}/.openclaw/agents/main/sessions/` is readable by Docker.
- **Grafana subpath problems**: confirm nginx proxy is serving `/grafana/` and Grafana `root_url` includes `/grafana/`.
- **Loki ingestion**: check `http://localhost:3100/ready` and verify `promtail` container logs.

## Security note

Anonymous Viewer mode and embedding are enabled for convenience. Restrict network exposure and disable anonymous access for untrusted environments.
