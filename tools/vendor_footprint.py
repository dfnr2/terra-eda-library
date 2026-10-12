#!/usr/bin/env python3
"""Vendor a stock KiCad footprint into a terra footprint library with a 3D model.

KiCad ships footprints for many parts it has no 3D model for. Terra supplies the
model: copy the stock footprint unchanged except for its `(model ...)` block, which
is pointed at a terra-owned STEP with the placement that seats it on the pads.
Pads, courtyard and silk stay byte-identical to KiCad's.

Family generators call `vendor_footprint` from a maintenance mode (e.g.
`--vendor-footprints`); the written `.kicad_mod` files are committed, so a build
never depends on the installed KiCad version.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOTPRINT_ROOT = ROOT / "kicad_footprints"
MODEL_ROOT = ROOT / "assets" / "3dmodels"

_MODEL_BLOCK = re.compile(
    r'\t\(model\s+"[^"]*"\s*'
    r'\(offset\s*\(xyz[^)]*\)\s*\)\s*'
    r'\(scale\s*\(xyz[^)]*\)\s*\)\s*'
    r'\(rotate\s*\(xyz[^)]*\)\s*\)\s*'
    r'\)\n'
)


def stock_footprint_dir() -> Path:
    """Directory holding KiCad's stock `<lib>.pretty` footprint libraries."""
    return Path(os.environ.get("KICAD10_FOOTPRINT_DIR", "/usr/share/kicad/footprints"))


def _xyz(v) -> str:
    return " ".join(f"{float(c):g}" for c in v)


def model_block(model: str, offset, rotate) -> str:
    """A KiCad 10 `(model ...)` block for `assets/3dmodels/<model>`."""
    return (
        f'\t(model "${{TERRA_EDA_LIB}}/assets/3dmodels/{model}"\n'
        f"\t\t(offset\n\t\t\t(xyz {_xyz(offset)})\n\t\t)\n"
        f"\t\t(scale\n\t\t\t(xyz 1 1 1)\n\t\t)\n"
        f"\t\t(rotate\n\t\t\t(xyz {_xyz(rotate)})\n\t\t)\n"
        "\t)\n"
    )


def vendor_footprint(stock_lib: str, name: str, dest_lib: str, model: str,
                     offset, rotate) -> Path:
    """Copy `<stock_lib>:<name>` into `kicad_footprints/<dest_lib>.pretty`.

    `model` is relative to `assets/3dmodels/` (e.g.
    `terra-connectors.3dshapes/53254-0470.stp`). Returns the written path.
    """
    src = stock_footprint_dir() / f"{stock_lib}.pretty" / f"{name}.kicad_mod"
    text = src.read_text()
    blocks = _MODEL_BLOCK.findall(text)
    if len(blocks) != 1:
        raise ValueError(f"{src}: expected one (model ...) block, found {len(blocks)}")
    text = _MODEL_BLOCK.sub(lambda _m: model_block(model, offset, rotate), text)
    dest = FOOTPRINT_ROOT / f"{dest_lib}.pretty" / f"{name}.kicad_mod"
    dest.write_text(text)
    return dest
