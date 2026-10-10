import streamlit as st, pandas as pd, plotly.graph_objects as go
from components.state import page_header, results, candidates
from components.scenario_forms import opt_num
from components.metric_cards import badge
from models.validation import validate_weights
from config.defaults import *
page_header("Optimization Lab", "Feasibility gates first, then an optional transparent weighted ranking. No unknown rubber properties are predicted.")
ss = st.session_state; cn = ss.constraints
st.subheader("1. Constraints")
a, b, c = st.columns(3)
cn["min_crr_reduction_pct"] = a.number_input("Min Crr reduction vs baseline (%)", value=float(cn["min_crr_reduction_pct"]), help="Design target — NOT VALIDATED")
cn["wet_tolerance_pct"] = b.number_input("Wet-braking distance tolerance (%)", value=float(cn["wet_tolerance_pct"]), min_value=0.0)
cn["wear_tolerance_pct"] = c.number_input("Wear tolerance (%)", value=float(cn["wear_tolerance_pct"]), min_value=0.0)
with a: cn["max_incremental_cost"] = opt_num("Max incremental cost per tyre (blank = no limit)", cn["max_incremental_cost"], "maxc")
cn["require_load_index"] = b.checkbox("Require load-index verification", value=cn["require_load_index"])
res = results()
st.subheader("2. Feasibility (PASS / FAIL / UNKNOWN)")
for n, r in res["per_candidate"].items():
    with st.expander(f"{n} — {r['feasibility']['overall']}", expanded=n == ss.active_name):
        st.table(pd.DataFrame([dict(criterion=x["criterion"], status=badge(x["status"]), safety_critical="YES" if x["safety_critical"] else "no", evidence=x["evidence"], detail=x["detail"]) for x in r["feasibility"]["criteria"]]))
st.caption("🔵 PASS means 'met on the evidence entered', not certified safe. UNKNOWN safety criteria are never treated as PASS.")
st.subheader("3. Weighted ranking (optional)")
w = {k: st.number_input(lbl, 0.0, 1.0, float(ss.weights[k]), 0.05, key=f"w_{k}") for k, lbl in WEIGHT_LABELS.items()}
ss.weights = w; errs = validate_weights(w)
if errs: st.error("; ".join(errs) + " — ranking disabled."); 
else:
    res = results()
    rows = [dict(candidate=r["candidate"], status=r["status"], rank=r["rank"] if r["rank"] else "—", score=None if r["score"] is None else round(r["score"], 2),
                 criteria_used=", ".join(r["used"]), missing_evidence=", ".join(r["missing"]) or "—") for r in res["ranking"]]
    st.dataframe(pd.DataFrame(rows))
    st.caption("Score uses only criteria with data (weights renormalised). Rr score: 20% Crr reduction = 10/10 (scaling convention). Infeasible candidates get no rank; pending-safety candidates are labelled UNVERIFIED.")
st.subheader("4. Pareto view: Crr vs incremental cost (both minimised)")
with st.expander("What is Pareto dominance?"): st.write("A candidate is dominated if another is at least as good on every objective and strictly better on one. Non-dominated candidates form the Pareto front. Wet braking is a hard filter, not an objective.")
pts = [(n, r["crr"], r["recurring"]["total"]) for n, r in res["per_candidate"].items()]
par = res["pareto"]
if len(par) < 2: st.info("Pareto chart needs ≥2 candidates with both Crr and a complete recurring cost. Enter cost increments on the Concept Designer page. Missing costs are not treated as zero.")
else:
    f = go.Figure()
    for n, crr, cost in pts:
        if n in par: f.add_trace(go.Scatter(x=[cost], y=[crr], mode="markers+text", text=[n], textposition="top center", name=par[n], marker=dict(size=12, color="#C8102E" if par[n] == "NON-DOMINATED" else "#6B7280")))
    f.update_layout(xaxis_title="Incremental cost per tyre", yaxis_title="Crr (–)", template="plotly_white", title="Pareto view (inputs: USER INPUT / ASSUMPTION)")
    st.plotly_chart(f)
