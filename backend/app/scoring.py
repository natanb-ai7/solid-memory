from .config import settings

TRIM_BASELINES = {
    "eDrive50": 105000,
    "xDrive60": 120000,
    "M70": 145000,
}


DEFAULT_WEIGHTS = {
    "discount_percent": 0.5,
    "miles": 0.2,
    "trim_baseline": 0.1,
    "incentives": 0.1,
    "lease_quality": 0.1,
}


def compute_discount_percent(msrp: float | None, price: float | None) -> float:
    if not msrp or not price:
        return 0.0
    return max((msrp - price) / msrp, 0.0)


def score_miles(miles: int | None) -> float:
    if miles is None:
        return 0.3
    if miles <= 5000:
        return 1.0
    if miles <= 10000:
        return 0.7
    if miles <= 15000:
        return 0.4
    return 0.1


def score_trim(trim: str | None) -> float:
    if not trim:
        return 0.5
    baseline = TRIM_BASELINES.get(trim, 120000)
    return baseline / max(TRIM_BASELINES.values())


def score_incentives(incentives: list[dict] | None) -> float:
    if not incentives:
        return 0.2
    stackable = any(item.get("stackable") for item in incentives)
    total = sum(item.get("amount", 0) for item in incentives)
    base = min(total / 10000, 1.0)
    return base + (0.2 if stackable else 0.0)


def score_lease_quality(lease_terms: dict | None) -> float:
    if not lease_terms:
        return 0.2
    due_at_signing = lease_terms.get("due_at_signing") or 0
    payment = lease_terms.get("payment") or 0
    score = 1.0
    if due_at_signing > 3000:
        score -= 0.3
    if payment > 1500:
        score -= 0.3
    return max(score, 0.1)


def compute_value_score(listing: dict, weights: dict | None = None) -> dict:
    weights = weights or DEFAULT_WEIGHTS
    discount_percent = compute_discount_percent(listing.get("msrp"), listing.get("advertised_price"))
    components = {
        "discount_percent": discount_percent,
        "miles": score_miles(listing.get("miles")),
        "trim_baseline": score_trim(listing.get("trim")),
        "incentives": score_incentives(listing.get("incentives")),
        "lease_quality": score_lease_quality(listing.get("lease_terms")),
    }
    score = sum(components[key] * weights[key] for key in weights)
    return {
        "score": round(score, 4),
        "discount_percent": round(discount_percent * 100, 2),
        "value_components": components,
    }
