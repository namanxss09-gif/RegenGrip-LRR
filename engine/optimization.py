"""Transparent weighted ranking (never hides a failed or pending safety gate) and Pareto dominance."""
from models.validation import validate_weights
from engine.cost_model import recurring_cost

CRR_SCALE_PCT = 20.0   # convention: a 20% Crr reduction scores 10/10 (scaling choice, not physics)

def evidence_strength(c):
    items = [c.crr_evidence == "MEASURED RESULT", c.wet_braking_distance_m is not None and bool(c.wet_evidence_ref.strip()),
             c.wear_life_ratio is not None and bool(c.wear_evidence_ref.strip()),
             c.noise_delta_db is not None and bool(c.noise_evidence_ref.strip()), c.load_index_status == "VERIFIED"]
    return sum(items) / len(items) * 10

def criterion_scores(cands, baseline):
    """Per-candidate dict of criterion -> score or None (missing)."""
    costs = {c.name: recurring_cost(c)["total"] for c in cands}
    known = [v for v in costs.values() if v is not None]
    out = {}
    for c in cands:
        s = {}
        if c.crr is not None and baseline.crr not in (None, 0):
            red = (baseline.crr - c.crr) / baseline.crr * 100
            s["rr_improvement"] = max(0.0, min(10.0, red / CRR_SCALE_PCT * 10))
        else: s["rr_improvement"] = None
        if costs[c.name] is not None and len(known) >= 2:
            lo, hi = min(known), max(known)
            s["cost"] = 10.0 if hi == lo else (hi - costs[c.name]) / (hi - lo) * 10
        else: s["cost"] = None
        s["manufacturing"] = c.score_manufacturing
        s["evidence"] = evidence_strength(c)
        s["technical_risk"] = None if c.score_risk is None else 10 - c.score_risk
        out[c.name] = s
    return out

def rank_candidates(cands, baseline, weights, overall_status):
    """Weighted ranking. Returns (rows, errors). Weights of missing criteria are excluded and renormalised.
    Candidates that are INFEASIBLE get no rank; UNVERIFIED ones are ranked but labelled."""
    errs = validate_weights(weights)
    if errs: return [], errs
    sc = criterion_scores(cands, baseline)
    rows = []
    for c in cands:
        used = {k: w for k, w in weights.items() if sc[c.name][k] is not None and w > 0}
        tw = sum(used.values())
        score = sum(sc[c.name][k] * w for k, w in used.items()) / tw if tw > 0 else None
        rows.append(dict(candidate=c.name, score=score, used=sorted(used), missing=sorted(k for k in weights if sc[c.name][k] is None),
                         status=overall_status[c.name], rank=None, **{f"s_{k}": v for k, v in sc[c.name].items()}))
    elig = sorted([r for r in rows if r["score"] is not None and not r["status"].startswith("INFEASIBLE")], key=lambda r: -r["score"])
    for i, r in enumerate(elig, 1): r["rank"] = i
    return rows, []

def pareto_front(points):
    """points: list of (name, crr, cost); both minimised. Returns {name: 'NON-DOMINATED'|'DOMINATED'}; entries with
    missing values are omitted. A point is dominated if another is <= in both and < in at least one."""
    pts = [(n, a, b) for n, a, b in points if a is not None and b is not None]
    res = {}
    for n, a, b in pts:
        dom = any((a2 <= a and b2 <= b) and (a2 < a or b2 < b) for n2, a2, b2 in pts if n2 != n)
        res[n] = "DOMINATED" if dom else "NON-DOMINATED"
    return res
