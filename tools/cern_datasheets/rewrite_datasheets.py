"""Rewrite cern_<t>.datasheet to local asset paths for verified datasheets."""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = _ROOT / "assets/datasheets/cern/manifest.json"


def apply(con: sqlite3.Connection, table: str, manifest: dict) -> int:
    count = 0
    for fn, entry in manifest.items():
        if entry.get("verify") == "ok" and entry.get("local_path"):
            cur = con.execute(
                f"UPDATE {table} SET datasheet = ? WHERE datasheet = ?",
                (entry["local_path"], fn))
            count += cur.rowcount
    con.commit()
    return count


def main(table: str = "cern_diodes") -> None:
    manifest = json.loads(MANIFEST.read_text())
    db = _ROOT / "db" / f"{table}.db"
    con = sqlite3.connect(db)
    try:
        n = apply(con, table, manifest)
    finally:
        con.close()
    print(f"+ rewrote {n} datasheet paths in {db}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cern_diodes")
