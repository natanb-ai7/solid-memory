import pytest

from normalization.catalog import Catalog, DEFAULT_CATALOG


def test_fuzzy_trim_match():
    catalog = DEFAULT_CATALOG
    normalized = catalog.normalize("Toyota", "RAV4", "Prime xse")
    assert normalized.trim == "prime xse"
    assert normalized.score > 0.3


def test_unknown_model_adds_low_score():
    catalog = Catalog({"Brand": {"Model": ["Base"]}})
    normalized = catalog.normalize("Brand", "UnknownModel", "Base")
    assert normalized.model == "unknownmodel"
    assert normalized.score < 1
