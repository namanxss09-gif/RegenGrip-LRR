import streamlit as st, pandas as pd
from components.state import page_header, results, vehicle, candidates
from components.metric_cards import badge, card, fmt
from config.defaults import *
page_header(TITLE, SUBTITLE)
ss, res = st.session_state, results()
st.info("This page compares the *mathematics* of rolling resistance under stated assumptions. It does not predict physical tyre performance.")
st.markdown("**Problem:** lower tyre rolling resistance can reduce road-load energy for an EV two-wheeler, but wet grip, wear and noise must not regress. "
            "This tool shows what a hypothetical Crr change implies and what evidence is still missing.")
if res["vehicle_errors"]: st.error("Vehicle input errors: " + "; ".join(res["vehicle_errors"]))
for w in res["vehicle_warnings"]: st.warning(w)
base, act = ss.baseline_name, ss.active_name
pb, pa = res["per_candidate"][base], res["per_candidate"][act]
st.subheader(f"Baseline: {base}  →  Active: {act}")
st.caption(DESIGN_TARGET_TEXT)
c = st.columns(4)
e = pa["energy"]
if e:
    card(c[0], "Crr (baseline → active)", f"{pb['crr']:.4f} → {pa['crr']:.4f}", f"{pb['crr_evidence']} / {pa['crr_evidence']}")
    card(c[1], "Rolling force F_rr", f"{e['cand']['f_rr_n']:.2f} N", "CALCULATION", f"Baseline {e['base']['f_rr_n']:.2f} N")
    card(c[2], "Rolling energy over distance", f"{e['cand']['e_rr_wh']:.1f} Wh", "CALCULATION", f"Baseline {e['base']['e_rr_wh']:.1f} Wh")
    card(c[3], "Δ rolling-resistance energy", f"{e['d_rr_wh']:+.2f} Wh ({fmt(e['d_rr_pct'], '{:+.1f}')}%)", "CALCULATION (not battery saving)")
else: st.warning("Comparison unavailable: enter valid vehicle inputs and Crr for both tyres.")
inc = [c_ for c_ in candidates()]
vin = sum(v is not None for v in [vehicle().drivetrain_eff, vehicle().cda_m2]) / 2
cbase = next(c_ for c_ in inc if c_.name == base); cact = next(c_ for c_ in inc if c_.name == act)
done = sum(i["status"] == "VERIFIED" for i in ss.checklist)
wet = next(x for x in pa["feasibility"]["criteria"] if x["criterion"].startswith("Wet"))
wear = next(x for x in pa["feasibility"]["criteria"] if x["criterion"].startswith("Wear"))
rows = [("Model status", "CALCULATION — closed-form algebra, NOT a validated tyre simulation"),
        ("Input completeness", f"{'ASSUMPTION-BASED' if 'ILLUSTRATIVE' in vehicle().vehicle_type.upper() else 'USER INPUT'}; optional inputs present: {vin:.0%}"),
        ("Wet-braking validation", badge("PENDING" if wet["status"] == "UNKNOWN" else wet["status"]) + " — " + wet["detail"]),
        ("Rolling-resistance evidence", f"{cact.crr_evidence} — {cact.crr_source or 'no source'}"),
        ("Wear evidence", badge("PENDING" if wear["status"] == "UNKNOWN" else wear["status"])),
        ("Manufacturing feasibility", f"{done}/{len(ss.checklist)} checklist items VERIFIED"),
        ("Cost-data completeness", f"{pa['cost_completeness']:.0%} of cost inputs entered"),
        ("Overall status", pa["feasibility"]["overall"])]
st.subheader("Status indicators"); st.table(pd.DataFrame(rows, columns=["Indicator", "Status"]).set_index("Indicator"))
st.subheader("Unresolved engineering questions")
st.markdown("- What is the measured baseline Crr and its test method?\n- Does the candidate keep wet braking at least equal to baseline (hard gate)?\n"
            "- What does the compound cost per tyre, and what plant changes are needed?\n- How do wear, noise and load-index verification turn out in testing?\n"
            "- What are the real vehicle mass, CdA, tyre size and pressure?")
