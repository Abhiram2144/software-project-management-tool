import math
import pytest
from src.metrics_engine import calculate_pert, calculate_cocomo_I, calculate_cocomo_II

def test_pert_type_and_value_checks():
    with pytest.raises(TypeError):
        calculate_pert("a", 1, 2)
    with pytest.raises(TypeError):
        calculate_pert(1, object(), 2)
    with pytest.raises(ValueError):
        calculate_pert(-0.1, 1, 2)
    with pytest.raises(ValueError):
        calculate_pert(0.1, -1, 2)

def test_pert_edge_numeric_results():
    assert calculate_pert(0, 0, 0) == pytest.approx(0.0)
    assert calculate_pert(1, 1, 1) == pytest.approx(1.0)

@pytest.mark.parametrize("size,model", [
    (1.0, "organic"),
    (1.0, "semi-detached"),
    (1.0, "embedded"),
    (10.0, "Organic"), 
])
def test_cocomo_I_sanity(size, model):
    out = calculate_cocomo_I(size, model=model)
    assert set(out.keys()) >= {"effort_person_months", "time_months", "staff", "productivity"}
    assert out["effort_person_months"] > 0
    assert out["time_months"] > 0
    
    assert out["staff"] == pytest.approx(out["effort_person_months"] / out["time_months"], rel=1e-6)

def test_cocomo_I_invalid_inputs_and_models():
    with pytest.raises(ValueError):
        calculate_cocomo_I(0.0, model="organic")
    with pytest.raises(TypeError):
        calculate_cocomo_I("ten", model="organic")
    with pytest.raises(ValueError):
        calculate_cocomo_I(10.0, model="unknown-model")

def test_cocomo_II_validation_and_clamping():
    sf = {"PREC": 3.0}
    em = {"M1": 1.0}
    
    out = calculate_cocomo_II(1.0, sf, em)
    assert out["effort_pm"] > 0

    with pytest.raises(ValueError):
        calculate_cocomo_II(1.0, {}, em)
    with pytest.raises(ValueError):
        calculate_cocomo_II(1.0, sf, {})
    
    with pytest.raises(TypeError):
        calculate_cocomo_II(1.0, {"PREC": "bad"}, em)
    extreme_sf = {"S1": 10000.0}
    out2 = calculate_cocomo_II(10.0, extreme_sf, {"M1": 1.0})
    assert math.isfinite(out2["schedule_months"])
    assert out2["schedule_months"] >= 0.0