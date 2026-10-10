"""Scenario assembly and the single compute_all() used by UI, database and report (reproducibility)."""
from datetime import datetime
from config.defaults import *
from models.vehicle import Vehicle
from models.tyre import Candidate
from engine import energy, feasibility, optimization, cost_model

def build_scenario(name, vehicle, candidates, baseline_name, constraints, weights, program, sens, tests, checklist):
    return dict(name=name, created=datetime.now().isoformat(timespec="seconds"), app_version=APP_VERSION,
                vehicle=vehicle.to_dict() if hasattr(vehicle, "to_dict") else dict(vehicle),
                candidates=[c.to_dict() if hasattr(c, "to_dict") else dict(c) for c in candidates],
                baseline_name=baseline_name, constraints=dict(constraints), weights=dict(weights),
                program=dict(program), sens=dict(sens), tests=list(tests), checklist=list(checklist))

def compute_all(sc):
    """Deterministically recompute every result from the scenario dict."""
    veh = Vehicle.from_dict(sc["vehicle"])
    cands = [Candidate.from_dict(c) for c in sc["candidates"]]
    base = next((c for c in cands if c.name == sc["baseline_name"]), cands[0])
    res = dict(vehicle_errors=veh.validate()[0], vehicle_warnings=veh.validate()[1], per_candidate={}, baseline=base.name)
    status = {}
    for c in cands:
        feas = feasibility.evaluate(c, base, sc["constraints"])
        if c is not base and c.name == base.name: pass
        feas["overall"] = feasibility.BASELINE_LABEL if c is base else feas["overall"]
        status[c.name] = feas["overall"]
        e = None
        if not res["vehicle_errors"] and c.crr is not None and base.crr is not None:
            e = energy.candidate_vs_baseline(veh, base.crr, c.crr)
        rc, oc = cost_model.recurring_cost(c), cost_model.one_time_cost(c)
        vol = sc["program"].get("volume")
        res["per_candidate"][c.name] = dict(
            energy=e, feasibility=feas, recurring=rc, one_time=oc, cost_completeness=cost_model.completeness(c),
            program_cost=cost_model.program_cost(c, vol),
            break_even=cost_model.break_even_volume(c, sc["program"].get("benefit_per_tyre")),
            crr=c.crr, crr_evidence=c.crr_evidence)
    rows, errs = optimization.rank_candidates(cands, base, sc["weights"], status)
    res["ranking"], res["weight_errors"] = rows, errs
    res["pareto"] = optimization.pareto_front([(c.name, c.crr, cost_model.recurring_cost(c)["total"]) for c in cands])
    return res
