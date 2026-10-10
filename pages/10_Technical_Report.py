import streamlit as st
from components.state import page_header, scenario, results
from services.report_generator import build_report
from services.export_service import comparison_table, df_csv, scenario_json
from config.defaults import REPORT_TITLE
page_header("Technical Report", REPORT_TITLE)
sc = scenario("Report scenario"); res = results()
st.write("The PDF is recomputed from the saved inputs shown here; targets, assumptions, calculations and measured data are labelled separately.")
st.download_button("Download technical report (PDF)", build_report(sc), "RegenGrip-LRR_Concept_Stage_Analysis.pdf", "application/pdf")
st.download_button("Download calculation table (CSV)", df_csv(comparison_table(sc, res)), "calculations.csv", "text/csv")
st.download_button("Download scenario inputs (JSON)", scenario_json(sc), "scenario.json", "application/json")
st.dataframe(comparison_table(sc, res))
