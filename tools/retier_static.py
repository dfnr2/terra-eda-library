#!/usr/bin/env python3
"""Promote static/curated tables to tier 0.

Every non-parametric table defaults to tier 5 (the schema default for migrated/
CERN imports). The HTTP server's default `tier <= 2` cutoff would otherwise hide
all of them. This sets tier=0 on every tiered table except the parametric set
(resistors_smt, capacitors_smt), which carry deliberately-assigned tiers.
"""
import sqlite3
import sys
from typing import Iterable


def tables_with_tier(conn: sqlite3.Connection) -> list[str]:
    """Names of non-sqlite tables that have a `tier` column."""
    out = []
    for (name,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{name}")')]
        if "tier" in cols:
            out.append(name)
    return out


def retier_static(conn: sqlite3.Connection, parametric: Iterable[str]) -> dict[str, int]:
    """Set tier=0 on every tiered table not in `parametric`. Returns {table: rows_changed}."""
    parametric = set(parametric)
    promoted: dict[str, int] = {}
    for table in tables_with_tier(conn):
        if table in parametric:
            continue
        cur = conn.execute(f'UPDATE "{table}" SET tier = 0 WHERE tier IS NOT 0')
        if cur.rowcount:
            promoted[table] = cur.rowcount
    conn.commit()
    return promoted


def main() -> None:
    db_path = sys.argv[1]
    parametric = sys.argv[2:]
    conn = sqlite3.connect(db_path)
    promoted = retier_static(conn, parametric)
    for table, n in sorted(promoted.items()):
        print(f"  re-tiered {table}: {n} rows -> tier 0")
    conn.close()


if __name__ == "__main__":
    main()
