# Operator Playbook (10–15 minute daily routine)

1. **Ingest new data** (2–3 min)
   - Upload CSV/XLSX files or use the UI forms.
   - Command: `./synergy ingest path/to/file_or_dir`

2. **Run daily scoring** (2 min)
   - Command: `./synergy run --date YYYY-MM-DD`

3. **Check auditability** (1 min)
   - Command: `./synergy validate --date YYYY-MM-DD`
   - If any checks fail, review the Fix-It report in `outputs/`.

4. **Review dashboard + action queue** (3–5 min)
   - Visit `/` and `/daily-brief`.

5. **Export deliverables** (2–3 min)
   - HTML/PDF/JSON exports: `./synergy export --format pdf --scope daily_brief --date YYYY-MM-DD`

## Next Best Action routing
- Use the Daily Brief action queue and assign owners within the UI.
