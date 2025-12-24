import json
from pathlib import Path


def test_seed_file_present():
    seed_path = Path("data/catalog_seed.json")
    assert seed_path.exists(), "Seed file should exist"
    payload = json.loads(seed_path.read_text())
    assert len(payload) >= 3
    assert any(make["make"] == "Toyota" for make in payload)
