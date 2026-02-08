from __future__ import annotations

from engine.run import run_daily
from engine.scoring import load_config
from engine.validators import run_validators


def test_validators_return(sample_db):
    run_daily("2024-08-30")
    config = load_config()
    results = run_validators("2024-08-30", config)
    assert "auditability" in results
    assert "calculation" in results
