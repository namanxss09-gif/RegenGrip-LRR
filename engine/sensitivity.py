"""Deterministic scenario / one-at-a-time sensitivity (NOT statistical uncertainty analysis)."""
import copy
import pandas as pd
from engine import energy as E

PARAMS = {"total_mass": "Total operating mass", "crr_candidate": "Candidate Crr", "crr_baseline": "Baseline Crr",
          "speed": "Speed", "distance": "Distance", "cda": "CdA", "air_density": "Air density", "drivetrain_eff": "Drivetrain efficiency"}

def evaluate(vehicle, crr_base, crr_cand, scale=None):
    """Metrics with multiplicative scale factors applied to chosen parameters."""
    s = scale or {}
    v = copy.copy(vehicle)
    k = s.get("total_mass", 1.0)
    v.vehicle_mass_kg *= k; v.payload_mass_kg *= k
    v.speed_kmh *= s.get("speed", 1.0); v.distance_km *= s.get("distance", 1.0)
    v.air_density *= s.get("air_density", 1.0)
    if v.cda_m2 is not None: v.cda_m2 *= s.get("cda", 1.0)
    if v.drivetrain_eff is not None: v.drivetrain_eff = min(1.0, v.drivetrain_eff * s.get("drivetrain_eff", 1.0))
    r = E.candidate_vs_baseline(v, crr_base * s.get("crr_baseline", 1.0), crr_cand * s.get("crr_candidate", 1.0))
    return dict(rr_saving_wh=-r["d_rr_wh"], rr_energy_cand_wh=r["cand"]["e_rr_wh"], total_cand_wh=r["cand"]["e_total_wh"],
                battery_cand_wh=r["cand"]["e_battery_wh"], rolling_share=r["cand"]["rolling_share"])

def oat_table(vehicle, crr_base, crr_cand, pct=10.0, metric="rr_saving_wh"):
    """Vary each parameter by -pct/+pct one at a time; returns DataFrame sorted by swing."""
    base = evaluate(vehicle, crr_base, crr_cand)[metric]
    rows = []
    for p, label in PARAMS.items():
        lo = evaluate(vehicle, crr_base, crr_cand, {p: 1 - pct / 100})[metric]
        hi = evaluate(vehicle, crr_base, crr_cand, {p: 1 + pct / 100})[metric]
        if base is None or lo is None or hi is None: continue
        rows.append(dict(parameter=label, low=lo, base=base, high=hi, swing=abs(hi - lo), delta_low=lo - base, delta_high=hi - base))
    return pd.DataFrame(rows).sort_values("swing", ascending=False).reset_index(drop=True)

def scenarios(vehicle, crr_base, crr_cand, low: dict, high: dict):
    """Low/base/high scenarios using user-set multipliers (all parameters moved together)."""
    return pd.DataFrame({n: evaluate(vehicle, crr_base, crr_cand, sc) for n, sc in
                         [("low", low), ("base", {}), ("high", high)]}).T
