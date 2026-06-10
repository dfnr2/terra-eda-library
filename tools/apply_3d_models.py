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
from tools.model_map import (  # noqa: E402
    native_centroid, resolve_connector, resolve_from_footprint, resolve_model)

_MODEL_PATH = re.compile(r'(\(model\s+")[^"]*(")')
_PAD_AT = re.compile(r"\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)")
# The offset xyz inside the (model …) block: model path, then (offset (xyz X Y Z)).
_MODEL_OFFSET = re.compile(
    r'(\(model\s+"[^"]*"\s*\(offset\s*\(xyz\s+)(-?[0-9.]+)\s+(-?[0-9.]+)\s+(-?[0-9.]+)',
    re.S)


def pad_centroid(txt: str) -> tuple[float, float] | None:
    """Mean of pad centers in a footprint (mm), or None if fewer than one pad."""
    cs = [(float(m.group(1)), float(m.group(2)))
          for chunk in txt.split("(pad ")[1:]
          for m in [_PAD_AT.search(chunk)] if m]
    if not cs:
        return None
    return (sum(x for x, _ in cs) / len(cs), sum(y for _, y in cs) / len(cs))


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


def grid_geometry(txt: str):
    """(pins, rows, perrow, pitch) when pads form a clean rectangular grid at a
    uniform pitch (a real pin header/socket); None for irregular layouts. This is
    the self-gate that keeps proprietary connectors out of the generic resolver."""
    cs = [(round(float(m.group(1)), 2), round(float(m.group(2)), 2))
          for chunk in txt.split("(pad ")[1:]
          for m in [_PAD_AT.search(chunk)] if m]
    if len(cs) < 2:
        return None
    xs = sorted({x for x, _ in cs})
    ys = sorted({y for _, y in cs})
    if len(xs) * len(ys) != len(cs):     # not a full rectangular grid
        return None

    def uniform(vals):
        if len(vals) < 2:
            return None
        ds = {round(vals[i + 1] - vals[i], 2) for i in range(len(vals) - 1)}
        return next(iter(ds)) if len(ds) == 1 else None

    if len(xs) >= len(ys):
        perrow, rows, p, minor = len(xs), len(ys), uniform(xs), ys
    else:
        perrow, rows, p, minor = len(ys), len(xs), uniform(ys), xs
    if not p:
        return None
    # Multi-row: require row spacing == pitch (a true uniform pin grid). This
    # declines DIP-spaced parts (rows 7.62mm apart, pitch 2.54) so they don't get
    # a wrong 2.54mm-row PinHeader/PinSocket model.
    if rows > 1:
        rp = uniform(minor)
        if rp is None or abs(rp - p) > 0.05:
            return None
    return (len(cs), rows, perrow, p)


def run(table: str, dry_run: bool) -> int:
    con = sqlite3.connect(ROOT / "db" / "terra.db")
    # footprint -> Counter of (package, pin_count) by part count
    fp_variants: dict[str, Counter] = {}
    fp_parts: Counter = Counter()
    fp_desc: dict[str, Counter] = {}      # footprint -> description frequencies
    for fpref, pkg, pin, desc in con.execute(
        f"SELECT kicad_footprint, package, pin_count, description FROM {table} "
        "WHERE kicad_footprint LIKE '%:%'"
    ):
        try:
            pin_i = int(pin) if pin not in (None, "") else None
        except (TypeError, ValueError):
            pin_i = None
        fp_variants.setdefault(fpref, Counter())[((pkg or "").strip(), pin_i)] += 1
        fp_desc.setdefault(fpref, Counter())[(desc or "").strip()] += 1
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
        #
        # Footprints owned by a name-only resolver (fuses, relays, sockets) skip
        # the generic package path: their CERN `Case` collides with diode/IC
        # package keys (a fuse `Case`='0603' would resolve to the diode D_0603
        # chip), so they must resolve purely from the footprint name below.
        ref_weight: Counter = Counter()
        if not name.upper().startswith(("FUSC", "FUSE", "FUSR", "FUSH", "SAR",
                                        "REL_", "RELS_", "THERM", "VAR")):
            for (pkg, pin), count in variants.items():
                ref = resolve_model(pkg, pad_pitch_mm=pitch, pin_count=pin,
                                    orientation=ori, leads=leads)
                if ref:
                    ref_weight[ref] += count
        if not ref_weight:
            # package column gave nothing; the footprint name often encodes the
            # body (bridges, blank-package SMD/axial parts).
            fref = resolve_from_footprint(name, pad_pitch_mm=pitch,
                                          orientation=ori, leads=leads)
            if fref:
                ref_weight[fref] = fp_parts[fpref]
        if not ref_weight:
            # connectors: description series + footprint grid geometry.
            desc = fp_desc[fpref].most_common(1)[0][0]
            g = grid_geometry(txt)
            cref = resolve_connector(
                desc, pins=(g[0] if g else None), rows=(g[1] if g else None),
                perrow=(g[2] if g else None), pitch_mm=(g[3] if g else None),
                orientation=ori)
            if cref:
                ref_weight[cref] = fp_parts[fpref]
        if not ref_weight:                        # still nothing maps
            single = len(variants) == 1
            for (pkg, _), count in variants.items():
                unmapped[pkg or "(blank)"] += fp_parts[fpref] if single else count
            continue
        ref = max(sorted(ref_weight), key=ref_weight.get)
        new, n = _MODEL_PATH.subn(lambda m: m.group(1) + ref + m.group(2), txt, count=1)
        if n == 0:
            no_model_line += 1
            continue
        # Align the model: KiCad models are authored origin-at-(native pad
        # centroid). CERN footprints use a different origin, so offset the model
        # by (CERN centroid - native centroid). Only when the current offset is
        # ~0, so manual positioning is never clobbered.
        nat = native_centroid(ref)
        cc = pad_centroid(txt)
        if nat and cc:
            dx, dy = cc[0] - nat[0], cc[1] - nat[1]

            def _set_offset(m, dx=dx, dy=dy):
                cur = (float(m.group(2)), float(m.group(3)))
                if abs(cur[0]) > 0.01 or abs(cur[1]) > 0.01:
                    return m.group(0)              # human-positioned; leave it
                return f"{m.group(1)}{dx:.4g} {-dy:.4g} {m.group(4)}"
            if abs(dx) > 0.05 or abs(dy) > 0.05:
                new = _MODEL_OFFSET.sub(_set_offset, new, count=1)
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
