from services import report_generator as R, database as D
from services.export_service import comparison_table
from models.scenario import build_scenario, compute_all
from models.vehicle import Vehicle
from engine.validation_planner import default_tests
from config.defaults import DEFAULT_CONSTRAINTS, DEFAULT_WEIGHTS
from pages_data import default_checklist

def _sc(tmp_path, vehicle=None):
    p = str(tmp_path / "r.db"); D.init_db(p); D.seed_demo(p); cs = D.list_candidates(p)
    return build_scenario("rep", vehicle or Vehicle(), cs, cs[0].name, DEFAULT_CONSTRAINTS, DEFAULT_WEIGHTS, {"volume": None}, {"pct": 10}, default_tests(), default_checklist())

def test_report_generates_pdf_with_missing_data(tmp_path):
    pdf = R.build_report(_sc(tmp_path)); assert pdf[:4] == b"%PDF" and len(pdf) > 3000

def test_report_with_invalid_vehicle_still_builds(tmp_path):
    assert R.build_report(_sc(tmp_path, Vehicle(vehicle_mass_kg=-5)))[:4] == b"%PDF"

def test_validation_report(): assert R.build_validation_report(default_tests())[:4] == b"%PDF"

def test_evidence_labels_and_csv(tmp_path):
    sc = _sc(tmp_path); df = comparison_table(sc, compute_all(sc))
    assert set(df["evidence_type"]) == {"CALCULATION"}
    assert df.loc[df.candidate.str.contains("Hybrid G"), "crr_evidence"].iloc[0] == "TARGET"
    assert df.loc[df.candidate.str.contains("Hybrid G"), "status"].iloc[0].startswith("UNVERIFIED")
