import sqlite3
from tools.cern_datasheets import rewrite_datasheets as rw


def _db():
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE cern_diodes (unique_id TEXT, datasheet TEXT)")
    con.execute("INSERT INTO cern_diodes VALUES ('A', '0402ESDA-MLP.pdf')")
    con.execute("INSERT INTO cern_diodes VALUES ('B', 'MISSING.pdf')")
    return con


def test_only_verified_are_rewritten():
    con = _db()
    manifest = {
        "0402ESDA-MLP.pdf": {"verify": "ok",
                              "local_path": "assets/datasheets/cern/0402ESDA-MLP.pdf"},
        "MISSING.pdf": {"verify": "mpn_mismatch", "local_path": ""},
    }
    n = rw.apply(con, "cern_diodes", manifest)
    assert n == 1
    rows = dict(con.execute("SELECT unique_id, datasheet FROM cern_diodes"))
    assert rows["A"] == "assets/datasheets/cern/0402ESDA-MLP.pdf"
    assert rows["B"] == "MISSING.pdf"
