#!/usr/bin/env python3
"""Audit the on-disk datasheet store against the committed acquisition log.

Checks, without mutating anything:
  - every `ok`/`quarantine` log record's sha256 has a real file (in files/ resp.
    quarantine/) whose content hash matches its name;
  - no orphan files on disk that no log record references;
  - summarizes status counts.

Exit non-zero if any integrity problem is found (corrupt/missing/orphan).

Usage: python3 tools/datasheets/audit.py
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "assets/datasheets/acquisition.jsonl"
FILES = ROOT / "assets/datasheets/files"
QUAR = ROOT / "assets/datasheets/quarantine"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main() -> None:
    records = []
    if LOG.exists():
        records = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    problems = []
    referenced: set[str] = set()
    for r in records:
        st, h = r.get("status"), r.get("sha256")
        if st not in ("ok", "quarantine"):
            continue
        if not h:
            problems.append(f"{r['filename']}: status {st} but no sha256")
            continue
        referenced.add(h)
        d = FILES if st == "ok" else QUAR
        f = d / f"{h}.pdf"
        if not f.exists():
            problems.append(f"{r['filename']}: {st} file missing ({f.relative_to(ROOT)})")
        elif sha256(f) != h:
            problems.append(f"{r['filename']}: content hash != filename ({f.relative_to(ROOT)})")
    # orphan files (on disk, not referenced by any record)
    for d in (FILES, QUAR):
        if d.exists():
            for f in d.glob("*.pdf"):
                if f.stem not in referenced:
                    problems.append(f"orphan file (no log record): {f.relative_to(ROOT)}")
    by = {}
    for r in records:
        by[r.get("status")] = by.get(r.get("status"), 0) + 1
    print(f"log records: {len(records)}  by status: {dict(sorted(by.items()))}")
    print(f"referenced hashes: {len(referenced)}")
    if problems:
        print(f"\nPROBLEMS ({len(problems)}):")
        for p in problems[:50]:
            print(f"  - {p}")
        sys.exit(1)
    print("audit OK: store and log consistent.")


if __name__ == "__main__":
    main()
