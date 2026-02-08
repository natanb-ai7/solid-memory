# Troubleshooting

## Validation fails
- Ensure every file has required columns.
- Confirm timestamps are current (market data <24 hours).
- Make sure risk score weights sum to ~1.0.

## PDF export issues
- WeasyPrint requires system libraries (Pango, Cairo). Use Docker to avoid local issues.

## Missing data
- The memo will show “MISSING” and suggest minimal next data steps.
