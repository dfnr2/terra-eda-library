#!/usr/bin/env python3
"""Build the unique-datasheet work-list from the built terra.db.

A datasheet is shared by many parts, so the fetch unit is the unique CERN
`datasheet` filename, not the part. Output: build/worklist.json — a JSON array of
{filename, manufacturer, mpns[<=3], part_count}, sorted by filename (deterministic).

Native tables already store full datasheet URLs; they are handled separately (not
here). This work-list is the CERN filename-keyed gap.

Usage: python3 tools/datasheets/build_worklist.py [db/terra.db]
"""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def build(db_path: str) -> list[dict]:
    con = sqlite3.connect(db_path)
    cern = [n for (n,) in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name LIKE 'cern_%' AND name NOT LIKE '%\\_v' ESCAPE '\\'")]
    work: dict[str, dict] = {}
    for t in cern:
        for ds, mfr, mpn in con.execute(
                f"SELECT datasheet, manufacturer, mpn FROM {t} "
                "WHERE datasheet != '' AND datasheet IS NOT NULL"):
            ds = (ds or "").strip()
            if not ds or ds.lower() == "none":
                continue
            e = work.setdefault(ds, {"filename": ds, "manufacturer": mfr,
                                     "mpns": set(), "part_count": 0})
            e["mpns"].add(mpn)
            e["part_count"] += 1
    out = []
    for ds in sorted(work):
        e = work[ds]
        e["mpns"] = sorted(e["mpns"])[:3]
        out.append(e)
    return out


def main() -> None:
    db = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "db/terra.db")
    out = build(db)
    dest = ROOT / "build/worklist.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=0))
    print(f"wrote {dest.relative_to(ROOT)}: {len(out)} unique datasheets, "
          f"{sum(e['part_count'] for e in out)} part references")


if __name__ == "__main__":
    main()
