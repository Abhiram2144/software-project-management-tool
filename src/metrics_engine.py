from typing import Dict, Optional
import numbers


__all__ = [
    "calculate_pert",
    "calculate_cocomo_I",
    "calculate_cocomo_II",
]


def _is_number(value) -> bool:
    return isinstance(value, numbers.Real)


def calculate_pert(optimistic: float, likely: float, pessimistic: float) -> float:
    """
    Calculate expected time using the PERT formula.

    Inputs:
    - optimistic: float (O) - must be numeric and >= 0
    - likely: float (M) - must be numeric and >= 0
    - pessimistic: float (P) - must be numeric and >= 0

    Returns:
    - expected time as float using formula (O + 4*M + P) / 6

    Raises:
    - TypeError: if any input is not numeric
    - ValueError: if any input is negative
    """
    for name, v in (("optimistic", optimistic), ("likely", likely), ("pessimistic", pessimistic)):
        if not _is_number(v):
            raise TypeError(f"{name} must be numeric")
        if v < 0:
            raise ValueError(f"{name} must be non-negative")

    expected = (optimistic + 4 * likely + pessimistic) / 6.0
    return float(expected)




    def calculate_cocomo_I(size_kloc: float, model: str = "organic") -> Dict[str, float]:
    """
    Basic COCOMO I estimator.

    Inputs:
    - size_kloc: float - size of the project in KLOC (kilo-lines of code). Must be > 0.
    - model: str - one of "organic", "semi-detached", "embedded" (case-insensitive).
      Defaults to "organic".

    Returns:
    - dict with keys:
      {
        "effort_person_months": float,
        "time_months": float,
        "staff": float,
        "productivity": float
      }

    Coefficients used (classic Basic COCOMO):
    - Organic:         a = 2.4, b = 1.05, c = 2.5, d = 0.38
    - Semi-Detached:   a = 3.0, b = 1.12, c = 2.5, d = 0.35
    - Embedded:        a = 3.6, b = 1.20, c = 2.5, d = 0.32

    Equations:
    - Effort (PM) = a * (KLOC ^ b)
    - Time (months) = c * (Effort ^ d)
    - Staff = Effort / Time
    - Productivity = KLOC / Effort

    Raises:
    - TypeError: if size_kloc is not numeric
    - ValueError: if size_kloc <= 0 or model unknown
    """
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




    def calculate_cocomo_II(
    size_kloc: float,
    scale_factors: Dict[str, float],
    effort_multipliers: Dict[str, float],
    *,
    A: float = 2.94,
    B: float = 0.91,
) -> Dict[str, object]:
    """
    Simplified COCOMO II estimator (lightweight).

    Inputs:
    - size_kloc: float - size in KLOC, must be > 0
    - scale_factors: dict of scale factor names to numeric values (expected several factors).
      Example keys: "PREC","FLEX","RESL","TEAM","PMAT" (this lightweight version accepts any numeric set).
    - effort_multipliers: dict of effort multiplier names to numeric factors (EAF multipliers).
      EAF is the product of all effort_multipliers.

    Optional kwargs:
    - A: calibration constant (default 2.94)
    - B: baseline exponent constant (default 0.91)

    Returns:
    - dict:
      {
        "effort_pm": float,
        "schedule_months": float,
        "details": {
            "A": float,
            "B": float,
            "E": float,
            "EAF": float,
            "scale_factors": {...},
            "effort_multipliers": {...}
        }
      }

    Simplified model used (documented):
    - E = B + 0.01 * sum(scale_factors.values())
    - EAF = product(effort_multipliers.values())
    - Effort (person-months) = A * (Size^E) * EAF
    - Schedule (months) = 3.67 * (Effort ^ (0.28 + 0.2 * (E - B)))

    Validation:
    - Raises TypeError if size_kloc not numeric or SF/EM values non-numeric
    - Raises ValueError if size_kloc <= 0 or scale/effort dicts are empty
    """
    if not _is_number(size_kloc):
        raise TypeError("size_kloc must be numeric")
    if size_kloc <= 0:
        raise ValueError("size_kloc must be greater than 0")
    if not isinstance(scale_factors, dict) or not scale_factors:
        raise ValueError("scale_factors must be a non-empty dict")
    if not isinstance(effort_multipliers, dict) or not effort_multipliers:
        raise ValueError("effort_multipliers must be a non-empty dict")

    for k, v in scale_factors.items():
        if not _is_number(v):
            raise TypeError(f"scale_factors['{k}'] must be numeric")
    for k, v in effort_multipliers.items():
        if not _is_number(v):
            raise TypeError(f"effort_multipliers['{k}'] must be numeric")

    sum_sf = sum(float(v) for v in scale_factors.values())
    E = B + 0.01 * sum_sf
    eaf = 1.0
    for v in effort_multipliers.values():
        eaf *= float(v)

    effort_pm = A * (size_kloc ** E) * eaf

    schedule_exponent = 0.28 + 0.2 * (E - B)
    schedule_exponent = max(-1.0, min(2.0, schedule_exponent))
    schedule_months = 3.67 * (effort_pm ** schedule_exponent) if effort_pm > 0 else 0.0

    return {
        "effort_pm": float(effort_pm),
        "schedule_months": float(schedule_months),
        "details": {
            "A": float(A),
            "B": float(B),
            "E": float(E),
            "EAF": float(eaf),
            "scale_factors": dict(scale_factors),
            "effort_multipliers": dict(effort_multipliers),
        },
    }