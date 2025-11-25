import pytest
from src.metrics_engine import calculate_cocomo_II


def test_cocomo_II_basic():
    size = 50.0
    sf = {"PREC": 3.0, "FLEX": 2.0, "RESL": 3.0, "TEAM": 2.0, "PMAT": 3.0}
    em = {"RELY": 1.0, "DATA": 1.1, "CPLX": 0.9}
    out = calculate_cocomo_II(size, sf, em)
    assert "effort_pm" in out and "schedule_months" in out and "details" in out
    assert out["effort_pm"] > 0
    assert "E" in out["details"] and "EAF" in out["details"]


def test_cocomo_II_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_cocomo_II(0.0, {"x": 1}, {"y": 1})
    with pytest.raises(TypeError):
        calculate_cocomo_II(10.0, {"a": "bad"}, {"b": 1})


def test_cocomo_II_schedule_exponent_edge():
    # craft SFs so E is large; ensure function returns a non-negative schedule_months (clamped exponent)
    sf = {"S1": 1000.0}
    em = {"M1": 1.0}
    out = calculate_cocomo_II(10.0, sf, em)
    assert "schedule_months" in out
    assert out["schedule_months"] >= 0.0