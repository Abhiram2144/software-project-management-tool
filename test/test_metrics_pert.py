import pytest

from src.metrics_engine import (
    calculate_pert,
    calculate_cocomo_I,
    calculate_cocomo_II,
    compute_evm,
)


def test_calculate_pert_basic():
    # example: (1 + 4*4 + 7)/6 = 4
    assert calculate_pert(1, 4, 7) == pytest.approx((1 + 4 * 4 + 7) / 6)


def test_calculate_pert_invalid():
    with pytest.raises(ValueError):
        calculate_pert(-1, 2, 3)
    with pytest.raises(TypeError):
        calculate_pert("a", 2, 3)


def test_cocomo_I_organic_known_behavior():
    small = calculate_cocomo_I(1, model="organic")
    big = calculate_cocomo_I(100, model="organic")
    assert big["effort_person_months"] > small["effort_person_months"]
    assert big["time_months"] > small["time_months"]
    assert small["productivity"] > 0.0


def test_cocomo_I_invalid():
    with pytest.raises(ValueError):
        calculate_cocomo_I(0, model="organic")
    with pytest.raises(ValueError):
        calculate_cocomo_I(10, model="unknown-model")


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
        calculate_cocomo_II(0, {"x": 1}, {"y": 1})
    with pytest.raises(TypeError):
        calculate_cocomo_II(10, {"a": "bad"}, {"b": 1})