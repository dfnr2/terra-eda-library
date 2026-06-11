#!/usr/bin/env python3
"""Append workflow result records to the committed acquisition log.

Reads a JSON array of result records (the workflow's return value, saved to a
file) and appends them to assets/datasheets/acquisition.jsonl, de-duplicating by
`filename` (last write wins — a retried `error` is superseded by its later result).

The PDFs themselves are written by the fetch agents (content-addressed, gitignored);
this only records the outcome so progress survives across sessions.

Usage: python3 tools/datasheets/ingest.py <results.json>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "assets/datasheets/acquisition.jsonl"
FIELDS = ("filename", "status", "source", "source_tier", "final_url",
          "sha256", "size_bytes", "pages", "mpn_in_doc", "quarantine_reason", "notes")


def load_log() -> dict[str, dict]:
    recs: dict[str, dict] = {}
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                recs[r["filename"]] = r
    return recs


def main() -> None:
    results = json.loads(Path(sys.argv[1]).read_text())
    recs = load_log()
    added = updated = 0
    for r in results:
        if not r or not r.get("filename"):
            continue
        rec = {k: r.get(k) for k in FIELDS if k in r}
        fn = rec["filename"]
        (updated := updated + 1) if fn in recs else (added := added + 1)
        recs[fn] = rec
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("w") as f:
        for fn in sorted(recs):
            f.write(json.dumps(recs[fn]) + "\n")
    by = {}
    for r in recs.values():
        by[r.get("status")] = by.get(r.get("status"), 0) + 1
    print(f"ingested: +{added} new, {updated} updated. log now {len(recs)} records.")
    print("by status:", dict(sorted(by.items())))


if __name__ == "__main__":
    main()
