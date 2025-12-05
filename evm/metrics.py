from typing import Iterable, List, Optional


def pv(planned_values: Iterable[float], upto_index: Optional[int] = None) -> float:
    """
    Compute Planned Value (PV).
    - planned_values: sequence of planned budget values (per task or per time period).
    - upto_index: if None, sum all planned values (PV = BAC); otherwise sum from index 0..upto_index inclusive.
    """
    pv_list = list(planned_values)
    if upto_index is None:
        return sum(pv_list)
    if upto_index < 0:
        return 0.0
    return sum(pv_list[: upto_index + 1])


def ev_from_task_completion(percent_complete: Iterable[float], budget_per_task: Iterable[float]) -> float:
    """
    Compute Earned Value (EV) from percent complete per task and budget per task.
    Both sequences must be same length. percent_complete contains values in range [0,1].
    EV = sum(percent * budget_for_task)
    """
    pc = list(percent_complete)
    budget = list(budget_per_task)
    if len(pc) != len(budget):
        raise ValueError("percent_complete and budget_per_task must have same length")
    return sum(max(0.0, min(1.0, p)) * b for p, b in zip(pc, budget))


def ac(actual_costs: Iterable[float]) -> float:
    """
    Compute Actual Cost (AC) as sum of actual costs.
    """
    return sum(actual_costs)


def sv(ev_value: float, pv_value: float) -> float:
    """
    Schedule Variance: SV = EV - PV
    """
    return ev_value - pv_value


def cv(ev_value: float, ac_value: float) -> float:
    """
    Cost Variance: CV = EV - AC
    """
    return ev_value - ac_value


def spi(ev_value: float, pv_value: float) -> float:
    """
    Schedule Performance Index: SPI = EV / PV (guard against division by zero).
    """
    if pv_value == 0:
        return float("inf") if ev_value > 0 else 0.0
    return ev_value / pv_value


def cpi(ev_value: float, ac_value: float) -> float:
    """
    Cost Performance Index: CPI = EV / AC (guard against division by zero).
    """
    if ac_value == 0:
        return float("inf") if ev_value > 0 else 0.0
    return ev_value / ac_value


# Common Estimate At Completion (EAC) formulas
def eac_by_cpi(bac: float, cpi_value: float) -> float:
    """
    EAC assuming future cost performance will be same as past (EAC = BAC / CPI).
    If CPI is zero, returns infinity.
    """
    if cpi_value == 0:
        return float("inf")
    return bac / cpi_value


def eac_by_ac_ev(ac_value: float, bac: float, ev_value: float) -> float:
    """
    EAC assuming remaining work will be performed at planned rate:
    EAC = AC + (BAC - EV)
    """
    return ac_value + (bac - ev_value)


def eac_by_ac_cpi(ac_value: float, bac: float, ev_value: float, cpi_value: float) -> float:
    """
    EAC assuming remaining work will continue at same cost performance as so far:
    EAC = AC + (BAC - EV) / CPI
    If CPI is zero, returns infinity.
    """
    if cpi_value == 0:
        return float("inf")
    return ac_value + (bac - ev_value) / cpi_value


def vac(bac: float, eac_value: float) -> float:
    """
    Variance At Completion: VAC = BAC - EAC
    """
    return bac - eac_value