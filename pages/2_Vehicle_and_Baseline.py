import streamlit as st
from components.state import page_header, vehicle, candidates, DB_PATH
from components.scenario_forms import opt_num
from models.vehicle import Vehicle
from services import database as db
from config.defaults import *
page_header("Vehicle and Baseline", "Reference vehicle and baseline Crr. All demo values are ILLUSTRATIVE and editable.")
ss, v = st.session_state, vehicle()
if st.button("Restore illustrative demo defaults"): ss.vehicle = Vehicle().to_dict(); st.rerun()
with st.form("veh"):
    a, b = st.columns(2)
    d = dict(vehicle_type=a.text_input("Vehicle type", v.vehicle_type), tyre_size=a.text_input("Tyre size / fitment ID", v.tyre_size, help="Obtain from the vehicle manufacturer"),
             vehicle_mass_kg=a.number_input("Vehicle mass (kg)", value=float(v.vehicle_mass_kg)), payload_mass_kg=a.number_input("Rider + payload (kg)", value=float(v.payload_mass_kg)),
             front_load_fraction=a.number_input("Front load fraction (0–1)", value=float(v.front_load_fraction)),
             analysis_axle=a.selectbox("Axle analysed", ["whole vehicle", "front", "rear"], index=["whole vehicle", "front", "rear"].index(v.analysis_axle),
                                       help="Candidate tyre on this axle; the other axle keeps baseline Crr"),
             pressure_kpa=b.number_input("Cold inflation pressure (kPa)", value=float(v.pressure_kpa), help="Test condition only — no Crr correlation is assumed"),
             speed_kmh=b.number_input("Reference speed (km/h)", value=float(v.speed_kmh)), distance_km=b.number_input("Test distance (km)", value=float(v.distance_km)),
             ambient_c=b.number_input("Ambient temperature (°C)", value=float(v.ambient_c)),
             drive_cycle=b.selectbox("Drive cycle", ["Constant speed, level road"], help="Only this cycle is implemented"),
             air_density=b.number_input("Air density (kg/m³)", value=float(v.air_density), format="%.3f"), aux_power_w=b.number_input("Auxiliary power (W)", value=float(v.aux_power_w)))
    eff = b.text_input("Drivetrain efficiency (0–1, blank = unknown)", "" if v.drivetrain_eff is None else str(v.drivetrain_eff))
    cda = b.text_input("CdA (m², blank = unknown)", "" if v.cda_m2 is None else str(v.cda_m2))
    ok = st.form_submit_button("Apply vehicle configuration")
if ok:
    try: d["drivetrain_eff"] = float(eff) if eff.strip() else None; d["cda_m2"] = float(cda) if cda.strip() else None
    except ValueError: st.error("Efficiency / CdA must be numbers"); st.stop()
    nv = Vehicle.from_dict(d); errs, _ = nv.validate()
    if errs: st.error("Not applied — " + "; ".join(errs))
    else: ss.vehicle = nv.to_dict(); st.success("Applied"); st.rerun()
errs, warns = v.validate()
for e in errs: st.error(e)
for w in warns: st.warning(w)
m = st.columns(3); m[0].metric("Total operating mass", f"{v.total_mass_kg:.1f} kg"); m[1].metric("Front / rear load", f"{v.total_mass_kg*v.front_load_fraction:.1f} / {v.total_mass_kg*(1-v.front_load_fraction):.1f} kg")
m[2].metric("Analysed load", f"{v.total_mass_kg*v.axle_fraction:.1f} kg")
st.subheader("Baseline Crr")
base = next(c for c in candidates() if c.name == ss.baseline_name)
with st.form("bcrr"):
    crr = opt_num("Baseline Crr (dimensionless)", base.crr, "bcrr_v"); src = st.text_input("Source / evidence", base.crr_source)
    ev = st.selectbox("Evidence status", EVIDENCE_TAGS, index=EVIDENCE_TAGS.index(base.crr_evidence))
    if st.form_submit_button("Save baseline Crr"):
        if crr is not None and crr < 0: st.error("Crr must be ≥ 0")
        else: base.crr, base.crr_source, base.crr_evidence = crr, src, ev; db.save_candidate(DB_PATH, base); st.rerun()
if base.crr_evidence != "MEASURED RESULT": st.warning(f"Baseline Crr evidence: {base.crr_evidence}. Replace with a sourced measurement before drawing conclusions.")
