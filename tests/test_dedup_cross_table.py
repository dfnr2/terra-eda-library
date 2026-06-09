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
    dropped = dedup(
        conn,
        {"3M-P50E-100P1-SR1-EA": "cern_3m"},
        part_tables=["cern_3m", "cern_sockets"],
    )
    # kept in canonical, removed from the other
    assert conn.execute("SELECT COUNT(*) FROM cern_3m WHERE unique_id='3M-P50E-100P1-SR1-EA'").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM cern_sockets WHERE unique_id='3M-P50E-100P1-SR1-EA'").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM cern_sockets WHERE unique_id='OTHER'").fetchone()[0] == 1
    assert dropped["3M-P50E-100P1-SR1-EA"] == ["cern_sockets"]


def test_dedup_does_not_touch_non_part_tables():
    """dedup must spare infra tables like `tags` that also carry unique_id."""
    conn = sqlite3.connect(":memory:")
    for t in ("cern_3m", "cern_sockets"):
        conn.execute(f"CREATE TABLE {t} (unique_id TEXT, mpn TEXT)")
    conn.execute("CREATE TABLE tags (unique_id TEXT, tag TEXT)")
    conn.execute("INSERT INTO cern_3m VALUES ('3M-P50E-100P1-SR1-EA', 'x')")
    conn.execute("INSERT INTO cern_sockets VALUES ('3M-P50E-100P1-SR1-EA', 'x')")
    conn.execute("INSERT INTO tags VALUES ('3M-P50E-100P1-SR1-EA', 'connector')")
    conn.commit()
    dedup(
        conn,
        {"3M-P50E-100P1-SR1-EA": "cern_3m"},
        part_tables=["cern_3m", "cern_sockets"],
    )
    # dropped from the non-canonical part table
    assert conn.execute("SELECT COUNT(*) FROM cern_sockets WHERE unique_id='3M-P50E-100P1-SR1-EA'").fetchone()[0] == 0
    # kept in canonical part table
    assert conn.execute("SELECT COUNT(*) FROM cern_3m WHERE unique_id='3M-P50E-100P1-SR1-EA'").fetchone()[0] == 1
    # infra table untouched
    assert conn.execute("SELECT COUNT(*) FROM tags WHERE unique_id='3M-P50E-100P1-SR1-EA'").fetchone()[0] == 1
