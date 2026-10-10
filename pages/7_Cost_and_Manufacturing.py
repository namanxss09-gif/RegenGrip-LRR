import streamlit as st, pandas as pd
from components.state import page_header, results, candidates
from components.scenario_forms import opt_num
from engine.cost_model import RECURRING, ONE_TIME, cost_per_pct_improvement
from components.metric_cards import fmt
from pages_data import STATUSES
page_header("Cost and Manufacturing Feasibility", "Increments vs baseline. Unknown stays unknown. Retail premium ≠ manufacturing cost.")
ss = st.session_state; res = results(); cs = {c.name: c for c in candidates()}
rows = []
for n, r in res["per_candidate"].items():
    rows.append({"candidate": n, **{lbl: fmt(r["recurring"]["items"][k]) for k, lbl in RECURRING}, "Recurring total/tyre": fmt(r["recurring"]["total"]) if r["recurring"]["complete"] else f"INCOMPLETE (partial {fmt(r['recurring']['partial'])})",
                 **{lbl: fmt(r["one_time"]["items"][k]) for k, lbl in ONE_TIME}, "One-time total": fmt(r["one_time"]["total"]), "completeness": f"{r['cost_completeness']:.0%}"})
st.dataframe(pd.DataFrame(rows)); st.caption("Edit cost inputs on the Tyre Concept Designer page (Economics tab). Currency/provenance are stored per candidate.")
st.subheader("Program economics (all optional)")
a, b = st.columns(2)
ss.program["volume"] = opt_num("Program volume (tyres)", ss.program["volume"], "vol"); ss.program["benefit_per_tyre"] = opt_num("Defined economic benefit per tyre (same currency)", ss.program["benefit_per_tyre"], "ben",
                                                                                                                        help="Your own defined benefit; not a consumer price premium")
res = results(); out = []
for n, r in res["per_candidate"].items():
    out.append(dict(candidate=n, program_cost=fmt(r["program_cost"]), break_even_volume=fmt(r["break_even"], "{:.0f}"), cost_per_pct_Crr=fmt(cost_per_pct_improvement(cs[n], cs[ss.baseline_name]))))
st.dataframe(pd.DataFrame(out)); st.caption("Cost per % Crr is only shown when Crr evidence is MEASURED RESULT; break-even only when margin per tyre is positive.")
st.subheader("Manufacturing feasibility checklist")
df = pd.DataFrame(ss.checklist)
ed = st.data_editor(df, column_config={"status": st.column_config.SelectboxColumn(options=STATUSES), "item": st.column_config.TextColumn(disabled=True)}, hide_index=True, key="chk")
ss.checklist = ed.to_dict("records")
bad = [i["item"] for i in ss.checklist if i["status"] == "VERIFIED" and not str(i["evidence"]).strip()]
if bad: st.warning("VERIFIED without evidence: " + ", ".join(bad))
