import pytest
from src.metrics_engine import compute_evm_metrics

def test_blackbox_evm_nominal():
    planned_values = [100, 200]
    tasks = [
        {'planned': 100, 'percent_complete': 1.0},
        {'planned': 200, 'percent_complete': 0.5}
    ]
    actual_costs = [110, 90]
    bac = 1000

    metrics = compute_evm_metrics(planned_values, tasks, actual_costs, bac=bac, eac_method='cpi')

    assert metrics['PV'] == 300
    assert metrics['EV'] == 200
    assert metrics['AC'] == 200
    assert metrics['SV'] == -100
    assert metrics['CV'] == 0
    assert metrics['SPI'] == pytest.approx(200 / 300)
    assert metrics['CPI'] == pytest.approx(1.0)
    assert metrics['EAC'] == pytest.approx(1000.0)
    assert metrics['VAC'] == pytest.approx(0.0)

def test_blackbox_evm_zero_divisions_and_none_indices():
    planned_values = []
    tasks = [{'planned': 0, 'percent_complete': 0.0}]
    actual_costs = []
    metrics = compute_evm_metrics(planned_values, tasks, actual_costs, bac=None)

    assert metrics['PV'] == 0
    assert metrics['EV'] == 0
    assert metrics['AC'] == 0
    assert metrics['SV'] == 0
    assert metrics['CV'] == 0
    assert metrics['SPI'] is None
    assert metrics['CPI'] is None
    assert metrics['EAC'] is None
    assert metrics['VAC'] is None

def test_blackbox_eac_methods_behavior():
    planned_values = [100, 150]
    tasks = [
        {'planned': 100, 'percent_complete': 1.0},
        {'planned': 150, 'percent_complete': 0.5}
    ]
    actual_costs = [110, 80]
    bac = 1000

    m_cpi = compute_evm_metrics(planned_values, tasks, actual_costs, bac=bac, eac_method='cpi')
    m_ac_plus = compute_evm_metrics(planned_values, tasks, actual_costs, bac=bac, eac_method='ac_plus_remaining')
    m_ac_ev_cpi = compute_evm_metrics(planned_values, tasks, actual_costs, bac=bac, eac_method='ac_ev_cpi')

    ev = m_cpi['EV']
    ac = m_cpi['AC']
    cpi = m_cpi['CPI']

    assert cpi is not None
    assert m_cpi['EAC'] == pytest.approx(bac / cpi)
    assert m_ac_plus['EAC'] == pytest.approx(ac + (bac - ev))
    assert m_ac_ev_cpi['EAC'] == pytest.approx(ac + (bac - ev) / cpi)