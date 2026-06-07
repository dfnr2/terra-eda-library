import os
import pytest
from tools import cern_source


def test_default_path_points_at_sibling_repo():
    p = cern_source.cern_db_path()
    assert p.name == "CERN.sqlite"
    assert p.parent.name == "cern-kicad-libs"


def test_env_override(monkeypatch):
    monkeypatch.setenv("CERN_SQLITE", "/tmp/override/CERN.sqlite")
    assert str(cern_source.cern_db_path()) == "/tmp/override/CERN.sqlite"


def test_rows_reads_diodes():
    if not cern_source.cern_db_path().exists():
        pytest.skip("CERN.sqlite not present")
    rows = list(cern_source.rows("Diodes"))
    assert len(rows) == 962
    assert isinstance(rows[0], dict)
    assert "Manufacturer Part Number" in rows[0]
