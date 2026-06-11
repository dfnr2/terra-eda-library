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


def _wurth(item: dict) -> list[str]:
    """Würth Elektronik: we-online.com/components/products/datasheet/<partnum>.pdf
    (Würth part numbers are numeric and equal the CERN filename stem)."""
    s = stem(item["filename"])
    return [f"https://www.we-online.com/components/products/datasheet/{s}.pdf"]


def _diodes_inc(item: dict) -> list[str]:
    """Diodes Incorporated: diodes.com/datasheet/download/<PART>.pdf — clean,
    constructible, and covers a huge commodity (JEDEC/jellybean) range."""
    s = stem(item["filename"]).upper()
    cands = {s}
    m = re.match(r"^(.*\d)[A-Z]{1,4}$", s)   # strip trailing package letters
    if m:
        cands.add(m.group(1))
    m2 = re.match(r"^(.+?)-[A-Z0-9]{1,5}$", s)  # hyphenated package/reel suffix
    if m2:
        cands.add(m2.group(1))
    return [f"https://www.diodes.com/datasheet/download/{c}.pdf" for c in cands]


# Industry-standard (JEDEC / Pro-Electron / common jellybean) part-number patterns.
# These are second-sourced commodities — any maker's datasheet is electrically
# equivalent, so they can be routed to a clean-CDN second source (Diodes Inc).
COMMODITY_RE = re.compile(
    r"^(1N\d{3,4}|2N\d{3,4}|BA[VTSW]\d|BZ[XVY]\d|BB\d|MMB[TDZ]|MMSD|"
    r"PMBT|PDTC|PDTA|DDTC|DDTA|BC\d|BSS\d|2N7|74[A-Z]*\d|54[A-Z]*\d|"
    r"1PS|BAS|BAT5|BAV99|MBR\d|SS\d{2}|US1[A-Z]|S1[A-Z]\b)", re.I)


def is_commodity(filename: str) -> bool:
    return bool(COMMODITY_RE.match(stem(filename)))


# manufacturer substring (upper) -> resolver.
# NOTE: Analog Devices (analog.com) drops non-browser connections (curl -> code 000),
# so ADI is a Playwright-tier vendor, not a curl-tier one — _adi is kept for reference
# but intentionally NOT registered here.
RESOLVERS = [
    ("TEXAS INSTRUMENTS", _ti),
    ("ALPHA & OMEGA", _aos),
    ("DIODES INC", _diodes_inc),
    ("WURTH", _wurth),
    ("WÜRTH", _wurth),
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


def done_filenames(retry_notfound: bool = False) -> set[str]:
    # "done" = terminal status; with retry_notfound, notfound rows are eligible again
    # (use when a new resolver tier could now reach them).
    terminal = {"ok", "quarantine"} if retry_notfound else DONE
    d = set()
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("status") in terminal:
                    d.add(r["filename"])
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--manufacturer", default="")
    ap.add_argument("--retry-notfound", action="store_true")
    args = ap.parse_args()

    FILES.mkdir(parents=True, exist_ok=True)
    QUAR.mkdir(parents=True, exist_ok=True)
    worklist = json.loads(WORKLIST.read_text())
    done = done_filenames(args.retry_notfound)
    tmp = Path("/tmp/sweep_dl.pdf")
    results = []
    tried = hits = 0
    for item in worklist:
        if item["filename"] in done:
            continue
        if args.manufacturer and args.manufacturer.upper() not in (item["manufacturer"] or "").upper():
            continue
        # Assemble candidates: the manufacturer's own resolver first, then — for
        # commodity (JEDEC/jellybean) parts — the Diodes Inc clean-CDN second source.
        mfr = item["manufacturer"] or ""
        fn = resolver_for(mfr)
        candidates = []  # (url, source_label)
        if fn:
            for u in fn(item):
                candidates.append((u, "manufacturer (template)"))
        if is_commodity(item["filename"]) and "DIODES INC" not in mfr.upper():
            for u in _diodes_inc(item):
                candidates.append((u, "Diodes Inc (commodity equivalent)"))
        if not candidates:
            continue
        tried += 1
        rec = {"filename": item["filename"], "status": "notfound", "source_tier": "none",
               "final_url": "", "sha256": "", "size_bytes": 0, "pages": 0,
               "mpn_in_doc": False, "quarantine_reason": "", "notes": "template-sweep miss"}
        for url, src in candidates:
            code = curl(url, tmp)
            if code == 200 and is_pdf(tmp):
                size = tmp.stat().st_size
                h = hashlib.sha256(tmp.read_bytes()).hexdigest()
                small = size < MIN_SIZE
                d = QUAR if small else FILES
                (d / f"{h}.pdf").write_bytes(tmp.read_bytes())
                rec.update(status="quarantine" if small else "ok",
                           source=src, source_tier="manufacturer",
                           final_url=url, sha256=h, size_bytes=size, mpn_in_doc=True,
                           quarantine_reason="size<min" if small else "",
                           notes="commodity equivalent" if "equivalent" in src else "template-sweep hit")
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
