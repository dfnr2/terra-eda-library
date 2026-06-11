#!/usr/bin/env python3
"""Compute the next chunk of un-fetched datasheets (work-list MINUS the log).

Progress lives in assets/datasheets/acquisition.jsonl (committed, append-only),
one record per completed work item keyed by `filename`. "Done" = any filename with
a terminal status in the log (ok | quarantine | notfound). `error` rows are NOT
done and will be retried.

Writes the next chunk to build/chunk.json and prints counts. The workflow / a
third-party runner consumes build/chunk.json by index.

Usage: python3 tools/datasheets/remaining.py [chunk_size=300]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKLIST = ROOT / "build/worklist.json"
LOG = ROOT / "assets/datasheets/acquisition.jsonl"
CHUNK = ROOT / "build/chunk.json"
DONE_STATUSES = {"ok", "quarantine", "notfound"}


def done_filenames() -> set[str]:
    done = set()
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("status") in DONE_STATUSES:
                done.add(rec["filename"])
    return done


def main() -> None:
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    worklist = json.loads(WORKLIST.read_text())
    done = done_filenames()
    remaining = [w for w in worklist if w["filename"] not in done]
    chunk = remaining[:size]
    CHUNK.write_text(json.dumps(chunk, indent=0))
    print(f"worklist={len(worklist)} done={len(done)} remaining={len(remaining)}")
    print(f"wrote {CHUNK.relative_to(ROOT)}: {len(chunk)} items (chunk size {size})")
    if chunk:
        print(f"first={chunk[0]['filename']}  last={chunk[-1]['filename']}")


if __name__ == "__main__":
    main()
