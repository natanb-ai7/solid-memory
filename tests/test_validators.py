from prewire.validators import validate_calculations


def test_validate_calculations_weight_sum():
    report = validate_calculations({"a": 0.6, "b": 0.6})
    assert not report.passed
