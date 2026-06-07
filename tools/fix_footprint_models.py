#!/usr/bin/env python3
"""Rewrite stale 3D-model paths in terra_sym.pretty footprints.

- If the model file's basename exists in assets/3dmodels/legacy.3dshapes/,
  rewrite the path to ${TERRA_EDA_LIB}/assets/3dmodels/legacy.3dshapes/<actual filename>
  (using the on-disk filename to fix case mismatches).
- If the path starts with ${KICAD6_3DMODEL_DIR} or ${KICAD9_3DMODEL_DIR}, replace
  the prefix with ${KICAD10_3DMODEL_DIR}.
- Otherwise, leave the line alone and report it.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOOTPRINT_DIR = ROOT / "assets" / "footprints" / "terra_sym.pretty"
LEGACY_DIR = ROOT / "assets" / "3dmodels" / "legacy.3dshapes"
NEW_PREFIX = "${TERRA_EDA_LIB}/assets/3dmodels/legacy.3dshapes"

MODEL_RE = re.compile(r'(\(model\s+")([^"]+)(")')


def build_legacy_index() -> dict[str, str]:
    """Return a map from lowercased basename to actual on-disk filename."""
    index: dict[str, str] = {}
    for entry in LEGACY_DIR.iterdir():
        if entry.is_file():
            index[entry.name.lower()] = entry.name
    return index


def rewrite_path(old_path: str, legacy_index: dict[str, str]) -> tuple[str, str]:
    """Return (new_path, reason)."""
    basename = os.path.basename(old_path)
    key = basename.lower()
    if key in legacy_index:
        return f"{NEW_PREFIX}/{legacy_index[key]}", "legacy"
    if old_path.startswith("${KICAD6_3DMODEL_DIR}/"):
        return old_path.replace("${KICAD6_3DMODEL_DIR}/", "${KICAD10_3DMODEL_DIR}/", 1), "kicad10"
    if old_path.startswith("${KICAD9_3DMODEL_DIR}/"):
        return old_path.replace("${KICAD9_3DMODEL_DIR}/", "${KICAD10_3DMODEL_DIR}/", 1), "kicad10"
    return old_path, "unchanged"


def process_file(path: Path, legacy_index: dict[str, str], unchanged: list[tuple[Path, str]]) -> int:
    text = path.read_text()
    changes = 0

    def repl(match: re.Match) -> str:
        nonlocal changes
        prefix, old_path, suffix = match.group(1), match.group(2), match.group(3)
        new_path, reason = rewrite_path(old_path, legacy_index)
        if reason == "unchanged":
            unchanged.append((path, old_path))
            return match.group(0)
        if new_path != old_path:
            changes += 1
        return f"{prefix}{new_path}{suffix}"

    new_text = MODEL_RE.sub(repl, text)
    if changes:
        path.write_text(new_text)
    return changes


def main() -> int:
    if not LEGACY_DIR.is_dir():
        print(f"missing: {LEGACY_DIR}", file=sys.stderr)
        return 1
    if not FOOTPRINT_DIR.is_dir():
        print(f"missing: {FOOTPRINT_DIR}", file=sys.stderr)
        return 1

    legacy_index = build_legacy_index()
    unchanged: list[tuple[Path, str]] = []
    total = 0
    touched = 0
    for fp in sorted(FOOTPRINT_DIR.glob("*.kicad_mod")):
        n = process_file(fp, legacy_index, unchanged)
        if n:
            print(f"updated {fp.name}: {n} model path(s)")
            touched += 1
            total += n

    print(f"\n{touched} file(s) modified, {total} model path(s) rewritten")
    if unchanged:
        print(f"\n{len(unchanged)} model reference(s) left unchanged (not in legacy.3dshapes, not KICAD6/9):")
        for path, old in unchanged:
            print(f"  {path.name}: {old}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
