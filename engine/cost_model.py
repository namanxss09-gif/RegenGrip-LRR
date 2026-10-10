"""Cost model: computes only from inputs present; missing stays missing (never zero)."""
RECURRING = [("material_cost", "Material (polymer/filler/silane/resin)"), ("processing_cost", "Mixing/processing"),
             ("scrap_cost", "Scrap/rework"), ("qc_cost", "Quality control")]
ONE_TIME = [("tooling_cost", "Tooling / mould modification"), ("testing_dev_cost", "Testing and development")]

def _sum(cand, spec):
    vals = {k: getattr(cand, k) for k, _ in spec}
    missing = [lbl for k, lbl in spec if vals[k] is None]
    present = [v for v in vals.values() if v is not None]
    return dict(total=sum(present) if not missing else None, partial=sum(present) if present else None,
                complete=not missing, missing=missing, items=vals)

def recurring_cost(cand):
    """Incremental variable cost per tyre vs baseline (total None unless every component is entered)."""
    return _sum(cand, RECURRING)

def one_time_cost(cand):
    return _sum(cand, ONE_TIME)

def completeness(cand):
    """Fraction of the 6 cost inputs that are present."""
    keys = [k for k, _ in RECURRING + ONE_TIME]
    return sum(getattr(cand, k) is not None for k in keys) / len(keys)

def program_cost(cand, volume):
    """Total program cost = one-time + recurring * volume; None when anything required is missing."""
    r, o = recurring_cost(cand), one_time_cost(cand)
    if not (r["complete"] and o["complete"]) or volume is None or volume < 0: return None
    return o["total"] + r["total"] * volume

def break_even_volume(cand, benefit_per_tyre):
    """Volume at which per-tyre benefit repays one-time cost. None if inputs missing or margin <= 0."""
    r, o = recurring_cost(cand), one_time_cost(cand)
    if not (r["complete"] and o["complete"]) or benefit_per_tyre is None: return None
    margin = benefit_per_tyre - r["total"]
    if margin <= 0: return None
    return o["total"] / margin

def cost_per_pct_improvement(cand, baseline):
    """Incremental cost per % Crr reduction — only when Crr evidence is MEASURED RESULT."""
    r = recurring_cost(cand)
    if not r["complete"] or cand.crr is None or baseline.crr in (None, 0) or cand.crr_evidence != "MEASURED RESULT": return None
    red = (baseline.crr - cand.crr) / baseline.crr * 100
    return r["total"] / red if red > 0 else None
