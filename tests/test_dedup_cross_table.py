import sqlite3
from tools.dedup_cross_table import dedup, RESOLUTIONS


def test_resolutions_has_five_entries():
    assert len(RESOLUTIONS) == 5
    assert RESOLUTIONS["SAMTEC-CES-110-01-T-S"] == "cern_samtec"


def test_dedup_keeps_canonical_drops_others():
    conn = sqlite3.connect(":memory:")
    for t in ("cern_3m", "cern_sockets"):
        conn.execute(f"CREATE TABLE {t} (unique_id TEXT, mpn TEXT)")
    conn.execute("INSERT INTO cern_3m VALUES ('3M-P50E-100P1-SR1-EA', 'x')")
    conn.execute("INSERT INTO cern_sockets VALUES ('3M-P50E-100P1-SR1-EA', 'x')")
    conn.execute("INSERT INTO cern_sockets VALUES ('OTHER', 'y')")  # untouched
    conn.commit()
    dropped = dedup(conn, {"3M-P50E-100P1-SR1-EA": "cern_3m"})
    # kept in canonical, removed from the other
    assert conn.execute("SELECT COUNT(*) FROM cern_3m WHERE unique_id='3M-P50E-100P1-SR1-EA'").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM cern_sockets WHERE unique_id='3M-P50E-100P1-SR1-EA'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM cern_sockets WHERE unique_id='OTHER'").fetchone()[0] == 1
    assert dropped["3M-P50E-100P1-SR1-EA"] == ["cern_sockets"]
