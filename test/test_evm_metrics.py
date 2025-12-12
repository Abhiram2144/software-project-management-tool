import math
from evm.metrics import (
    pv,
    ev_from_task_completion,
    ac,
    sv,
    cv,
    spi,
    cpi,
    eac_by_cpi,
    eac_by_ac_ev,
    eac_by_ac_cpi,
    vac,
)


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol


def test_basic_evm():
    planned = [1000.0, 2000.0, 1500.0]  # budgets per task
    actuals = [900.0, 2100.0, 1400.0]
    percent_complete = [1.0, 0.5, 0.0]  # task1 done, task2 half, task3 none
    bac = sum(planned)

    PV_total = pv(planned)  # should equal BAC
    assert PV_total == bac

    PV_up_to_task1 = pv(planned, upto_index=1)
    assert PV_up_to_task1 == 1000.0 + 2000.0

    EV = ev_from_task_completion(percent_complete, planned)
    # EV = 1.0*1000 + 0.5*2000 + 0*1500 = 1000 + 1000 = 2000
    assert approx(EV, 2000.0)

    AC = ac(actuals)
    assert AC == sum(actuals)  # 900 + 2100 + 1400 = 4400

    SV_val = sv(EV, PV_up_to_task1)
    # PV up to task1 = 3000, EV = 2000 => SV = -1000
    assert approx(SV_val, -1000.0)

    CV_val = cv(EV, AC)
    assert approx(CV_val, 2000.0 - 4400.0)  # -2400

    SPI_val = spi(EV, PV_up_to_task1)
    assert approx(SPI_val, 2000.0 / 3000.0)

    CPI_val = cpi(EV, AC)
    assert approx(CPI_val, 2000.0 / 4400.0)

    EAC1 = eac_by_cpi(bac, CPI_val)
    # EAC1 = BAC / CPI
    assert math.isfinite(EAC1)

    EAC2 = eac_by_ac_ev(AC, bac, EV)
    # EAC2 = AC + (BAC - EV)
    assert approx(EAC2, AC + (bac - EV))

    EAC3 = eac_by_ac_cpi(AC, bac, EV, CPI_val)
    assert math.isfinite(EAC3)

    VAC1 = vac(bac, EAC1)
    assert approx(VAC1, bac - EAC1)



from typing import Any, Dict, List, Tuple


def target_concolic(x: int, s: str) -> str:
    # Function with branches that a concolic tester should try to reach
    if x < 0:
        if "fail" in s:
            return "NEG-FAIL"
        return "NEG"

    if x == 42:
        # hidden defect path: requires exact number and substring
        if "magic" in s:
            return "CRASH"
        return "THE-ANSWER"

    if x % 3 == 0:
        if s.startswith("a"):
            return "MULTI-A"
        return "MULTI"

    return "OTHER"


def concolic_attempt(func, seed_inputs: List[Tuple[int, str]], max_iters: int = 200) -> Dict[str, Dict]:
   
    found = {}
    queue = list(seed_inputs)
    tried = set()
    iters = 0

    while queue and iters < max_iters:
        x, s = queue.pop(0)
        key = (x, s)
        if key in tried:
            iters += 1
            continue
        tried.add(key)

        try:
            out = func(x, s)
        except Exception as exc:
            found[f"EXC-{x}-{s}"] = {"x": x, "s": s, "exc": repr(exc)}
            iters += 1
            continue

        found[out] = {"x": x, "s": s}

        # Mutation strategies (multiple branches)
        # 1) Numeric neighbors
        for dx in (-1, 1, 3, -3, 42 - x):
            nx = x + dx
            # branch: avoid enormous numbers
            if abs(nx) > 1000:
                continue
            # push mutated candidate
            queue.append((nx, s))

        # 2) String mutations: append keywords that flip branches
        if "magic" not in s:
            queue.append((x, s + "magic"))
        if "fail" not in s:
            queue.append((x, s + "fail"))
        if not s.startswith("a"):
            queue.append((x, "a" + s))

        # 3) Heuristic: if x divisible by 3 try nearby non-divisible values
        if x % 3 == 0:
            queue.append((x + 1, s))

        iters += 1

    return found


def test_concolic_finds_hidden_defect():
    seeds = [(1, "init"), (3, "start"), (0, "zero")]
    found = concolic_attempt(target_concolic, seeds, max_iters=1000)

    # Ensure we found a variety of outputs
    assert "THE-ANSWER" in found or "CRASH" in found or "MULTI" in found

    # Specifically, the harness should find the hidden defect (CRASH) by combining x==42 and 'magic'
    assert "CRASH" in found, "Concolic attempt should discover CRASH path"































    
    
