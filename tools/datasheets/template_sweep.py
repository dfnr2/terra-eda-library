#!/usr/bin/env python3
"""Tier-1 datasheet resolver: cheap per-vendor URL sweep (no LLM, no browser).

For manufacturers with a known datasheet-URL scheme, derive candidate URLs from the
CERN filename / MPN, download with curl, validate a real PDF, and store it
content-addressed. Misses are left for the higher tiers (Playwright discovery /
Haiku open-search). Emits records in the same schema as the fetch workflow, so the
existing ingest.py appends them to acquisition.jsonl.

Resolvers return a LIST of candidate URLs (the base-part transform is fuzzy — e.g.
TI needs a prefix and a package-suffix strip that we can't always predict), and the
first candidate that yields a valid PDF wins.

Usage:
  python3 tools/datasheets/template_sweep.py [--limit N] [--manufacturer SUBSTR] > build/results.json
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKLIST = ROOT / "build/worklist.json"
LOG = ROOT / "assets/datasheets/acquisition.jsonl"
FILES = ROOT / "assets/datasheets/files"
QUAR = ROOT / "assets/datasheets/quarantine"
MIN_SIZE = 20000
DONE = {"ok", "quarantine", "notfound"}


def stem(filename: str) -> str:
    return re.sub(r"\.pdf$", "", filename, flags=re.I)


def _ti(item: dict) -> list[str]:
    """TI: ti.com/lit/ds/symlink/<base>.pdf (and /lit/gpn/<base>). The base-part
    transform is fuzzy, so emit several candidates and let the first valid PDF win:
    strip the -NOPB RoHS tag and trailing package codes, and (for bare-number
    74-series) try the sn/cd family prefixes."""
    s = stem(item["filename"]).lower()
    s = re.sub(r"-nopb$", "", s)            # RoHS marker
    s = re.sub(r"-q1[a-z]*$", "-q1", s)     # automotive: keep -q1, drop reel letters
    cores = {s}
    m = re.match(r"^(.*\d)[a-z]{1,5}$", s)  # trailing package letters (acf2101bu -> acf2101)
    if m:
        cores.add(m.group(1))
    m2 = re.match(r"^(.+?)-[a-z0-9]{1,4}$", s)  # hyphenated package/reel suffix
    if m2:
        cores.add(m2.group(1))
    prefixed = set()
    for c in list(cores):
        if c[:2] == "74":                   # 74-series live under sn/cd prefixes
            prefixed.add("sn" + c)
            prefixed.add("cd" + c)
    cores |= prefixed
    cands = []
    for c in cores:
        cands.append(f"https://www.ti.com/lit/ds/symlink/{c}.pdf")
    for c in cores:
        cands.append(f"https://www.ti.com/lit/gpn/{c}")
    return cands


def _aos(item: dict) -> list[str]:
    """Alpha & Omega: aosmd.com/pdfs/datasheet/<exact filename>."""
    return [f"http://www.aosmd.com/pdfs/datasheet/{item['filename']}"]


def _adi(item: dict) -> list[str]:
    """Analog Devices: analog.com/.../data-sheets/<part>.pdf (case-preserved)."""
    s = stem(item["filename"])
    base = "https://www.analog.com/media/en/technical-documentation/data-sheets"
    return [f"{base}/{s}.pdf", f"{base}/{s.upper()}.pdf"]


# manufacturer substring (upper) -> resolver
RESOLVERS = [
    ("TEXAS INSTRUMENTS", _ti),
    ("ALPHA & OMEGA", _aos),
    ("ANALOG DEVICES", _adi),
]


def resolver_for(mfr: str):
    u = (mfr or "").upper()
    for key, fn in RESOLVERS:
        if key in u:
            return fn
    return None


def curl(url: str, dest: Path) -> int:
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "30", "-A", "Mozilla/5.0",
                        "-o", str(dest), "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip() or 0)
    except ValueError:
        return 0


def is_pdf(p: Path) -> bool:
    return p.exists() and p.stat().st_size > 0 and p.read_bytes()[:5] == b"%PDF-"


def done_filenames() -> set[str]:
    d = set()
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("status") in DONE:
                    d.add(r["filename"])
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--manufacturer", default="")
    args = ap.parse_args()

    FILES.mkdir(parents=True, exist_ok=True)
    QUAR.mkdir(parents=True, exist_ok=True)
    worklist = json.loads(WORKLIST.read_text())
    done = done_filenames()
    tmp = Path("/tmp/sweep_dl.pdf")
    results = []
    tried = hits = 0
    for item in worklist:
        if item["filename"] in done:
            continue
        if args.manufacturer and args.manufacturer.upper() not in (item["manufacturer"] or "").upper():
            continue
        fn = resolver_for(item["manufacturer"])
        if not fn:
            continue
        tried += 1
        rec = {"filename": item["filename"], "status": "notfound", "source_tier": "none",
               "final_url": "", "sha256": "", "size_bytes": 0, "pages": 0,
               "mpn_in_doc": False, "quarantine_reason": "", "notes": "template-sweep miss"}
        for url in fn(item):
            code = curl(url, tmp)
            if code == 200 and is_pdf(tmp):
                size = tmp.stat().st_size
                h = hashlib.sha256(tmp.read_bytes()).hexdigest()
                small = size < MIN_SIZE
                d = QUAR if small else FILES
                (d / f"{h}.pdf").write_bytes(tmp.read_bytes())
                rec.update(status="quarantine" if small else "ok",
                           source="manufacturer (template)", source_tier="manufacturer",
                           final_url=url, sha256=h, size_bytes=size, mpn_in_doc=True,
                           quarantine_reason="size<min" if small else "",
                           notes="template-sweep hit")
                hits += 1
                break
        results.append(rec)
        if args.limit and tried >= args.limit:
            break
    if tmp.exists():
        tmp.unlink()
    json.dump(results, sys.stdout)
    print(f"\n# tried={tried} hits={hits} ({100*hits//max(tried,1)}%)", file=sys.stderr)


if __name__ == "__main__":
    main()
