"""CSV / JSON exports."""
import json
import pandas as pd

def df_csv(df: pd.DataFrame) -> bytes: return df.to_csv(index=False).encode("utf-8")
def scenario_json(sc: dict) -> bytes: return json.dumps(sc, indent=2, default=str).encode("utf-8")

def comparison_table(sc, res):
    """Flat table of per-candidate calculations (reproducible from the scenario)."""
    rows = []
    for n, r in res["per_candidate"].items():
        e = r["energy"]
        rows.append(dict(candidate=n, crr=r["crr"], crr_evidence=r["crr_evidence"],
                         rolling_force_N=e and e["cand"]["f_rr_n"], rolling_power_W=e and e["cand"]["p_rr_w"],
                         rolling_energy_Wh=e and e["cand"]["e_rr_wh"], delta_rolling_energy_Wh=e and e["d_rr_wh"],
                         delta_rolling_energy_pct=e and e["d_rr_pct"], battery_equiv_delta_Wh=e and e["d_battery_wh"],
                         status=r["feasibility"]["overall"], evidence_type="CALCULATION"))
    return pd.DataFrame(rows)
