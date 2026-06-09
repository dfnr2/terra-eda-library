import sqlite3
from tools.retier_static import retier_static, tables_with_tier


def _make_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE cern_x (unique_id TEXT PRIMARY KEY, tier INTEGER DEFAULT 5);
        INSERT INTO cern_x (unique_id) VALUES ('a'), ('b');
        CREATE TABLE resistors_smt (unique_id TEXT PRIMARY KEY, tier INTEGER);
        INSERT INTO resistors_smt VALUES ('r0', 0), ('r3', 3);
        CREATE TABLE tags (unique_id TEXT, tag TEXT);
        """
    )
    conn.commit()
    return conn


def test_tables_with_tier_excludes_non_tier_tables():
    conn = _make_db()
    assert set(tables_with_tier(conn)) == {"cern_x", "resistors_smt"}


def test_retier_promotes_static_but_not_parametric():
    conn = _make_db()
    promoted = retier_static(conn, parametric=["resistors_smt"])
    assert [r[0] for r in conn.execute("SELECT tier FROM cern_x")] == [0, 0]
    assert promoted["cern_x"] == 2
    assert sorted(r[0] for r in conn.execute("SELECT tier FROM resistors_smt")) == [0, 3]
    assert "resistors_smt" not in promoted
