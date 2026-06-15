"""Stamp build identity into the parts DB as a ``terra_meta`` key/value table.

The database carries no version of its own otherwise (``PRAGMA user_version`` is
unused and ``standards_version`` is a per-row data convention, not a build
stamp). The master build calls this last so ``db/terra.db`` records which library
version / commit produced it — used for distribution and as the value the HTTP
server exposes at ``/v1/meta.json``.
"""
from __future__ import annotations

import argparse
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> str:
    """Run ``git -C repo <args>`` and return stdout stripped, or '' on failure."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def git_version(repo: Path = ROOT) -> str:
    """``git describe --tags --always --dirty``; 'unknown' outside a git repo."""
    return _git(repo, "describe", "--tags", "--always", "--dirty") or "unknown"


def git_commit(repo: Path = ROOT) -> str:
    """Full HEAD SHA; 'unknown' outside a git repo."""
    return _git(repo, "rev-parse", "HEAD") or "unknown"


def stamp(db_path, version: str, commit: str, built_at: str) -> None:
    """(Re)write the terra_meta table with the given build identity (idempotent)."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("DROP TABLE IF EXISTS terra_meta")
        conn.execute("CREATE TABLE terra_meta (key TEXT PRIMARY KEY, value TEXT)")
        conn.executemany(
            "INSERT INTO terra_meta (key, value) VALUES (?, ?)",
            [("version", version), ("git_commit", commit), ("built_at", built_at)],
        )
        conn.commit()
    finally:
        conn.close()


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Stamp terra_meta build identity into the DB.")
    ap.add_argument("--db", default="db/terra.db")
    ap.add_argument("--version", help="override (default: git describe)")
    ap.add_argument("--commit", help="override (default: git HEAD sha)")
    ap.add_argument("--built-at", help="override (default: now, UTC ISO-8601)")
    a = ap.parse_args(argv)
    version = a.version or git_version()
    commit = a.commit or git_commit()
    built_at = a.built_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stamp(a.db, version, commit, built_at)
    print(f"stamped terra_meta: version={version} commit={commit[:12]} built_at={built_at}")


if __name__ == "__main__":
    main()
