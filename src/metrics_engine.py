from typing import List
import numbers

__all__ = ["calculate_pert"]

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
