import streamlit as st, pandas as pd
from components.state import page_header, results, candidates, scenario
from components.comparison_charts import bar, delta_bar
from components.metric_cards import badge
from services.export_service import comparison_table, df_csv
page_header("Performance Comparison", "Identical vehicle conditions for every candidate. All values are CALCULATIONS from entered Crr.")
ss, res = st.session_state, results()
if res["vehicle_errors"]: st.error("; ".join(res["vehicle_errors"])); st.stop()
names = [c.name for c in candidates()]
pick = st.multiselect("Candidates", names, default=names[:3])
if ss.baseline_name not in pick: pick = [ss.baseline_name] + pick
pc = {n: res["per_candidate"][n] for n in pick if res["per_candidate"][n]["energy"]}
ev = [f"{pc[n]['crr_evidence']} (Crr input)" for n in pc]; n = list(pc)
c1, c2 = st.columns(2)
c1.plotly_chart(bar(n, [pc[x]["crr"] for x in n], "Rolling-resistance coefficient", "Crr (–)", ss.baseline_name, ev, "%{y:.5f}"))
c2.plotly_chart(bar(n, [pc[x]["energy"]["cand"]["f_rr_n"] for x in n], "Rolling force", "N", ss.baseline_name, ev))
c3, c4 = st.columns(2)
c3.plotly_chart(bar(n, [pc[x]["energy"]["cand"]["p_rr_w"] for x in n], "Rolling-resistance power at selected speed", "W", ss.baseline_name, ev))
c4.plotly_chart(bar(n, [pc[x]["energy"]["cand"]["e_rr_wh"] for x in n], "Rolling-resistance energy over distance", "Wh", ss.baseline_name, ev))
others = [x for x in n if x != ss.baseline_name]
if others: st.plotly_chart(delta_bar(others, [pc[x]["energy"]["d_rr_pct"] for x in others], "Rolling-resistance energy change vs baseline", "% (negative = lower)"))
tot = [pc[x]["energy"]["cand"]["e_total_wh"] for x in n]
if all(t is not None for t in tot): st.plotly_chart(bar(n, tot, "Estimated total road-load energy (rolling + aero, constant speed, level road)", "Wh", ss.baseline_name, ev))
else: st.info("Total road-load comparison UNAVAILABLE: CdA missing.")
bat = [pc[x]["energy"]["d_battery_wh"] for x in others]
if others and all(b is not None for b in bat): st.caption("Model-based battery-side equivalent of the rolling-term change (constant speed, level road, drivetrain η): " + ", ".join(f"{o}: {b:+.2f} Wh" for o, b in zip(others, bat)) + " — NOT a measured saving.")
st.subheader("Evidence, status and provenance")
rows = [dict(candidate=x, crr=pc[x]["crr"], crr_evidence=pc[x]["crr_evidence"], wet_braking=badge("PENDING" if next(c for c in pc[x]["feasibility"]["criteria"] if c["criterion"].startswith("Wet"))["status"] == "UNKNOWN" else next(c for c in pc[x]["feasibility"]["criteria"] if c["criterion"].startswith("Wet"))["status"]),
             wear="PENDING (no data)" if next(c for c in pc[x]["feasibility"]["criteria"] if c["criterion"].startswith("Wear"))["status"] == "UNKNOWN" else "see Optimization Lab", noise="PENDING (no data)", overall=pc[x]["feasibility"]["overall"], cost_completeness=f"{pc[x]['cost_completeness']:.0%}") for x in n]
st.dataframe(pd.DataFrame(rows)); st.caption("Wet grip, tyre life and noise are never estimated here — only measured data you enter, or PENDING.")
st.download_button("Download comparison CSV", df_csv(comparison_table(scenario(), res)), "comparison.csv", "text/csv")
