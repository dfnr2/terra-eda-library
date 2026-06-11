#!/usr/bin/env python3
"""Propose manufacturer switches for commodity-equivalent datasheets, as a reviewable
org-mode control surface + a machine-readable detail file.

When the commodity tier attached a Diodes Inc / TI datasheet to a part whose CERN
manufacturer differs, the datasheet no longer matches the part. The fix is to switch
the part to the major manufacturer whose datasheet we used. This tool builds the
proposed switches, precision-verifies each (does the datasheet text actually name the
MPN/base?), groups the obvious ones by (manufacturer, family) for pattern-approval,
flags collapse/merge groups, and isolates precision failures for individual review.

Outputs:
  manufacturer-switch-review.org   — human control surface (edit the Approve/Decision cols)
  build/proposed_switches.json     — full per-row detail for apply_switches.py

Usage: python3 tools/datasheets/propose_switches.py
"""
from __future__ import annotations
import json
import re
import sqlite3
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "assets/datasheets/acquisition.jsonl"
FILES = ROOT / "assets/datasheets/files"
DB = ROOT / "db/terra.db"
ORG = ROOT / "manufacturer-switch-review.org"
JSON = ROOT / "build/proposed_switches.json"

FAMILY_RE = re.compile(
    r"^(1N|2N|BAV|BAT|BAS|BAW|BZX|BZV|BZY|BB|MMBT|MMBD|MMBZ|MMSD|PMBT|BC|BSS|1PS|"
    r"MBR|SS|74|54|CD4|HEF4|MC14|LM|LF|NE5|TL|LMV|LMC|TLV|ICL|ICM)", re.I)


def family(mpn: str) -> str:
    m = FAMILY_RE.match(mpn)
    return (m.group(1).upper() if m else "other")


def base(mpn: str) -> str:
    s = mpn.upper()
    s = re.sub(r"-NOPB$|-E3.*$|-7$|G$", "", s)
    m = re.match(r"^(.*\d)[A-Z]{1,4}$", s)
    return m.group(1) if m else s


_text_cache: dict[str, str] = {}


def names_part(sha: str, mpn: str) -> bool:
    if sha not in _text_cache:
        f = FILES / f"{sha}.pdf"
        try:
            _text_cache[sha] = subprocess.run(
                ["pdftotext", "-l", "3", str(f), "-"], capture_output=True,
                text=True, timeout=30).stdout.upper()
        except Exception:
            _text_cache[sha] = ""
    txt = _text_cache[sha]
    return bool(txt) and (mpn.upper() in txt or base(mpn) in txt)


def main() -> None:
    log = [json.loads(l) for l in LOG.read_text().splitlines() if l.strip()]
    equiv = {}  # filename -> (new_mfr, sha256)
    for r in log:
        if r["status"] == "ok" and "equivalent" in r.get("source", ""):
            new = "Diodes Incorporated" if "Diodes" in r["source"] else "Texas Instruments"
            equiv[r["filename"]] = (new, r["sha256"])

    con = sqlite3.connect(DB)
    cern = [n for (n,) in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cern_%' "
        "AND name NOT LIKE '%\\_v' ESCAPE '\\'")]
    rows = []  # full detail
    for t in cern:
        for ds, uid, mpn, mfr in con.execute(
                f"SELECT datasheet, unique_id, mpn, manufacturer FROM {t}"):
            if ds in equiv and mfr.upper() not in equiv[ds][0].upper():
                new, sha = equiv[ds]
                rows.append({"table": t, "unique_id": uid, "mpn": mpn,
                             "old_mfr": mfr, "new_mfr": new, "sha256": sha,
                             "family": family(mpn), "new_uid": f"{new}-{mpn}",
                             "verified": names_part(sha, mpn)})
    JSON.parent.mkdir(parents=True, exist_ok=True)
    JSON.write_text(json.dumps(rows, indent=1))

    # partition: merges (new_uid used >1), precision-fails, clean
    byuid = defaultdict(list)
    for r in rows:
        byuid[r["new_uid"]].append(r)
    merge_uids = {k for k, v in byuid.items() if len(v) > 1}
    clean = [r for r in rows if r["new_uid"] not in merge_uids and r["verified"]]
    fails = [r for r in rows if r["new_uid"] not in merge_uids and not r["verified"]]

    # pattern groups for clean switches
    patt = defaultdict(lambda: {"n": 0, "ex": []})
    for r in clean:
        g = patt[(r["new_mfr"], r["family"])]
        g["n"] += 1
        if len(g["ex"]) < 3:
            g["ex"].append(r["mpn"])

    def cell(s):
        return str(s).replace("|", "/")

    out = ["#+TITLE: Manufacturer Switch Review (commodity-equivalent datasheets)",
           f"#+SUMMARY: {len(rows)} switches — {len(clean)} clean / "
           f"{sum(len(byuid[u]) for u in merge_uids)} in {len(merge_uids)} merges / "
           f"{len(fails)} precision-fail",
           "",
           "* Pattern switches  (uncheck [ ] to VETO a whole family; all precision-verified)",
           "| Approve | N | New Manufacturer | Family | Examples |",
           "|---------+---+------------------+--------+----------|"]
    for (nm, fam), g in sorted(patt.items(), key=lambda x: -x[1]["n"]):
        out.append(f"| [X] | {g['n']} | {cell(nm)} | {fam}* | {cell(', '.join(g['ex']))} |")

    out += ["",
            "* Merges  (Decision: merge | keep | skip ; collapses >1 CERN row into one part)",
            "| Decision | Target unique_id | Rows | Source manufacturers |",
            "|----------+------------------+------+----------------------|"]
    for u in sorted(merge_uids):
        srcs = ", ".join(sorted({f"{r['old_mfr']}" for r in byuid[u]}))
        out.append(f"| merge | {cell(u)} | {len(byuid[u])} | {cell(srcs)} |")

    out += ["",
            "* Precision exceptions  (datasheet text did NOT name the part — check [X] to switch anyway)",
            "| Approve | unique_id | mpn | datasheet sha (12) | new mfr |",
            "|---------+-----------+-----+--------------------+---------|"]
    for r in fails:
        out.append(f"| [ ] | {cell(r['unique_id'])} | {cell(r['mpn'])} | "
                   f"{r['sha256'][:12]} | {cell(r['new_mfr'])} |")
    out.append("")
    ORG.write_text("\n".join(out))
    print(f"wrote {ORG.relative_to(ROOT)}  ({len(rows)} switches: {len(clean)} clean, "
          f"{len(merge_uids)} merge groups, {len(fails)} precision-fail)")
    print(f"wrote {JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
