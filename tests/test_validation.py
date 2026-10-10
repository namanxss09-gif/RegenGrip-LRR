import pytest
from engine import validation_planner as V, sensitivity as S
from models.vehicle import Vehicle

def test_complete_requires_result_and_reference():
    t = V.default_tests()[0]
    with pytest.raises(ValueError): V.complete_test(t, "", "ref", True)
    with pytest.raises(ValueError): V.complete_test(t, "ok", "  ", True)
    assert V.complete_test(t, "ok", "DOC-1", True)["passed"] is True

def test_stage_gates():
    tests = V.default_tests()
    assert V.stage_gate(tests, 0)["allowed"]
    g = V.stage_gate(tests, 3); assert not g["allowed"] and g["reasons"]
    for t in tests:
        if t["stage"] < 3 and t["safety_critical"]: tests[tests.index(t)] = V.complete_test(t, "r", "e", True)
    assert V.stage_gate(tests, 3)["allowed"]
    wet = next(i for i, t in enumerate(tests) if t["name"] == "Wet braking")
    tests[wet] = V.complete_test(tests[wet], "worse", "e", False)
    g = V.stage_gate(tests, 3); assert not g["allowed"] and "FAILED" in g["reasons"][0]

def test_all_required_test_categories_present():
    names = " ".join(t["name"] for t in V.default_tests()).lower()
    for k in ["dynamic mechanical", "rolling-resistance", "wet braking", "tread wear", "endurance", "dynamic growth", "noise", "thermal", "ageing", "manufacturing consistency", "energy-per-distance"]:
        assert k in names

def test_oat_and_scenarios():
    v = Vehicle()
    t = S.oat_table(v, 0.012, 0.0108, 10)
    top = t.iloc[0]["parameter"]; assert top in ("Candidate Crr", "Baseline Crr", "Total operating mass")
    sp = t[t.parameter == "Speed"].iloc[0]; assert sp["swing"] == pytest.approx(0)   # rolling saving independent of speed in this model
    sc = S.scenarios(v, 0.012, 0.0108, {"total_mass": 0.9}, {"total_mass": 1.1})
    assert sc.loc["low", "rr_saving_wh"] < sc.loc["base", "rr_saving_wh"] < sc.loc["high", "rr_saving_wh"]
