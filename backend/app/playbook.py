from datetime import datetime
from .scoring import compute_discount_percent


def build_playbook(listing: dict) -> dict:
    msrp = listing.get("msrp") or 0
    price = listing.get("advertised_price") or 0
    discount_percent = compute_discount_percent(msrp, price) * 100
    target_discount = max(discount_percent + 2, 15)
    target_price = msrp * (1 - target_discount / 100) if msrp else price

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "target_selling_price": round(target_price, 2),
        "ask_discount_percent": round(target_discount, 2),
        "messaging": [
            "Please provide a full dealer fee breakdown and confirm whether fees are mandatory.",
            "Confirm money factor, residual, and any lease incentives applicable to my profile.",
            "Can you structure this as $0 due at signing with MSDs instead of cap cost reduction?",
        ],
        "fallback_structure": {
            "zero_due_at_signing": True,
            "msds": True,
        },
    }
