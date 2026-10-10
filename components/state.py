"""Shared Streamlit session state, DB access and scenario assembly."""
import os
import streamlit as st
from config.defaults import *
from models.vehicle import Vehicle
from models.scenario import build_scenario, compute_all
from services import database as db
from engine.validation_planner import default_tests
from pages_data import default_checklist

DB_PATH = os.environ.get("REGENGRIP_DB", "regengrip.db")

def ensure_state():
    st.set_page_config(page_title=TITLE, page_icon="🛞", layout="wide")
    if st.session_state.get("_init"): return
    db.init_db(DB_PATH); db.seed_demo(DB_PATH)
    ss = st.session_state
    ss.vehicle = Vehicle().to_dict(); ss.baseline_name = BASELINE_NAME; ss.active_name = G_NAME
    ss.constraints = dict(DEFAULT_CONSTRAINTS); ss.weights = dict(DEFAULT_WEIGHTS)
    ss.program = dict(volume=None, benefit_per_tyre=None); ss.sens = dict(pct=10.0)
    ss.tests = default_tests(); ss.checklist = default_checklist(); ss._init = True

def vehicle(): return Vehicle.from_dict(st.session_state.vehicle)
def candidates(): return db.list_candidates(DB_PATH)

def scenario(name="Working scenario"):
    ss = st.session_state
    return build_scenario(name, vehicle(), candidates(), ss.baseline_name, ss.constraints, ss.weights, ss.program, ss.sens, ss.tests, ss.checklist)

def results(): return compute_all(scenario())

def sidebar():
    ss = st.session_state
    names = [c.name for c in candidates()]
    with st.sidebar:
        st.markdown(f"### {TITLE}"); st.caption("CONCEPT-STAGE · results are calculations, not measurements")
        if ss.baseline_name not in names: ss.baseline_name = names[0]
        ss.baseline_name = st.selectbox("Baseline", names, index=names.index(ss.baseline_name), key="sb_base")
        if ss.active_name not in names: ss.active_name = names[0]
        ss.active_name = st.selectbox("Active candidate", names, index=names.index(ss.active_name), key="sb_active")
        st.caption("Demo inputs are ILLUSTRATIVE. Wet braking stays PENDING until measured data is entered.")

def page_header(title, sub=None):
    ensure_state(); sidebar(); st.title(title)
    if sub: st.caption(sub)
    st.warning(DISCLAIMER, icon="⚠️")
