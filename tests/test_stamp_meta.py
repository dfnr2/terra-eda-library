"""Tests for tools/stamp_meta.py — the terra_meta build-identity stamp."""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import stamp_meta as sm  # noqa: E402


def _read(db):
    conn = sqlite3.connect(str(db))
    try:
        return {k: v for k, v in conn.execute("SELECT key, value FROM terra_meta")}
    finally:
        conn.close()


def test_stamp_creates_terra_meta(tmp_path):
    db = tmp_path / "x.db"
    sqlite3.connect(str(db)).close()
    sm.stamp(db, "v1.0.0", "deadbeef", "2026-06-15T00:00:00Z")
    assert _read(db) == {
        "version": "v1.0.0",
        "git_commit": "deadbeef",
        "built_at": "2026-06-15T00:00:00Z",
    }


def test_stamp_overwrites_idempotently(tmp_path):
    db = tmp_path / "x.db"
    sqlite3.connect(str(db)).close()
    sm.stamp(db, "v1", "aaa", "t1")
    sm.stamp(db, "v2", "bbb", "t2")  # no PRIMARY KEY error; latest values win
    assert _read(db) == {"version": "v2", "git_commit": "bbb", "built_at": "t2"}


def test_git_version_is_nonempty_string():
    v = sm.git_version()
    assert isinstance(v, str) and v != ""
