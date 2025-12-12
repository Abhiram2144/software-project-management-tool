from typing import Dict, Any
import numbers

__all__ = [
    "calculate_pert",
    "calculate_cocomo_I",
    "calculate_cocomo_II",
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

def calculate_cocomo_II(
    size_kloc: float,
    scale_factors: Dict[str, float],
    effort_multipliers: Dict[str, float],
    *,
    A: float = 2.94,
    B: float = 0.91,
) -> Dict[str, Any]:
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


from typing import Iterable, Dict, Optional

def compute_pv(planned_values: Iterable[float]) -> float:
    return float(sum(planned_values))

def compute_ev(tasks: Iterable[Dict]) -> float:
    total = 0.0
    for t in tasks:
        if 'earned_value' in t and t['earned_value'] is not None:
            total += float(t['earned_value'])
        else:
            planned = float(t.get('planned', 0.0))
            pc = float(t.get('percent_complete', 0.0))
            total += planned * pc
    return total

def compute_ac(actual_costs: Iterable[float]) -> float:
    return float(sum(actual_costs))

def compute_variances_and_indices(pv: float, ev: float, ac: float) -> Dict[str, Optional[float]]:
    sv = ev - pv
    cv = ev - ac
    spi = (ev / pv) if pv else None
    cpi = (ev / ac) if ac else None
    return {'SV': sv, 'CV': cv, 'SPI': spi, 'CPI': cpi}

def compute_eac(bac: float, ac: float, ev: float, cpi: Optional[float], method: str = 'cpi') -> Optional[float]:
    if method == 'cpi':
        if cpi and cpi > 0:
            return bac / cpi
        return None
    if method == 'ac_plus_remaining':
        return ac + (bac - ev)
    if method == 'ac_ev_cpi':
        if cpi and cpi > 0:
            return ac + (bac - ev) / cpi
        return None
    return None

def compute_vac(bac: float, eac: Optional[float]) -> Optional[float]:
    return (bac - eac) if (eac is not None) else None

def compute_evm_metrics(
    planned_values: Iterable[float],
    tasks: Iterable[Dict],
    actual_costs: Iterable[float],
    bac: Optional[float] = None,
    eac_method: str = 'cpi'
) -> Dict[str, Optional[float]]:
    pv = compute_pv(planned_values)
    ev = compute_ev(tasks)
    ac = compute_ac(actual_costs)
    vi = compute_variances_and_indices(pv, ev, ac)
    eac = None
    vac = None
    if bac is not None:
        eac = compute_eac(bac, ac, ev, vi.get('CPI'), method=eac_method)
        vac = compute_vac(bac, eac)
    return {
        'PV': pv, 'EV': ev, 'AC': ac,
        **vi,
        'EAC': eac,
        'VAC': vac
    }
