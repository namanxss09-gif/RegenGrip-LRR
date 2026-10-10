import pytest
from models.tyre import Candidate
from engine import cost_model as C

def cand(**kw): return Candidate(**kw)

def test_recurring_sum_and_separation():
    c = cand(material_cost=10, processing_cost=2, scrap_cost=1, qc_cost=0.5, tooling_cost=1000, testing_dev_cost=500)
    assert C.recurring_cost(c)["total"] == 13.5 and C.one_time_cost(c)["total"] == 1500
    assert C.program_cost(c, 100) == 1500 + 13.5 * 100

def test_missing_stays_missing():
    c = cand(material_cost=10)
    r = C.recurring_cost(c)
    assert r["total"] is None and r["partial"] == 10 and not r["complete"] and len(r["missing"]) == 3
    assert C.program_cost(c, 100) is None and C.completeness(c) == pytest.approx(1 / 6)

def test_zero_is_not_missing():
    assert C.recurring_cost(cand(material_cost=0, processing_cost=0, scrap_cost=0, qc_cost=0))["total"] == 0

def test_break_even():
    c = cand(material_cost=3, processing_cost=1, scrap_cost=0.5, qc_cost=0.5, tooling_cost=1000, testing_dev_cost=500)
    assert C.break_even_volume(c, 10) == pytest.approx(1500 / 5)
    assert C.break_even_volume(c, 5) is None          # zero margin
    assert C.break_even_volume(c, 2) is None          # negative margin
    assert C.break_even_volume(c, None) is None
    assert C.break_even_volume(cand(material_cost=1), 10) is None

def test_cost_per_improvement_requires_measured():
    base = Candidate(crr=0.012)
    c = cand(crr=0.0108, crr_evidence="TARGET", material_cost=1, processing_cost=1, scrap_cost=0, qc_cost=0)
    assert C.cost_per_pct_improvement(c, base) is None
    c.crr_evidence = "MEASURED RESULT"
    assert C.cost_per_pct_improvement(c, base) == pytest.approx(2 / 10)
