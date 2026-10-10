import streamlit as st
from components.state import page_header, candidates, DB_PATH
from components.scenario_forms import opt_num
from models.tyre import Candidate
from services import database as db
from config.defaults import *
page_header("Tyre Concept Designer", "Create, edit, duplicate and delete candidates. Missing values stay missing.")
ss = st.session_state
cs = candidates(); names = [c.name for c in cs]
sel = st.selectbox("Candidate", names, index=names.index(ss.active_name) if ss.active_name in names else 0)
c = next(x for x in cs if x.name == sel); k = f"{c.db_id}_"
a, b, d = st.columns(3)
if a.button("Duplicate"): n = db.duplicate_candidate(DB_PATH, sel); ss.active_name = n.name; st.rerun()
new_name = b.text_input("New candidate name", key="newc")
if b.button("Create new concept") and new_name.strip():
    if new_name in names: st.error("Name exists")
    else: db.save_candidate(DB_PATH, Candidate(name=new_name.strip())); ss.active_name = new_name.strip(); st.rerun()
if d.button("Delete this candidate", disabled=c.name == ss.baseline_name, help="Baseline in use cannot be deleted"):
    db.delete_candidate(DB_PATH, sel); ss.active_name = names[0]; st.rerun()
st.info("The Crr below is a HYPOTHETICAL INPUT used to explore consequences. A formulation does not determine Crr by itself — that needs experimental calibration.")
with st.form("cand"):
    t1, t2, t3, t4 = st.tabs(["Identity & compound", "Tread", "Construction", "Economics"])
    with t1:
        name = st.text_input("Name", c.name); version = st.text_input("Version", c.version); desc = st.text_area("Description", c.description)
        author = st.text_input("Author", c.author); status = st.selectbox("Status", CANDIDATE_STATUSES, index=CANDIDATE_STATUSES.index(c.status))
        cs_ = st.text_area("Compound strategy", c.compound_strategy); fi = st.text_input("Filler strategy", c.filler); po = st.text_input("Polymer strategy", c.polymer)
        si = st.text_input("Silane / dispersion", c.silane); ro = st.text_input("Resin / oil", c.resin_oil)
        crr = opt_num("Crr (hypothetical or measured; blank = missing)", c.crr, k + "crr"); cev = st.selectbox("Crr evidence", EVIDENCE_TAGS, index=EVIDENCE_TAGS.index(c.crr_evidence))
        csrc = st.text_input("Crr source / provenance", c.crr_source)
        st.markdown("**Measured data (leave blank unless a real test exists; an evidence reference is required to count)**")
        wet = opt_num("Wet braking distance (m, same test as baseline)", c.wet_braking_distance_m, k + "wet"); wref = st.text_input("Wet-braking evidence ref", c.wet_evidence_ref)
        wear = opt_num("Tread-life ratio vs baseline (1.0 = equal)", c.wear_life_ratio, k + "wear"); wearref = st.text_input("Wear evidence ref", c.wear_evidence_ref)
        noise = opt_num("Noise change vs baseline (dB, negative = quieter)", c.noise_delta_db, k + "noise"); nref = st.text_input("Noise evidence ref", c.noise_evidence_ref)
        mp = st.text_area("Material-property data (if any)", c.material_properties)
    with t2:
        pat = st.text_input("Pattern category", c.pattern); bg = st.text_area("Block geometry", c.block_geometry); ps = st.text_input("Pitch sequencing", c.pitch_sequence)
        bs = st.text_area("Block-stiffness hypothesis", c.block_stiffness_hypothesis); dr = st.text_area("Drainage considerations", c.drainage_notes)
    with t3:
        ca = st.text_area("Casing strategy", c.casing_strategy); pr = st.text_input("Profile / sidewall changes", c.profile_changes); ts = st.text_input("Tyre size", c.tyre_size)
        li = st.selectbox("Load-index verification", LOAD_INDEX_STATUSES, index=LOAD_INDEX_STATUSES.index(c.load_index_status))
        mc = st.text_area("Manufacturing changes required", c.manufacturing_changes); ms = st.selectbox("Manufacturing status", LOAD_INDEX_STATUSES, index=LOAD_INDEX_STATUSES.index(c.manufacturing_status))
        sm = opt_num("Manufacturing feasibility score 0–10 (user-assigned ASSUMPTION)", c.score_manufacturing, k + "sm"); sr = opt_num("Technical risk score 0–10 (user-assigned; higher = riskier)", c.score_risk, k + "sr")
    with t4:
        st.caption("Increments vs baseline per tyre. Blank = unknown (never treated as zero).")
        mat = opt_num("Material cost increment", c.material_cost, k + "mat"); prc = opt_num("Processing cost increment", c.processing_cost, k + "prc")
        scr = opt_num("Scrap/rework increment", c.scrap_cost, k + "scr"); qc = opt_num("QC cost increment", c.qc_cost, k + "qc")
        too = opt_num("One-time tooling expenditure", c.tooling_cost, k + "too"); tdv = opt_num("Testing & development expenditure", c.testing_dev_cost, k + "tdv")
        cur = st.text_input("Currency", c.currency); cpv = st.text_input("Cost provenance", c.cost_provenance)
    if st.form_submit_button("Save candidate"):
        if crr is not None and crr < 0: st.error("Crr must be ≥ 0")
        elif sm is not None and not 0 <= sm <= 10 or sr is not None and not 0 <= sr <= 10: st.error("Scores must be 0–10")
        else:
            c.__dict__.update(name=name, version=version, description=desc, author=author, status=status, compound_strategy=cs_, filler=fi, polymer=po, silane=si,
                resin_oil=ro, crr=crr, crr_evidence=cev, crr_source=csrc, wet_braking_distance_m=wet, wet_evidence_ref=wref, wear_life_ratio=wear, wear_evidence_ref=wearref,
                noise_delta_db=noise, noise_evidence_ref=nref, material_properties=mp, pattern=pat, block_geometry=bg, pitch_sequence=ps, block_stiffness_hypothesis=bs, drainage_notes=dr,
                casing_strategy=ca, profile_changes=pr, tyre_size=ts, load_index_status=li, manufacturing_changes=mc, manufacturing_status=ms, score_manufacturing=sm, score_risk=sr,
                material_cost=mat, processing_cost=prc, scrap_cost=scr, qc_cost=qc, tooling_cost=too, testing_dev_cost=tdv, currency=cur, cost_provenance=cpv)
            if name != sel: db.rename_candidate(DB_PATH, sel, c); 
            else: db.save_candidate(DB_PATH, c)
            if ss.baseline_name == sel: ss.baseline_name = name
            ss.active_name = name; st.success("Saved"); st.rerun()
