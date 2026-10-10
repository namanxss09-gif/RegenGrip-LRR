import os, pathlib, pytest
from streamlit.testing.v1 import AppTest
ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGES = sorted((ROOT / "pages").glob("*.py"))

@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("REGENGRIP_DB", str(tmp_path / "ui.db")); monkeypatch.chdir(ROOT)

@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.name)
def test_page_runs_without_exception(page):
    at = AppTest.from_file(str(page), default_timeout=60).run()
    assert not at.exception, [e.value for e in at.exception]

def test_app_navigation_loads():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception, [e.value for e in at.exception]
