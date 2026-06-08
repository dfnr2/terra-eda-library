#!/usr/bin/env python3
"""Set the footprint type attribute (smd / through_hole) on terra-owned footprints.

The CERN -> KiCad conversion left the copied footprints with no `(attr …)` type,
so KiCad shows every one as an "Other/Virtual" footprint (excluded from position
files, etc.). The pads themselves are correctly typed, so the real footprint type
is derived from them:

    any thru_hole pad        -> through_hole
    else any smd pad         -> smd
    else (NPTH/graphical)    -> left unset

This EDITS the committed terra `.kicad_mod` files in place (terra owns them); it
is a maintenance tool, idempotent/re-runnable. It also reports anomalies — a
footprint whose derived type disagrees with the lib it lives in (smd vs thd) —
which flags a footprint filed in the wrong CERN library.

Usage: uv run python tools/fix_footprint_attrs.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_PAD_TYPE = re.compile(r'\(pad\s+"[^"]*"\s+(\S+)')
_ATTR = re.compile(r'(^[ \t]*)\(attr\s+([^)]*)\)', re.M)
# A top-level (descr "…") line; the quoted text may contain parens/commas.
_DESCR = re.compile(r'^[ \t]*\(descr\s+"(?:[^"\\]|\\.)*"\s*\)[ \t]*$', re.M)


def footprint_type(txt: str) -> str | None:
    types = {m.group(1) for m in _PAD_TYPE.finditer(txt)}
    if "thru_hole" in types:
        return "through_hole"
    if "smd" in types:
        return "smd"
    return None


def fix(txt: str) -> tuple[str, bool]:
    """Return (new_text, changed) with the correct `(attr <type> …)` set."""
    ftype = footprint_type(txt)
    if ftype is None:
        return txt, False
    m = _ATTR.search(txt)
    if m:
        flags = [f for f in m.group(2).split() if f not in ("smd", "through_hole")]
        new = f'{m.group(1)}(attr {" ".join([ftype] + flags)})'
        if new == m.group(0):
            return txt, False
        return txt[:m.start()] + new + txt[m.end():], True
    d = _DESCR.search(txt)
    if not d:
        return txt, False                 # no anchor; skip (very rare)
    return txt[:d.end()] + f"\n\t(attr {ftype})" + txt[d.end():], True


def run(dry_run: bool) -> None:
    changed = Counter()
    anomalies = []
    for pretty in sorted(ROOT.glob("kicad_footprints/cern-*.pretty")):
        lib = pretty.name
        lib_is_thd = "thd" in lib.lower()
        lib_is_smd = "smd" in lib.lower()
        for f in pretty.glob("*.kicad_mod"):
            txt = f.read_text()
            ftype = footprint_type(txt)
            if ftype == "through_hole" and lib_is_smd and not lib_is_thd:
                anomalies.append(f"{lib}/{f.name}: through_hole pads in an SMD lib")
            if ftype == "smd" and lib_is_thd:
                anomalies.append(f"{lib}/{f.name}: smd pads in a THD lib")
            new, did = fix(txt)
            if did:
                changed[lib] += 1
                if not dry_run:
                    f.write_text(new)
    total = sum(changed.values())
    print(f"footprints {'to update' if dry_run else 'updated'}: {total}")
    for lib, n in sorted(changed.items()):
        print(f"  {n:5}  {lib}")
    if anomalies:
        print(f"\nanomalies (type disagrees with lib): {len(anomalies)}")
        for a in anomalies[:20]:
            print(f"  {a}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run(args.dry_run)


if __name__ == "__main__":
    main()
