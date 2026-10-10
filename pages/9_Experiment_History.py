import json, streamlit as st, pandas as pd
from components.state import page_header, scenario, DB_PATH, candidates
from services import database as db
from services.export_service import scenario_json
from models.scenario import compute_all
page_header("Experiment History", "Save, reload, compare and export scenarios (SQLite). Results are reproducible from saved inputs.")
ss = st.session_state
name = st.text_input("Scenario name", "Scenario " + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"))
if st.button("Save current scenario"):
    sc = scenario(name); db.save_scenario(DB_PATH, sc, compute_all(sc)); st.success("Saved"); st.rerun()
rows = db.list_scenarios(DB_PATH)
if not rows: st.info("No saved scenarios yet.")
else:
    st.dataframe(pd.DataFrame(rows))
    sid = st.selectbox("Scenario", [r["id"] for r in rows], format_func=lambda i: next(f"#{r['id']} {r['name']}" for r in rows if r["id"] == i))
    sc = db.load_scenario(DB_PATH, sid)
    if sc is None: st.error("Record is malformed")
    else:
        a, b, c = st.columns(3)
        if a.button("Reload into workspace"):
            ss.vehicle, ss.baseline_name, ss.constraints, ss.weights = sc["vehicle"], sc["baseline_name"], sc["constraints"], sc["weights"]
            ss.program, ss.sens, ss.tests, ss.checklist = sc["program"], sc["sens"], sc["tests"], sc["checklist"]
            from models.tyre import Candidate
            for cd in sc["candidates"]: db.save_candidate(DB_PATH, Candidate.from_dict(cd))
            st.success("Scenario restored (candidates upserted by name)")
        b.download_button("Export JSON", scenario_json(sc), f"scenario_{sid}.json", "application/json")
        if c.button("Delete scenario"): db.delete_scenario(DB_PATH, sid); st.rerun()
        other = st.selectbox("Compare with", [r["id"] for r in rows if r["id"] != sid], format_func=lambda i: f"#{i}", index=None)
        if other:
            r1, r2 = compute_all(sc), compute_all(db.load_scenario(DB_PATH, other))
            cmp = []
            for n in r1["per_candidate"]:
                e1 = r1["per_candidate"][n]["energy"]; e2 = r2["per_candidate"].get(n, {}).get("energy")
                cmp.append(dict(candidate=n, rolling_Wh_selected=e1 and e1["cand"]["e_rr_wh"], rolling_Wh_other=e2 and e2["cand"]["e_rr_wh"], status_selected=r1["per_candidate"][n]["feasibility"]["overall"], status_other=r2["per_candidate"].get(n, {}).get("feasibility", {}).get("overall")))
            st.dataframe(pd.DataFrame(cmp))
st.subheader("Reset demo candidates")
st.warning("Restores the four built-in demo candidates to defaults (your edits to them are lost). Your own candidates and saved scenarios are not deleted.")
if st.checkbox("I understand") and st.button("Reset demo candidates"): db.reset_demo(DB_PATH, confirm=True); st.success("Demo candidates reset"); st.rerun()
