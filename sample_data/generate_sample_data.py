from __future__ import annotations

import csv
import random
from datetime import date, timedelta, datetime
from uuid import uuid4

random.seed(7)

SEGMENTS = ["servicing", "analytics", "origination", "special_situations", "data_tech"]

base_date = date(2024, 8, 30)


def write_csv(path, rows, headers):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


targets = []
for i in range(50):
    target_id = str(uuid4())
    targets.append(
        {
            "target_id": target_id,
            "legal_name": f"Synergy Platform {i} LLC",
            "common_name": f"Target {i}",
            "segment": random.choice(SEGMENTS),
            "geography_footprint": "US Nationwide",
            "key_products": "Loan servicing, analytics",
            "key_customers_public": "Public filings",
            "ownership_status": "private",
            "website_url": f"https://target{i}.example.com",
            "last_touch_date": base_date.isoformat(),
            "owner": "REIT Strategy",
            "status": "active_process" if i % 4 == 0 else "sourcing",
            "integration_complexity": random.randint(1, 5),
            "strategic_fit_notes": "Synthetic sample target.",
        }
    )

subscores = []
evidence = []
signals = []

def rand_score():
    return round(random.uniform(4, 9), 2)

for target in targets:
    target_id = target["target_id"]
    evidence_id = str(uuid4())
    evidence.append(
        {
            "evidence_id": evidence_id,
            "target_id": target_id,
            "asof_date": base_date.isoformat(),
            "evidence_type": "manual_note",
            "source_url": "https://example.com/news",
            "file_ref": "",
            "title": f"Coverage note for {target['common_name']}",
            "excerpt": "Synthetic evidence excerpt.",
            "tags": "coverage|sample",
            "confidence": 0.75,
            "created_by": "Analyst",
            "created_at": datetime.utcnow().isoformat(),
        }
    )
    subscores.append(
        {
            "subscore_id": str(uuid4()),
            "target_id": target_id,
            "asof_date": base_date.isoformat(),
            "counterparty_access": rand_score(),
            "collateral_eligibility_lift": rand_score(),
            "haircut_or_term_benefit": rand_score(),
            "surveillance_delta": rand_score(),
            "workout_edge": rand_score(),
            "early_warning_coverage": rand_score(),
            "channel_scale": rand_score(),
            "borrower_overlap": rand_score(),
            "speed_to_close": rand_score(),
            "uniqueness": rand_score(),
            "integration_readiness": rand_score(),
            "contracts_durability": rand_score(),
            "cost_takeout_feasibility": rand_score(),
            "process_redundancy": rand_score(),
            "evidence_ids": evidence_id,
        }
    )
    signals.append(
        {
            "signal_id": str(uuid4()),
            "target_id": target_id,
            "asof_date": base_date.isoformat(),
            "hiring_change_30d": random.randint(-5, 10),
            "news_event_score": round(random.uniform(1, 9), 2),
            "capital_event_flag": random.choice([True, False]),
            "partnership_signal_score": round(random.uniform(1, 9), 2),
            "exec_departure_flag": random.choice([True, False]),
            "customer_concentration_pct": round(random.uniform(10, 60), 2),
            "banker_hired_flag": random.choice([True, False]),
            "litigation_flag": random.choice([True, False]),
            "notes": "Synthetic signals.",
            "evidence_ids": evidence_id,
        }
    )

market_context = [
    {
        "asof_date": base_date.isoformat(),
        "rates_context": "SOFR steady, spreads flat.",
        "sofr_2y": 5.1,
        "sofr_5y": 4.9,
        "sofr_10y": 4.6,
        "cmbx_level_proxy": 102.5,
        "credit_spread_proxy": 1.8,
        "funding_tightness_index": 0.2,
        "evidence_ids": evidence[0]["evidence_id"],
    }
]

write_csv(
    "sample_data/targets.csv",
    targets,
    list(targets[0].keys()),
)
write_csv(
    "sample_data/subscores.csv",
    subscores,
    list(subscores[0].keys()),
)
write_csv(
    "sample_data/evidence.csv",
    evidence,
    list(evidence[0].keys()),
)
write_csv(
    "sample_data/signals.csv",
    signals,
    list(signals[0].keys()),
)
write_csv(
    "sample_data/market_context.csv",
    market_context,
    list(market_context[0].keys()),
)

print("Sample data generated")
