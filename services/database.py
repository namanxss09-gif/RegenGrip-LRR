"""SQLite persistence (parameterised SQL only). Auto-initialises; tolerates malformed JSON rows."""
import json, sqlite3
from datetime import datetime
from models.tyre import Candidate, demo_candidates

SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, version TEXT,
  is_demo INTEGER DEFAULT 0, data TEXT NOT NULL, created TEXT, updated TEXT);
CREATE TABLE IF NOT EXISTS scenarios(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, app_version TEXT,
  created TEXT, data TEXT NOT NULL, results TEXT);
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT);
"""

def _conn(path):
    c = sqlite3.connect(path); c.row_factory = sqlite3.Row; return c

def _now(): return datetime.now().isoformat(timespec="seconds")

def init_db(path):
    with _conn(path) as c: c.executescript(SCHEMA)

def seed_demo(path):
    """Insert built-in demo candidates only if absent (never overwrites)."""
    with _conn(path) as c:
        for cand in demo_candidates():
            c.execute("INSERT OR IGNORE INTO candidates(name,version,is_demo,data,created,updated) VALUES(?,?,?,?,?,?)",
                      (cand.name, cand.version, 1, json.dumps(cand.to_dict()), _now(), _now()))

def reset_demo(path, confirm=False):
    """Restore built-in demo candidates to defaults. Requires confirm=True. User candidates and scenarios untouched."""
    if not confirm: raise PermissionError("Confirmation required")
    with _conn(path) as c:
        for cand in demo_candidates():
            c.execute("INSERT INTO candidates(name,version,is_demo,data,created,updated) VALUES(?,?,?,?,?,?) "
                      "ON CONFLICT(name) DO UPDATE SET data=excluded.data, updated=excluded.updated, is_demo=1",
                      (cand.name, cand.version, 1, json.dumps(cand.to_dict()), _now(), _now()))

def _row_to_cand(r):
    try:
        c = Candidate.from_dict(json.loads(r["data"])); c.db_id = r["id"]; return c
    except (ValueError, TypeError):
        return None   # malformed record skipped

def list_candidates(path):
    with _conn(path) as c: rows = c.execute("SELECT * FROM candidates ORDER BY id").fetchall()
    return [x for x in (_row_to_cand(r) for r in rows) if x is not None]

def save_candidate(path, cand):
    """Insert or update by name; returns id."""
    d = json.dumps(cand.to_dict())
    with _conn(path) as c:
        c.execute("INSERT INTO candidates(name,version,is_demo,data,created,updated) VALUES(?,?,?,?,?,?) "
                  "ON CONFLICT(name) DO UPDATE SET version=excluded.version, data=excluded.data, updated=excluded.updated",
                  (cand.name, cand.version, int(cand.is_demo), d, cand.created, _now()))
        return c.execute("SELECT id FROM candidates WHERE name=?", (cand.name,)).fetchone()["id"]

def rename_candidate(path, old, cand):
    with _conn(path) as c:
        c.execute("UPDATE candidates SET name=?, version=?, data=?, updated=? WHERE name=?",
                  (cand.name, cand.version, json.dumps(cand.to_dict()), _now(), old))

def delete_candidate(path, name):
    with _conn(path) as c: return c.execute("DELETE FROM candidates WHERE name=?", (name,)).rowcount

def duplicate_candidate(path, name):
    src = next((c for c in list_candidates(path) if c.name == name), None)
    if src is None: raise KeyError(name)
    names = {c.name for c in list_candidates(path)}
    n, i = f"{name} (copy)", 2
    while n in names: n, i = f"{name} (copy {i})", i + 1
    d = src.to_dict(); d.update(name=n, is_demo=False, is_baseline=False, db_id=None)
    new = Candidate.from_dict(d); save_candidate(path, new); return new

def save_scenario(path, scenario, results=None):
    with _conn(path) as c:
        cur = c.execute("INSERT INTO scenarios(name,app_version,created,data,results) VALUES(?,?,?,?,?)",
                        (scenario["name"], scenario.get("app_version"), _now(), json.dumps(scenario), json.dumps(results, default=str)))
        return cur.lastrowid

def list_scenarios(path):
    with _conn(path) as c:
        return [dict(r) for r in c.execute("SELECT id,name,app_version,created FROM scenarios ORDER BY id DESC").fetchall()]

def load_scenario(path, sid):
    with _conn(path) as c: r = c.execute("SELECT data FROM scenarios WHERE id=?", (sid,)).fetchone()
    if r is None: return None
    try: return json.loads(r["data"])
    except ValueError: return None

def load_results(path, sid):
    with _conn(path) as c: r = c.execute("SELECT results FROM scenarios WHERE id=?", (sid,)).fetchone()
    try: return json.loads(r["results"]) if r and r["results"] else None
    except ValueError: return None

def delete_scenario(path, sid):
    with _conn(path) as c: return c.execute("DELETE FROM scenarios WHERE id=?", (sid,)).rowcount
