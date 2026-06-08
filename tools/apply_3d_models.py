#!/usr/bin/env python3
"""Rewrite terra footprint `(model ...)` refs to KiCad bundled models by package.

Phase 2a: for each terra-owned footprint used by a cern_diodes part whose package
maps (tools/model_map), rewrite the footprint's `(model "...")` path to the KiCad
bundled model. Leaves offset/scale/rotate untouched (human positions). Footprints
whose package is unmapped/blank/ambiguous are reported for the download tail.

This EDITS the committed terra `.kicad_mod` files in place (terra owns them); it is a
maintenance tool, not part of every build. Re-runnable/idempotent.

Usage: uv run python tools/apply_3d_models.py [--table cern_diodes] [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.model_map import model_ref  # noqa: E402

_MODEL_PATH = re.compile(r'(\(model\s+")[^"]*(")')


def run(table: str, dry_run: bool) -> int:
    con = sqlite3.connect(ROOT / "db" / "terra.db")
    fp_pkgs: dict[str, set[str]] = {}
    fp_parts: Counter = Counter()
    for fpref, pkg in con.execute(
        f"SELECT kicad_footprint, package FROM {table} WHERE kicad_footprint LIKE '%:%'"
    ):
        fp_pkgs.setdefault(fpref, set()).add((pkg or "").strip())
        fp_parts[fpref] += 1

    rewritten = ambiguous = no_model_line = 0
    parts_covered = 0
    unmapped: Counter = Counter()
    for fpref, pkgs in sorted(fp_pkgs.items()):
        nick, name = fpref.split(":", 1)
        refs = {model_ref(p) for p in pkgs}
        if refs == {None}:                       # nothing maps
            for p in pkgs:
                unmapped[p or "(blank)"] += fp_parts[fpref] if len(pkgs) == 1 else 1
            continue
        if len([r for r in refs if r]) > 1:      # maps to >1 distinct model
            ambiguous += 1
            continue
        ref = next(r for r in refs if r)
        f = ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod"
        if not f.is_file():
            continue
        txt = f.read_text()
        new, n = _MODEL_PATH.subn(lambda m: m.group(1) + ref + m.group(2), txt, count=1)
        if n == 0:
            no_model_line += 1
            continue
        if new != txt and not dry_run:
            f.write_text(new)
        rewritten += 1
        parts_covered += fp_parts[fpref]

    total_parts = sum(fp_parts.values())
    print(f"footprints rewritten: {rewritten}  ambiguous: {ambiguous}  "
          f"no-model-line: {no_model_line}  unmapped footprints: {sum(1 for p in fp_pkgs.values() if {model_ref(x) for x in p}=={None})}")
    print(f"parts covered: {parts_covered}/{total_parts} "
          f"({100*parts_covered//max(total_parts,1)}%)")
    if unmapped:
        print("top unmapped packages (-> download tail / human):")
        for pkg, n in unmapped.most_common(12):
            print(f"  {n:4}  {pkg}")
    return rewritten


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default="cern_diodes")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run(args.table, args.dry_run)


if __name__ == "__main__":
    main()
