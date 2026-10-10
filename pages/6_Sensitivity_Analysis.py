import streamlit as st, plotly.graph_objects as go
from components.state import page_header, vehicle, candidates
from engine import sensitivity as S
from services.export_service import df_csv
page_header("Sensitivity Analysis", "Deterministic one-at-a-time and low/base/high scenarios. These are NOT confidence intervals.")
ss = st.session_state; v = vehicle(); cs = {c.name: c for c in candidates()}
base, cand = cs[ss.baseline_name], cs[ss.active_name]
if base.name == cand.name or base.crr is None or cand.crr is None or v.validate()[0]:
    st.info("Select a different active candidate than the baseline, with Crr entered for both and valid vehicle inputs."); st.stop()
metric_lbl = {"rr_saving_wh": "Rolling-term saving vs baseline (Wh)", "rr_energy_cand_wh": "Candidate rolling energy (Wh)", "total_cand_wh": "Candidate total road-load energy (Wh)", "battery_cand_wh": "Candidate battery energy (Wh)"}
m = st.selectbox("Output metric", list(metric_lbl), format_func=metric_lbl.get)
pct = st.slider("± variation applied to each input (%)", 1.0, 50.0, float(ss.sens["pct"])); ss.sens["pct"] = pct
t = S.oat_table(v, base.crr, cand.crr, pct, m)
if t.empty: st.warning("Metric unavailable (missing CdA or efficiency)."); st.stop()
st.dataframe(t.round(4))
f = go.Figure()
t2 = t.iloc[::-1]
f.add_bar(y=t2.parameter, x=t2.delta_low, orientation="h", name=f"−{pct:.0f}%", marker_color="#6B7280")
f.add_bar(y=t2.parameter, x=t2.delta_high, orientation="h", name=f"+{pct:.0f}%", marker_color="#C8102E")
f.update_layout(barmode="overlay", title=f"Tornado: change in '{metric_lbl[m]}' (deterministic)", xaxis_title="Δ vs base (Wh)", template="plotly_white", height=420)
st.plotly_chart(f)
zero = t[t.swing < 1e-9].parameter.tolist()
if zero: st.caption("No effect by model construction on this metric: " + ", ".join(zero) + ".")
st.write(f"Largest influence: **{t.iloc[0].parameter}**, then **{t.iloc[1].parameter}**.")
st.subheader("Low / base / high scenarios (user-set multipliers, moved together)")
cols = st.columns(2); keys = ["total_mass", "crr_candidate", "crr_baseline", "distance", "cda", "air_density", "drivetrain_eff", "speed"]
lo = {k: cols[0].number_input(f"Low × {S.PARAMS[k]}", 0.1, 3.0, 0.9, 0.05, key=f"lo{k}") for k in keys}
hi = {k: cols[1].number_input(f"High × {S.PARAMS[k]}", 0.1, 3.0, 1.1, 0.05, key=f"hi{k}") for k in keys}
sc = S.scenarios(v, base.crr, cand.crr, lo, hi); st.dataframe(sc)
st.download_button("Download scenario CSV", df_csv(sc.reset_index()), "scenarios.csv", "text/csv")
