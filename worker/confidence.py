def compute_confidence(data: dict) -> float:
    fields = [
        "dealer_name",
        "dealer_state",
        "vin",
        "miles",
        "msrp",
        "advertised_price",
        "trim",
    ]
    present = sum(1 for field in fields if data.get(field))
    return round(present / len(fields), 2)
