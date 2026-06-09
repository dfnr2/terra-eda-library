#!/usr/bin/env python3
"""Resolve cross-table duplicate unique_ids during the db build.

A handful of unique_ids appear in more than one part table. The HTTP server's
`build_id_map` treats unique_id as globally unique and raises ValueError when it
sees the same id in two tables. For each such id we keep the row in one canonical
table and delete it from every other table, making unique_id globally unique.
"""
import sqlite3
import sys
from collections.abc import Iterable

# unique_id -> canonical table that KEEPS the row; deleted everywhere else.
RESOLUTIONS: dict[str, str] = {
    "3M-P50E-100P1-SR1-EA": "cern_3m",
    "MURATA POWER SOLUTIONS-OKI-78SR-3.3/1.5-W36H-C": "cern_regulators",
    "Broadcom-ASMT-SWB5-NW703": "leds",
    "NXP SEMICONDUCTORS-SC18IM700IPW": "cern_analog_interface",
    "SAMTEC-CES-110-01-T-S": "cern_samtec",
}


def tables_with_unique_id(conn: sqlite3.Connection) -> list[str]:
    """Names of non-sqlite tables that have a `unique_id` column."""
    out = []
    for (name,) in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ):
        cols = [r[1] for r in conn.execute(f'PRAGMA table_info("{name}")')]
        if "unique_id" in cols:
            out.append(name)
    return out


def dedup(
    conn: sqlite3.Connection,
    resolutions: dict[str, str],
    part_tables: Iterable[str],
) -> dict[str, list[str]]:
    """Delete each duplicate unique_id from every part table except its canonical one.

    For each (uid, keep_table) in `resolutions`, delete uid from every table in
    `part_tables` that is not keep_table and currently contains it. Returns
    {uid: [tables_dropped_from]}, omitting uids where nothing was dropped. If
    keep_table holds no row for the uid, the deletions still happen (a warning
    is printed) so the build does not crash.

    Only `part_tables` are scanned. Infra tables that also carry a unique_id
    column — notably the `tags` join table — must be spared, or the kept
    canonical row would lose its tag associations.
    """
    tables = list(part_tables)
    dropped: dict[str, list[str]] = {}
    for uid, keep_table in resolutions.items():
        kept = conn.execute(
            f'SELECT COUNT(*) FROM "{keep_table}" WHERE unique_id = ?', (uid,)
        ).fetchone()[0]
        if not kept:
            print(f"  warning: {uid} not present in canonical table {keep_table}")
        removed_from: list[str] = []
        for table in tables:
            if table == keep_table:
                continue
            cur = conn.execute(
                f'DELETE FROM "{table}" WHERE unique_id = ?', (uid,)
            )
            if cur.rowcount:
                removed_from.append(table)
        if removed_from:
            dropped[uid] = removed_from
    conn.commit()
    return dropped


def main() -> None:
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tools.terra_server import load_spec

    db = sys.argv[1]
    conn = sqlite3.connect(db)
    # Confine dedup to the dbl part base tables; infra tables like `tags` are
    # never in this list and so keep their unique_id rows intact.
    part_tables = [s["base_table"] for s in load_spec("terra.kicad_dbl")]
    dropped = dedup(conn, RESOLUTIONS, part_tables)
    for uid, tables in dropped.items():
        print(f"  deduped {uid}: dropped from {', '.join(tables)}")
    conn.close()


if __name__ == "__main__":
    main()
