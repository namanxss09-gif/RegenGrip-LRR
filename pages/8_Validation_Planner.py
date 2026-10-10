import streamlit as st, pandas as pd
from components.state import page_header
from engine.validation_planner import STAGES, stage_gate, complete_test
from services.report_generator import build_validation_report
page_header("Validation Planner", "Staged tests with safety stage gates. A test is complete only with a result AND an evidence reference.")
ss = st.session_state
st.subheader("Stage gates")
for s in STAGES:
    g = stage_gate(ss.tests, s)
    (st.success if False else st.info if g["allowed"] else st.error)(f"Stage {s} — {STAGES[s]}: " + ("OPEN (not evidence of safety)" if g["allowed"] else "BLOCKED"))
    for r in g["reasons"]: st.caption("• " + r)
st.subheader("Tests")
st.dataframe(pd.DataFrame([{k: t[k] for k in ("stage", "name", "safety_critical", "evidence_status", "acceptance", "owner", "next_action")} for t in ss.tests]))
labels = [f"S{x['stage']} · {x['name']}" for x in ss.tests]
i = labels.index(st.selectbox("Open a test", labels))
t = ss.tests[i]
with st.expander("Details", expanded=True):
    for k in ("objective", "baseline", "required_inputs", "equipment", "method", "procedure", "units", "acceptance"): st.markdown(f"**{k.replace('_',' ').title()}:** {t[k]}")
with st.form("done"):
    res_ = st.text_input("Result (with units)", t["result"]); ref = st.text_input("Evidence reference (report ID / file / URL)", t["evidence_ref"])
    passed = st.radio("Outcome against acceptance criterion", ["PASS", "FAIL"], horizontal=True); owner = st.text_input("Owner", t["owner"]); nxt = st.text_input("Next action", t["next_action"])
    if st.form_submit_button("Mark complete"):
        try: ss.tests[i] = complete_test({**t, "owner": owner, "next_action": nxt}, res_, ref, passed == "PASS"); st.rerun()
        except ValueError as e: st.error(str(e))
st.download_button("Download printable validation plan (PDF)", build_validation_report(ss.tests), "validation_plan.pdf", "application/pdf")
st.caption("Regulatory items (UN/ECE R75, IS 15627, ISO 18164) are a checklist to verify; no compliance is claimed.")
