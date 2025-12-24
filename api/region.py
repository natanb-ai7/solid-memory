from functools import lru_cache
from typing import Dict, List, Tuple

# Mapping of ZIP code ranges to USPS state abbreviations.
_ZIP_STATE_RANGES: List[Tuple[int, int, str]] = [
    (35000, 36999, "AL"),
    (99500, 99999, "AK"),
    (85000, 86999, "AZ"),
    (71600, 72999, "AR"),
    (90000, 96699, "CA"),
    (80000, 81699, "CO"),
    (6000, 6999, "CT"),
    (19700, 19999, "DE"),
    (32000, 34999, "FL"),
    (30000, 31999, "GA"),
    (96700, 96899, "HI"),
    (50000, 52999, "IA"),
    (83200, 83999, "ID"),
    (60000, 62999, "IL"),
    (46000, 47999, "IN"),
    (66000, 67999, "KS"),
    (40000, 42799, "KY"),
    (70000, 71599, "LA"),
    (3900, 4999, "ME"),
    (20600, 21999, "MD"),
    (1000, 2799, "MA"),
    (48000, 49999, "MI"),
    (55000, 56899, "MN"),
    (38600, 39799, "MS"),
    (63000, 65999, "MO"),
    (59000, 59999, "MT"),
    (27000, 28999, "NC"),
    (58000, 58899, "ND"),
    (68000, 69999, "NE"),
    (88900, 89999, "NV"),
    (3000, 3899, "NH"),
    (7000, 8999, "NJ"),
    (87000, 88499, "NM"),
    (8899, 14999, "NY"),
    (43000, 45999, "OH"),
    (73000, 74999, "OK"),
    (97000, 97999, "OR"),
    (15000, 19699, "PA"),
    (300, 999, "PR"),
    (2800, 2999, "RI"),
    (29000, 29999, "SC"),
    (57000, 57799, "SD"),
    (37000, 38599, "TN"),
    (75000, 79999, "TX"),
    (88500, 88599, "TX"),
    (84000, 84999, "UT"),
    (5000, 5999, "VT"),
    (20100, 20199, "VA"),
    (22000, 24699, "VA"),
    (20000, 20099, "DC"),
    (98000, 99499, "WA"),
    (24700, 26899, "WV"),
    (53000, 54999, "WI"),
    (82000, 83199, "WY"),
]

# Regions from U.S. Census Bureau definitions.
_STATE_REGION: Dict[str, str] = {
    "CT": "Northeast",
    "ME": "Northeast",
    "MA": "Northeast",
    "NH": "Northeast",
    "RI": "Northeast",
    "VT": "Northeast",
    "NJ": "Northeast",
    "NY": "Northeast",
    "PA": "Northeast",
    "IL": "Midwest",
    "IN": "Midwest",
    "MI": "Midwest",
    "OH": "Midwest",
    "WI": "Midwest",
    "IA": "Midwest",
    "KS": "Midwest",
    "MN": "Midwest",
    "MO": "Midwest",
    "NE": "Midwest",
    "ND": "Midwest",
    "SD": "Midwest",
    "DE": "South",
    "FL": "South",
    "GA": "South",
    "MD": "South",
    "NC": "South",
    "SC": "South",
    "VA": "South",
    "DC": "South",
    "WV": "South",
    "AL": "South",
    "KY": "South",
    "MS": "South",
    "TN": "South",
    "AR": "South",
    "LA": "South",
    "OK": "South",
    "TX": "South",
    "AZ": "West",
    "CO": "West",
    "ID": "West",
    "MT": "West",
    "NV": "West",
    "NM": "West",
    "UT": "West",
    "WY": "West",
    "AK": "West",
    "CA": "West",
    "HI": "West",
    "OR": "West",
    "WA": "West",
    "PR": "Territory",
}

@lru_cache(maxsize=512)
def lookup_region(zip_code: str) -> str:
    """
    Convert a ZIP code string to a U.S. region name.

    The lookup uses an LRU cache to speed up repeated queries for popular
    ZIP codes.
    """
    normalized = zip_code.strip()
    if not normalized.isdigit():
        raise ValueError("ZIP code must be numeric")

    numeric_zip = int(normalized)
    for start, end, state in _ZIP_STATE_RANGES:
        if start <= numeric_zip <= end:
            return _STATE_REGION.get(state, "Unknown")
    raise KeyError(f"ZIP code {zip_code} not found in mapping")

