"""Three-valued feasibility logic. UNKNOWN is never treated as PASS for safety-critical criteria."""
PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
BASELINE_LABEL = "BASELINE REFERENCE"

def _crit(name, status, detail, safety, evidence):
    return dict(criterion=name, status=status, detail=detail, safety_critical=safety, evidence=evidence)

def evaluate(cand, baseline, constraints):
    """Return dict(criteria=[...], overall=label). Gate checks use only entered, referenced measurements."""
    crit = []
    # Crr target (calculation on a user-entered/hypothetical value)
    if cand.crr is None or baseline.crr in (None, 0):
        crit.append(_crit("Crr reduction vs baseline", UNKNOWN, "Crr or baseline Crr missing", False, "UNAVAILABLE"))
    else:
        red = (baseline.crr - cand.crr) / baseline.crr * 100
        need = constraints.get("min_crr_reduction_pct", 0.0)
        crit.append(_crit("Crr reduction vs baseline", PASS if round(red, 9) >= need else FAIL,
                          f"{red:.2f}% lower (required ≥ {need}%); input evidence: {cand.crr_evidence}", False, cand.crr_evidence))
    # Wet braking (hard gate)
    tol = constraints.get("wet_tolerance_pct", 0.0)
    if cand.wet_braking_distance_m is None or baseline.wet_braking_distance_m is None or not cand.wet_evidence_ref.strip():
        crit.append(_crit("Wet braking non-regression", UNKNOWN, "PENDING — measured baseline and candidate distances plus evidence reference required", True, "UNAVAILABLE"))
    else:
        lim = baseline.wet_braking_distance_m * (1 + tol / 100)
        ok = cand.wet_braking_distance_m <= lim
        crit.append(_crit("Wet braking non-regression", PASS if ok else FAIL,
                          f"{cand.wet_braking_distance_m} m vs limit {lim:.2f} m (ref: {cand.wet_evidence_ref})", True, "MEASURED RESULT"))
    # Load index (hard gate)
    if constraints.get("require_load_index", True):
        s = {"VERIFIED": PASS, "FAILED": FAIL}.get(cand.load_index_status, UNKNOWN)
        crit.append(_crit("Load-index verification", s, f"Status entered: {cand.load_index_status}", True,
                          "USER INPUT" if s != UNKNOWN else "UNAVAILABLE"))
    # Wear
    if cand.wear_life_ratio is None or not cand.wear_evidence_ref.strip():
        crit.append(_crit("Wear non-regression", UNKNOWN, "Measured tread-life ratio and evidence reference missing", False, "UNAVAILABLE"))
    else:
        t = constraints.get("wear_tolerance_pct", 0.0)
        crit.append(_crit("Wear non-regression", PASS if cand.wear_life_ratio >= 1 - t / 100 else FAIL,
                          f"Tread-life ratio {cand.wear_life_ratio} (ref: {cand.wear_evidence_ref})", False, "MEASURED RESULT"))
    # Cost
    mx = constraints.get("max_incremental_cost")
    if mx is not None:
        from engine.cost_model import recurring_cost
        rc = recurring_cost(cand)
        if not rc["complete"]: crit.append(_crit("Incremental cost limit", UNKNOWN, f"Missing: {', '.join(rc['missing'])}", False, "UNAVAILABLE"))
        else: crit.append(_crit("Incremental cost limit", PASS if rc["total"] <= mx else FAIL, f"{rc['total']:.2f} vs max {mx}", False, "USER INPUT"))
    # Manufacturing
    ms = {"VERIFIED": PASS, "FAILED": FAIL}.get(cand.manufacturing_status, UNKNOWN)
    crit.append(_crit("Manufacturing compatibility", ms, f"Status entered: {cand.manufacturing_status}", False, "USER INPUT" if ms != UNKNOWN else "UNAVAILABLE"))
    return dict(criteria=crit, overall=overall(crit, cand.is_baseline and baseline is cand))

def overall(crit, is_ref=False):
    if is_ref: return BASELINE_LABEL
    if any(c["status"] == FAIL for c in crit): return "INFEASIBLE UNDER CURRENT CONSTRAINTS"
    if any(c["status"] == UNKNOWN and c["safety_critical"] for c in crit): return "UNVERIFIED — VALIDATION PENDING"
    if any(c["status"] == UNKNOWN for c in crit): return "ASSUMPTION-BASED"
    return "READY FOR COMPARISON (constraints met on entered evidence; not a safety certification)"

def wet_status(result):
    """Wet-braking status label for display."""
    for c in result["criteria"]:
        if c["criterion"].startswith("Wet"): return {PASS: "PASS on entered evidence", FAIL: "FAIL", UNKNOWN: "PENDING"}[c["status"]]
