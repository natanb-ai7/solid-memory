# Troubleshooting

## Auditability validator fails
- Ensure every numeric input has an evidence object with confidence >= 0.6.
- Add evidence links in `evidence_ids` and re-run `./synergy run`.

## Calculation validator fails
- Verify weights in `engine/config/defaults.yaml` sum to ~1.0.
- Ensure subscore values are between 0 and 10.

## Narrative validator fails
- Update top levers/risks to include a metric or tag as `QUALITATIVE`.

## PDF export fails
- Ensure WeasyPrint system dependencies are installed.
- In Docker, use the provided image which includes required libraries.
