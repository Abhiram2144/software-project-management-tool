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