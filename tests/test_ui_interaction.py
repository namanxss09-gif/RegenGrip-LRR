import os, pathlib, pytest
from streamlit.testing.v1 import AppTest
ROOT = pathlib.Path(__file__).resolve().parents[1]

@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("REGENGRIP_DB", str(tmp_path / "ui.db")); monkeypatch.chdir(ROOT)

def run(p): return AppTest.from_file(str(ROOT / "pages" / p), default_timeout=60).run()
def btn(at, label): return next(b for b in at.button if b.label == label)

def test_crr_edit_saves_and_recalculates():
    from services import database as db
    at = run("3_Tyre_Concept_Designer.py")
    next(t for t in at.text_input if t.label.startswith("Crr (hypothetical")).set_value("0.0100")
    btn(at, "Save candidate").click(); at.run()
    assert not at.exception
    g = next(c for c in db.list_candidates(os.environ["REGENGRIP_DB"]) if c.name.endswith("Hybrid G"))
    assert g.crr == 0.01

def test_invalid_weights_disable_ranking():
    at = run("5_Optimization_Lab.py")
    at.number_input(key="w_rr_improvement").set_value(0.9).run()
    assert any("Weights must sum" in e.value for e in at.error)

def test_vehicle_invalid_rejected():
    at = run("2_Vehicle_and_Baseline.py")
    next(n for n in at.number_input if n.label.startswith("Vehicle mass")).set_value(-5.0)
    btn(at, "Apply vehicle configuration").click(); at.run()
    assert any("Not applied" in e.value for e in at.error)

def test_test_completion_needs_evidence():
    at = run("8_Validation_Planner.py")
    next(t for t in at.text_input if t.label.startswith("Result")).set_value("x")
    btn(at, "Mark complete").click(); at.run()
    assert any("evidence reference" in e.value for e in at.error)
