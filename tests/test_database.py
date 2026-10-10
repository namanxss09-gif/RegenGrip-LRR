import json, sqlite3, pytest
from services import database as D
from models.tyre import Candidate
from models.scenario import build_scenario, compute_all
from models.vehicle import Vehicle
from config.defaults import DEFAULT_CONSTRAINTS, DEFAULT_WEIGHTS

@pytest.fixture
def db(tmp_path):
    p = str(tmp_path / "t.db"); D.init_db(p); D.seed_demo(p); return p

def test_init_and_seed(db): assert len(D.list_candidates(db)) == 4

def test_save_update_delete(db):
    c = Candidate(name="X", crr=0.011); D.save_candidate(db, c)
    assert next(x for x in D.list_candidates(db) if x.name == "X").crr == 0.011
    c.crr = 0.010; D.save_candidate(db, c)
    assert next(x for x in D.list_candidates(db) if x.name == "X").crr == 0.010
    assert D.delete_candidate(db, "X") == 1

def test_duplicate(db):
    n = D.duplicate_candidate(db, "RegenGrip-LRR Hybrid G"); assert n.name.endswith("(copy)") and not n.is_demo
    assert D.duplicate_candidate(db, "RegenGrip-LRR Hybrid G").name.endswith("(copy 2)")

def test_missing_fields_and_malformed(db):
    with sqlite3.connect(db) as c:
        c.execute("INSERT INTO candidates(name,data) VALUES('old','{\"name\":\"old\",\"unknown_field\":1}')")
        c.execute("INSERT INTO candidates(name,data) VALUES('bad','{not json')")
    names = [x.name for x in D.list_candidates(db)]
    assert "old" in names and "bad" not in names
    assert next(x for x in D.list_candidates(db) if x.name == "old").crr is None

def test_scenario_reproducible(db):
    cs = D.list_candidates(db)
    sc = build_scenario("s1", Vehicle(), cs, cs[0].name, DEFAULT_CONSTRAINTS, DEFAULT_WEIGHTS, {"volume": 1000}, {"pct": 10}, [], [])
    r1 = compute_all(sc); sid = D.save_scenario(db, sc, r1)
    sc2 = D.load_scenario(db, sid); r2 = compute_all(sc2)
    assert json.dumps(r1, default=str, sort_keys=True) == json.dumps(r2, default=str, sort_keys=True)
    assert D.list_scenarios(db)[0]["name"] == "s1" and D.delete_scenario(db, sid) == 1 and D.load_scenario(db, sid) is None

def test_reset_demo_requires_confirmation_and_keeps_user_data(db):
    D.save_candidate(db, Candidate(name="mine", crr=0.009))
    sc = build_scenario("keep", Vehicle(), D.list_candidates(db), "Baseline Reference Tyre", DEFAULT_CONSTRAINTS, DEFAULT_WEIGHTS, {}, {}, [], [])
    D.save_scenario(db, sc)
    with pytest.raises(PermissionError): D.reset_demo(db)
    g = next(c for c in D.list_candidates(db) if c.name.endswith("Hybrid G")); g.crr = 0.001; D.save_candidate(db, g)
    D.reset_demo(db, confirm=True)
    assert next(c for c in D.list_candidates(db) if c.name.endswith("Hybrid G")).crr == 0.0108
    assert any(c.name == "mine" for c in D.list_candidates(db)) and len(D.list_scenarios(db)) == 1

def test_sql_injection_safe(db):
    D.save_candidate(db, Candidate(name="x'; DROP TABLE candidates;--")); assert len(D.list_candidates(db)) == 5
