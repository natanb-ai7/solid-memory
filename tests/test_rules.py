from __future__ import annotations

from engine.rules import next_best_actions
from engine.scoring import load_config


def test_accelerate_rule(sample_db):
    config = load_config()
    score_row = {
        "target_id": "unknown",
        "asof_date": "2024-08-30",
        "TSS": 8.0,
        "drift_5d": 0.6,
        "score_confidence_pct": 75,
        "FES": 7.0,
    }
    actions = next_best_actions(score_row, config)
    assert any("Schedule principal call" in action["action"] for action in actions)
