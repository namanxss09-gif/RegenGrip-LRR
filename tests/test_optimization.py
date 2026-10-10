import pytest
from models.tyre import Candidate, demo_candidates
from models.validation import validate_weights
from engine import optimization as O, feasibility as F
from config.defaults import DEFAULT_CONSTRAINTS, DEFAULT_WEIGHTS

def test_weights_valid_and_invalid():
    assert validate_weights(DEFAULT_WEIGHTS) == []
    assert validate_weights({"a": -0.1, "b": 1.1})
    assert validate_weights({"a": 0.3, "b": 0.3})
    assert validate_weights({"a": 0, "b": 0})
    assert validate_weights({"a": float("nan"), "b": 1})

def test_rank_rejects_bad_weights():
    cs = demo_candidates()
    rows, errs = O.rank_candidates(cs, cs[0], {"rr_improvement": 2}, {c.name: "x" for c in cs})
    assert errs and rows == []

def _wet(cand_d, base_d, ref="LAB-1"):
    b = Candidate(crr=0.012, wet_braking_distance_m=base_d, is_baseline=True)
    c = Candidate(crr=0.0108, wet_braking_distance_m=cand_d, wet_evidence_ref=ref, load_index_status="VERIFIED")
    return F.evaluate(c, b, DEFAULT_CONSTRAINTS)

def _status(res, name): return next(x["status"] for x in res["criteria"] if x["criterion"].startswith(name))

def test_unknown_is_not_pass_and_blocks():
    cs = demo_candidates(); r = F.evaluate(cs[2], cs[0], DEFAULT_CONSTRAINTS)
    assert _status(r, "Wet") == F.UNKNOWN and r["overall"].startswith("UNVERIFIED")

def test_wet_requires_evidence_reference():
    r = _wet(10.0, 10.0, ref="")
    assert _status(r, "Wet") == F.UNKNOWN

def test_wet_fail_overrides_everything():
    r = _wet(11.0, 10.0); assert _status(r, "Wet") == F.FAIL and r["overall"].startswith("INFEASIBLE")

def test_wet_pass_with_evidence():
    assert _status(_wet(10.0, 10.0), "Wet") == F.PASS

def test_high_score_does_not_override_failed_gate():
    cs = demo_candidates(); g = cs[2]; g.wet_braking_distance_m, g.wet_evidence_ref = 12.0, "LAB"; cs[0].wet_braking_distance_m = 10.0
    g.score_manufacturing, g.score_risk = 10, 0
    status = {c.name: F.evaluate(c, cs[0], DEFAULT_CONSTRAINTS)["overall"] for c in cs}
    rows, _ = O.rank_candidates(cs, cs[0], DEFAULT_WEIGHTS, status)
    row = next(r for r in rows if r["candidate"] == g.name)
    assert row["rank"] is None and row["status"].startswith("INFEASIBLE")

def test_load_index_gate():
    c = Candidate(crr=0.0108, load_index_status="FAILED"); b = Candidate(crr=0.012)
    assert _status(F.evaluate(c, b, DEFAULT_CONSTRAINTS), "Load") == F.FAIL

def test_pareto():
    res = O.pareto_front([("A", 0.010, 5), ("B", 0.011, 6), ("C", 0.009, 8), ("D", None, 1)])
    assert res == {"A": "NON-DOMINATED", "B": "DOMINATED", "C": "NON-DOMINATED"}
    assert O.pareto_front([("A", 1, 1), ("B", 1, 1)]) == {"A": "NON-DOMINATED", "B": "NON-DOMINATED"}
