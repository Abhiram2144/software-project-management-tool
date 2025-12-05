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