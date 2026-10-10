"""RegenGrip-LRR Engineering Studio — launch with: streamlit run app.py"""
import streamlit as st
st.set_page_config(page_title="RegenGrip-LRR Engineering Studio", page_icon="🛞", layout="wide")
pages = [("1_Executive_Overview", "Executive Overview"), ("2_Vehicle_and_Baseline", "Vehicle & Baseline"),
         ("3_Tyre_Concept_Designer", "Tyre Concept Designer"), ("4_Performance_Comparison", "Performance Comparison"),
         ("5_Optimization_Lab", "Optimization Lab"), ("6_Sensitivity_Analysis", "Sensitivity Analysis"),
         ("7_Cost_and_Manufacturing", "Cost & Manufacturing"), ("8_Validation_Planner", "Validation Planner"),
         ("9_Experiment_History", "Experiment History"), ("10_Technical_Report", "Technical Report")]
nav = st.navigation([st.Page(f"pages/{f}.py", title=t, default=(i == 0)) for i, (f, t) in enumerate(pages)])
nav.run()
