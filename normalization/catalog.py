"""
Catalog-driven normalization utilities.

The catalog contains a reference set of makes, models, and trims and performs
fuzzy matching to align messy scraped data to canonical entries.
"""
from dataclasses import dataclass
from difflib import get_close_matches
from typing import Dict, Iterable, Tuple


@dataclass
class NormalizedVehicle:
    make: str
    model: str
    trim: str
    score: float


class Catalog:
    """Simple in-memory catalog for vehicle normalization."""

    def __init__(self, reference: Dict[str, Dict[str, Iterable[str]]]):
        self.reference = {
            make.lower(): {model.lower(): {trim.lower() for trim in trims} for model, trims in models.items()}
            for make, models in reference.items()
        }

    def _normalize_make(self, make: str) -> Tuple[str, float]:
        candidates = list(self.reference.keys())
        match = get_close_matches(make.lower(), candidates, n=1, cutoff=0.6)
        if match:
            return match[0], 1.0
        return make.lower(), 0.0

    def _normalize_model(self, make_key: str, model: str) -> Tuple[str, float]:
        models = list(self.reference.get(make_key, {}).keys())
        match = get_close_matches(model.lower(), models, n=1, cutoff=0.65)
        if match:
            return match[0], 1.0
        return model.lower(), 0.0

    def _normalize_trim(self, make_key: str, model_key: str, trim: str) -> Tuple[str, float]:
        trims = list(self.reference.get(make_key, {}).get(model_key, []))
        match = get_close_matches(trim.lower(), trims, n=1, cutoff=0.4)
        if match:
            return match[0], 1.0
        return trim.lower(), 0.0

    def normalize(self, make: str, model: str, trim: str) -> NormalizedVehicle:
        """Normalize incoming values against the reference catalog."""

        make_key, make_score = self._normalize_make(make)
        model_key, model_score = self._normalize_model(make_key, model)
        trim_key, trim_score = self._normalize_trim(make_key, model_key, trim)

        average_score = (make_score + model_score + trim_score) / 3
        return NormalizedVehicle(make=make_key, model=model_key, trim=trim_key, score=average_score)


DEFAULT_CATALOG = Catalog(
    {
        "Toyota": {
            "RAV4": ["LE", "XLE", "Limited", "Prime XSE"],
            "Camry": ["SE", "XSE", "LE"],
        },
        "Honda": {
            "Accord": ["LX", "EX-L", "Touring"],
            "CR-V": ["EX", "Sport-L", "Touring"],
        },
    }
)
