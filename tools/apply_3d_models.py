#!/usr/bin/env python3
"""Rewrite terra footprint `(model ...)` refs to KiCad bundled models.

For each terra-owned footprint used by a `cern_<table>` part, resolve a KiCad
bundled 3D model via tools/model_map (exact SMD, geometry-aware THT axial,
TO-220) and rewrite the footprint's `(model "...")` path. Offset/scale/rotate are
left untouched — a human positions afterwards. Footprints with no suitable
bundled model are reported for the download tail.

THT axial models are pitch-parameterized, so the resolver needs the footprint's
actual lead pitch; this tool measures it from the pad centers and passes it in.

This EDITS the committed terra `.kicad_mod` files in place (terra owns them); it
is a maintenance tool, not part of every build. Re-runnable/idempotent.

Usage: uv run python tools/apply_3d_models.py [--table cern_diodes] [--dry-run]
"""
from __future__ import annotations

import argparse
import math
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.model_map import resolve_model  # noqa: E402

_MODEL_PATH = re.compile(r'(\(model\s+")[^"]*(")')
_PAD_AT = re.compile(r"\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)")


def fp_orientation(name: str) -> str | None:
    """Mounting orientation encoded in a footprint name: 'v', 'h', or None.

    CERN footprints tag TO/axial mounting with -v / -h / -HFLIP tokens, e.g.
    'TO-247-2-h', 'TO-220-2-v', 'TO-220-2-HFLIP'.
    """
    toks = re.split(r"[-_]", name.lower())
    if any(t == "v" or t.startswith("vert") for t in toks):
        return "v"
    if any(t.startswith("h") for t in toks):  # h, horiz, hflip
        return "h"
    return None


def fp_leads(name: str) -> int | None:
    """Lead count encoded in a footprint name (e.g. 'TO-220-2-H' -> 2)."""
    for t in re.split(r"[-_]", name):
        if t.isdigit() and int(t) in (2, 3, 4, 5):
            return int(t)
    return None


def measure_pitch(txt: str) -> float | None:
    """Largest pad-center separation in a footprint (its lead pitch for axials).

    Returns None if fewer than two pads are found.
    """
    centers = []
    for chunk in txt.split("(pad ")[1:]:
        m = _PAD_AT.search(chunk)
        if m:
            centers.append((float(m.group(1)), float(m.group(2))))
    if len(centers) < 2:
        return None
    return max(math.dist(a, b) for i, a in enumerate(centers) for b in centers[i + 1:])


def run(table: str, dry_run: bool) -> int:
    con = sqlite3.connect(ROOT / "db" / "terra.db")
    # footprint -> Counter of (package, pin_count) by part count
    fp_variants: dict[str, Counter] = {}
    fp_parts: Counter = Counter()
    for fpref, pkg, pin in con.execute(
        f"SELECT kicad_footprint, package, pin_count FROM {table} "
        "WHERE kicad_footprint LIKE '%:%'"
    ):
        try:
            pin_i = int(pin) if pin not in (None, "") else None
        except (TypeError, ValueError):
            pin_i = None
        fp_variants.setdefault(fpref, Counter())[((pkg or "").strip(), pin_i)] += 1
        fp_parts[fpref] += 1

    rewritten = no_model_line = missing_file = 0
    parts_covered = 0
    unmapped: Counter = Counter()
    for fpref, variants in sorted(fp_variants.items()):
        nick, name = fpref.split(":", 1)
        f = ROOT / "kicad_footprints" / f"{nick}.pretty" / f"{name}.kicad_mod"
        if not f.is_file():
            missing_file += 1
            continue
        txt = f.read_text()
        pitch = measure_pitch(txt)
        ori = fp_orientation(name)
        leads = fp_leads(name)
        # A footprint is one physical body. When its parts carry conflicting
        # package labels that resolve to different models, the label backing the
        # most parts wins (ties broken by name for determinism).
        ref_weight: Counter = Counter()
        for (pkg, pin), count in variants.items():
            ref = resolve_model(pkg, pad_pitch_mm=pitch, pin_count=pin,
                                orientation=ori, leads=leads)
            if ref:
                ref_weight[ref] += count
        if not ref_weight:                        # nothing maps
            single = len(variants) == 1
            for (pkg, _), count in variants.items():
                unmapped[pkg or "(blank)"] += fp_parts[fpref] if single else count
            continue
        ref = max(sorted(ref_weight), key=ref_weight.get)
        new, n = _MODEL_PATH.subn(lambda m: m.group(1) + ref + m.group(2), txt, count=1)
        if n == 0:
            no_model_line += 1
            continue
        if new != txt and not dry_run:
            f.write_text(new)
        rewritten += 1
        parts_covered += fp_parts[fpref]

    total_parts = sum(fp_parts.values())
    print(f"footprints rewritten: {rewritten}  "
          f"no-model-line: {no_model_line}  missing-file: {missing_file}")
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
