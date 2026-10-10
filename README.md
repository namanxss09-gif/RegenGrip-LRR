# RegenGrip-LRR Engineering Studio
Concept-stage engineering decision support for the Eurogrip × Unstop Case Study 2 (EV two-wheeler tyre). Python + Streamlit + SQLite.
**Not an official Eurogrip product or report. No result here is a measured tyre property.**

## Features
Executive overview · vehicle/baseline config · candidate designer (create/edit/duplicate/delete) · rolling force/power/energy comparison ·
feasibility gates (PASS/FAIL/UNKNOWN) and transparent ranking · Pareto view · deterministic sensitivity/tornado · cost and manufacturing checklist ·
staged validation planner with stage gates · SQLite experiment history · PDF/CSV/JSON export.

## Install and launch
Windows:
```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```
Linux/macOS:
```
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```
The database (`regengrip.db`) is created on first launch. Set `REGENGRIP_DB` to use another path.

## Tests
`python -m pytest -q tests`

## Demo workflow
1 Overview → 2 Vehicle (illustrative scooter; edit/restore) → 3 Designer (change a Crr) → 4 Comparison → 7 Cost (enter increments) →
5 Optimization (constraints, ranking, Pareto) → 6 Sensitivity → 8 Validation (generate PDF plan) → 9 Save scenario → 10 Export report.

## How to
- Add a candidate: Designer → "Create new concept" or "Duplicate".
- Add physical test data: Designer → Measured data (value AND evidence reference are both needed to count).
- Verify sources: replace ILLUSTRATIVE inputs with cited values; set Crr evidence to MEASURED RESULT only for real measurements.
- Save/export: Experiment History (save/reload/compare/JSON), Technical Report (PDF/CSV).

## Structure
app.py (navigation) · config/ · models/ · engine/ · services/ · components/ · pages/ · tests/ · docs/ · data/ · pages_data.py (checklist defaults)
Note: pages/ are loaded via `st.navigation` in app.py (not auto-discovery) so order and titles are explicit.

## Troubleshooting
Module not found → run from the project folder. Port busy → `streamlit run app.py --server.port 8600`. Reset demo candidates on the Experiment History page.

## Roadmap
Real dossier data import · measured-data calibration of Crr models · uncertainty distributions once data exists · slope/drive-cycle energy model.
