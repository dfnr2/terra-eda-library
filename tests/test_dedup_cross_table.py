import sqlite3
from tools.dedup_cross_table import dedup, find_cross_table_duplicates, RESOLUTIONS


def test_resolutions_has_six_entries():
    assert len(RESOLUTIONS) == 6
    assert RESOLUTIONS["SAMTEC-CES-110-01-T-S"] == "cern_samtec"
    assert RESOLUTIONS["TYCO ELECTRONICS-1415044-1"] == "cern_sockets"


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


def test_find_cross_table_duplicates_flags_residual():
    """A uid in two part tables is reported; a uid in one table is not."""
    conn = sqlite3.connect(":memory:")
    for t in ("cern_relays", "cern_sockets"):
        conn.execute(f"CREATE TABLE {t} (unique_id TEXT)")
    conn.execute("INSERT INTO cern_relays VALUES ('DUP')")
    conn.execute("INSERT INTO cern_sockets VALUES ('DUP')")
    conn.execute("INSERT INTO cern_sockets VALUES ('SOLO')")
    conn.commit()
    residual = find_cross_table_duplicates(conn, ["cern_relays", "cern_sockets"])
    assert residual == {"DUP": ["cern_relays", "cern_sockets"]}


def test_find_cross_table_duplicates_clean_after_dedup():
    """After dedup resolves a collision, no residual duplicate remains."""
    conn = sqlite3.connect(":memory:")
    for t in ("cern_relays", "cern_sockets"):
        conn.execute(f"CREATE TABLE {t} (unique_id TEXT)")
    conn.execute("INSERT INTO cern_relays VALUES ('DUP')")
    conn.execute("INSERT INTO cern_sockets VALUES ('DUP')")
    conn.commit()
    dedup(conn, {"DUP": "cern_sockets"}, part_tables=["cern_relays", "cern_sockets"])
    assert find_cross_table_duplicates(conn, ["cern_relays", "cern_sockets"]) == {}
