# Data Schema Guide

## Portfolio Positions
Required fields:
- asof_date, cusip, deal_name, tranche, rating, original_balance, current_balance,
  price, spread, wal, property_type_mix, top_msas, servicer, special_servicing_flag,
  watchlist_flag, ara_flag, maturity_bucket, comments

## Funding Terms
- counterparty, asof_date, haircut, spread, advance_rate, margin_call_terms, eligible_assets_rules

## Hedge Book
- instrument, notional, dv01, cs01_proxy, reference_index, entry_level, current_level

## Market Indicators
- indicator, asof_date, value, unit

## M&A Targets CRM
- company, segment, last_touch_date, signal_score_components, notes, owner, next_action, status

## Source pointers
The engine annotates each numeric value with a source pointer using:
- filename + row + column for file uploads
- timestamp captured at ingestion

## File formats
- CSV: preferred for daily runs.
- XLSX: supported via `openpyxl`.

## Example
See `/sample_data` for synthetic CSV templates.
