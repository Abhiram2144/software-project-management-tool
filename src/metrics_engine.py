from typing import Dict
import numbers

__all__ = [
    "calculate_pert",
    "calculate_cocomo_I",
]

def _is_number(value) -> bool:
    return isinstance(value, numbers.Real) and not isinstance(value, bool)

def calculate_pert(optimistic: float, likely: float, pessimistic: float) -> float:
    for name, v in (("optimistic", optimistic), ("likely", likely), ("pessimistic", pessimistic)):
        if not _is_number(v):
            raise TypeError(f"{name} must be numeric")
        if v < 0:
            raise ValueError(f"{name} must be non-negative")
    expected = (optimistic + 4 * likely + pessimistic) / 6.0
    return float(expected)

def calculate_cocomo_I(size_kloc: float, model: str = "organic") -> Dict[str, float]:
    if not _is_number(size_kloc):
        raise TypeError("size_kloc must be numeric")
    if size_kloc <= 0:
        raise ValueError("size_kloc must be greater than 0")

    model_key = model.strip().lower()
    coeffs = {
        "organic": (2.4, 1.05, 2.5, 0.38),
        "semi-detached": (3.0, 1.12, 2.5, 0.35),
        "semidetached": (3.0, 1.12, 2.5, 0.35),
        "embedded": (3.6, 1.20, 2.5, 0.32),
    }

    if model_key not in coeffs:
        raise ValueError(f"unknown model '{model}', expected one of: organic, semi-detached, embedded")

    a, b, c, d = coeffs[model_key]
    effort = a * (size_kloc ** b)
    time_months = c * (effort ** d)
    staff = effort / time_months if time_months != 0 else float("inf")
    productivity = size_kloc / effort if effort != 0 else 0.0

    return {
        "effort_person_months": float(effort),
        "time_months": float(time_months),
        "staff": float(staff),
        "productivity": float(productivity),
    }
