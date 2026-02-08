from __future__ import annotations

from engine.scoring import compute_scores, load_config


def test_scoring_bounds(sample_db):
    config = load_config()
    scores = compute_scores("2024-08-30", config)
    assert scores
    for score in scores:
        assert 0 <= score.TSS <= 10
        assert 0 <= score.FES <= 10
        assert 0 <= score.LMS <= 10
        assert 0 <= score.OS <= 10
        assert 0 <= score.DMS <= 10
        assert 0 <= score.OLS <= 10
