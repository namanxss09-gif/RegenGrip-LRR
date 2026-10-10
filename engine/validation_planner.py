"""Staged validation plan and stage gates."""
STAGES = {0: "Research and input verification", 1: "Compound screening", 2: "Prototype tyre laboratory testing",
          3: "Instrumented vehicle testing", 4: "Durability and ageing", 5: "Pilot manufacturing consistency",
          6: "Commercial qualification readiness"}
NS = "TO BE SELECTED AND VERIFIED WITH TEST LAB (no standard edition verified here)"

def _t(stage, name, obj, inputs, equip, unit, crit, safety, proc):
    return dict(stage=stage, name=name, objective=obj, baseline="Baseline reference tyre, same conditions", required_inputs=inputs,
                equipment=equip, method=NS, procedure=proc, units=unit, acceptance=crit, safety_critical=safety,
                evidence_status="NOT STARTED", result="", evidence_ref="", passed=None, owner="TBD", next_action="Define method with lab")

def default_tests():
    return [
        _t(0, "Input verification (baseline Crr, tyre size, load index, pressure)", "Replace illustrative inputs with sourced values",
           "Vehicle spec, baseline test data, dossier", "Document review", "n/a", "All inputs sourced; no ILLUSTRATIVE tags remain", True, "Collect and cite sources"),
        _t(1, "Dynamic mechanical analysis (DMA)", "Screen compound viscoelastic behaviour", "Compound samples", "DMA instrument / lab",
           "tan δ, E′ vs T", "Defined by team vs baseline compound", False, "Temperature/strain sweep on baseline and candidate compounds"),
        _t(2, "Rolling-resistance testing", "Measure Crr of prototype vs baseline", "Prototype tyres, baseline tyres", "RR drum machine",
           "Crr (dimensionless)", "Target: ≥10% lower than baseline (NOT VALIDATED)", False, "Same load, pressure, speed, temperature for both"),
        _t(2, "Wet braking", "Verify no regression vs baseline", "Prototype & baseline tyres, test vehicle/track", "Wet-surface braking facility",
           "Braking distance (m) / deceleration (m/s²)", "No worse than baseline (hard gate)", True, "Repeat runs, same surface/speed/load"),
        _t(2, "Tread wear", "Compare wear rate", "Prototype & baseline", "Wear test rig / road trial", "mm/1000 km or index",
           "No worse than baseline (target)", False, "Matched duty cycle"),
        _t(2, "Load and speed endurance", "Verify structural durability at rated load/speed", "Prototype tyres", "Endurance drum",
           "Pass/fail, hours", "Defined by applicable method (to verify)", True, "Staged load/speed steps"),
        _t(2, "Dynamic growth and structural integrity", "Check dimensional growth and integrity", "Prototype tyres", "Growth measurement / inspection",
           "mm, pass/fail", "Defined by applicable method (to verify)", True, "Measure outer dimensions before/after"),
        _t(2, "Noise and vibration", "Measure noise change", "Prototype & baseline", "Noise test facility", "dB(A)",
           "Target: reduction (requires measurement)", False, "Internal method unless standard verified"),
        _t(3, "Thermal behaviour", "Check running temperature", "Instrumented prototype", "Thermocouple/IR instrumentation", "°C",
           "Defined by team", False, "Instrumented vehicle run"),
        _t(3, "On-vehicle energy-per-distance", "Measure Wh/km change on the real vehicle", "Instrumented vehicle, battery logger", "Energy logger",
           "Wh/km", "Statistically distinguishable improvement (method TBD)", False, "Repeated matched runs"),
        _t(4, "Environmental ageing", "Check property drift with age", "Aged samples/tyres", "Ageing chamber", "Property change %",
           "Defined by team", True, "Ageing then retest"),
        _t(5, "Manufacturing consistency", "Verify repeatability in pilot production", "Pilot batch", "Plant QC", "Batch variation %",
           "Defined by plant QC", False, "Statistical batch comparison"),
        _t(6, "Commercial qualification readiness (regulatory / OEM)", "Confirm requirements and evidence", "All prior evidence", "Certification body / OEM",
           "Checklist", "Requirements verified; no compliance claimed here", True, "Verify R75, IS 15627, ISO 18164 requirements and editions"),
    ]

def complete_test(t, result, evidence_ref, passed):
    """Mark complete only with a result and an evidence reference."""
    if not str(result).strip(): raise ValueError("A result is required to complete a test")
    if not str(evidence_ref).strip(): raise ValueError("An evidence reference is required to complete a test")
    t = dict(t); t.update(result=str(result), evidence_ref=str(evidence_ref), passed=bool(passed),
                          evidence_status="COMPLETE — PASS" if passed else "COMPLETE — FAIL")
    return t

def stage_gate(tests, stage):
    """Stage N is blocked while any safety-critical test in an earlier stage is incomplete or failed."""
    reasons = []
    for t in tests:
        if t["stage"] < stage and t["safety_critical"]:
            if t["passed"] is None: reasons.append(f"Stage {t['stage']}: '{t['name']}' not completed")
            elif not t["passed"]: reasons.append(f"Stage {t['stage']}: '{t['name']}' FAILED")
    return dict(stage=stage, allowed=not reasons, reasons=reasons)
