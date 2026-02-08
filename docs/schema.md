# Schema Guide

All numeric fields require an auditable citation (URL, file+sheet+cell, or manual entry with timestamp).

## CSV Templates

### targets.csv
- target_id (uuid)
- legal_name
- common_name
- segment (servicing|analytics|origination|special_situations|data_tech|other)
- geography_footprint
- key_products
- key_customers_public
- ownership_status (private|public|subsidiary|unknown)
- website_url
- last_touch_date
- owner
- status (sourcing|diligence|active_process|paused|dead)
- integration_complexity (1-5)
- strategic_fit_notes

### evidence.csv
- evidence_id (uuid)
- target_id
- asof_date
- evidence_type (url|upload|manual_note)
- source_url (nullable)
- file_ref (filename, sheet, cell_range)
- title
- excerpt (<=500 chars)
- tags (pipe-delimited)
- confidence (0-1)
- created_by
- created_at

### signals.csv
- signal_id (uuid)
- target_id
- asof_date
- hiring_change_30d
- news_event_score
- capital_event_flag
- partnership_signal_score
- exec_departure_flag
- customer_concentration_pct
- banker_hired_flag
- litigation_flag
- notes
- evidence_ids (pipe-delimited)

### market_context.csv
- asof_date
- rates_context
- sofr_2y, sofr_5y, sofr_10y
- cmbx_level_proxy
- credit_spread_proxy
- funding_tightness_index
- evidence_ids (pipe-delimited)

### subscores.csv
- subscore_id
- target_id
- asof_date
- counterparty_access
- collateral_eligibility_lift
- haircut_or_term_benefit
- surveillance_delta
- workout_edge
- early_warning_coverage
- channel_scale
- borrower_overlap
- speed_to_close
- uniqueness
- integration_readiness
- contracts_durability
- cost_takeout_feasibility
- process_redundancy
- evidence_ids (pipe-delimited)
