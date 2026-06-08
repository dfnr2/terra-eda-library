"""Codified CERN package -> KiCad bundled 3D model resolution.

This is the single source of truth for "which KiCad model does a CERN package
get". It exists so the mapping never has to be re-derived by hand: every
decision — exact SMD matches, geometry-aware THT pitch selection, and the
packages we deliberately leave to the download tail — lives here in code.

Three resolution strategies, tried in order by ``resolve_model``:

1. **Exact SMD** (``SMD_PACKAGE_MODEL``) — one package string == one model file.
   KiCad ships one canonical model per SMD diode/SOT package, so a flat dict is
   exact and stable.

2. **THT axial families** (``THT_AXIAL_FAMILY``) — KiCad parameterizes axial
   diode models by *lead pitch and orientation* (e.g. ``D_DO-41_SOD81_P10.16mm_
   Horizontal.step``), so a package alone (``DO-41``) is not enough. The caller
   measures the footprint's actual pad pitch; we pick the horizontal model whose
   pitch is closest, but only if within ``AXIAL_PITCH_TOL_MM`` — a footprint
   wider than any bundled model (e.g. DO-201AD at 20.32mm vs 15.24mm max) would
   render with leads not reaching the body, so we decline it instead.

3. **THT TO-220** (``TO220_MODEL``) — direct package->file; KiCad's TO-220 models
   are not pitch-parameterized.

Anything not resolved is recorded in ``SKIP_REASON`` (why it's left to the
download tail / human), so the gaps are documented rather than mysterious.

Refs are emitted as ``${KICAD10_3DMODEL_DIR}/<lib>/<file>`` — KiCad expands the
var at load time. ``kicad_3dmodel_dir`` resolves the *real* filesystem path so we
can glob for available pitches.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

ENV = "${KICAD10_3DMODEL_DIR}"

# How far a footprint's measured lead pitch may sit from the nearest bundled
# axial model before we decline (mm). 1.5mm tolerates the standard half-step
# offsets (e.g. DO-15 at 13.97mm -> the 15.24mm model, off by 1.27) but rejects
# gross mismatches where no shipped model spans the leads.
AXIAL_PITCH_TOL_MM = 1.5

_DIODE_SMD = "Diode_SMD.3dshapes"
_DIODE_THT = "Diode_THT.3dshapes"
_TO_SOT_SMD = "Package_TO_SOT_SMD.3dshapes"
_TO_SOT_THT = "Package_TO_SOT_THT.3dshapes"
_SO = "Package_SO.3dshapes"

# --- 1. Exact SMD: CERN package -> (kicad 3dshapes lib, model filename) -------
SMD_PACKAGE_MODEL = {
    # DO-214 family == SMA/SMB/SMC
    "DO-214AC": (_DIODE_SMD, "D_SMA.step"), "SMA": (_DIODE_SMD, "D_SMA.step"),
    "DO-214AA": (_DIODE_SMD, "D_SMB.step"), "SMB": (_DIODE_SMD, "D_SMB.step"),
    "DO-214AB": (_DIODE_SMD, "D_SMC.step"), "SMC": (_DIODE_SMD, "D_SMC.step"),
    # SOD family
    "SOD-123": (_DIODE_SMD, "D_SOD-123.step"), "SOD123": (_DIODE_SMD, "D_SOD-123.step"),
    "SOD-123FL": (_DIODE_SMD, "D_SOD-123F.step"), "SOD-123F": (_DIODE_SMD, "D_SOD-123F.step"),
    "SOD123F": (_DIODE_SMD, "D_SOD-123F.step"),
    "SOD-323": (_DIODE_SMD, "D_SOD-323.step"), "SOD323": (_DIODE_SMD, "D_SOD-323.step"),
    "SOD-323F": (_DIODE_SMD, "D_SOD-323F.step"),
    "SOD-523": (_DIODE_SMD, "D_SOD-523.step"), "SOD523": (_DIODE_SMD, "D_SOD-523.step"),
    "SOD-128": (_DIODE_SMD, "D_SOD-128.step"),
    "SOD-110": (_DIODE_SMD, "D_SOD-110.step"), "SOD110": (_DIODE_SMD, "D_SOD-110.step"),
    "SOD-923": (_DIODE_SMD, "D_SOD-923.step"),
    "SOD-882": (_DIODE_SMD, "D_SOD-882.step"), "SOD882": (_DIODE_SMD, "D_SOD-882.step"),
    # MELF family (SOD-80 / DO-213)
    "SOD-80": (_DIODE_SMD, "D_MiniMELF.step"), "SOD-80C": (_DIODE_SMD, "D_MiniMELF.step"),
    "SOD80": (_DIODE_SMD, "D_MiniMELF.step"), "DO-213AB": (_DIODE_SMD, "D_MiniMELF.step"),
    # chip
    "0402": (_DIODE_SMD, "D_0402_1005Metric.step"),
    "0603": (_DIODE_SMD, "D_0603_1608Metric.step"),
    # SOT / power SMD
    "SOT23-3": (_TO_SOT_SMD, "SOT-23.step"), "SOT23-5": (_TO_SOT_SMD, "SOT-23-5.step"),
    "SOT23-6": (_TO_SOT_SMD, "SOT-23-6.step"),
    "SOT323": (_TO_SOT_SMD, "SOT-323_SC-70.step"),
    "SOT363": (_TO_SOT_SMD, "SOT-363_SC-70-6.step"),
    "SOT143": (_TO_SOT_SMD, "SOT-143.step"), "SOT143B": (_TO_SOT_SMD, "SOT-143.step"),
    "SOT89": (_TO_SOT_SMD, "SOT-89-3.step"),
    "DPAK": (_TO_SOT_SMD, "TO-252-2.step"), "D-PAK": (_TO_SOT_SMD, "TO-252-2.step"),
    "D2PAK": (_TO_SOT_SMD, "TO-263-2.step"),
    # SOIC (multi-diode arrays); CERN SOIC8 == SOIC-8 3.9x4.9 P1.27
    "SOIC8": (_SO, "SOIC-8_3.9x4.9mm_P1.27mm.step"),
}

# --- 2. THT axial families: CERN package -> (lib, model filename prefix) -------
# Resolver globs the lib for "<prefix>*_P<pitch>mm_Horizontal.step", parses the
# pitch token, and picks the nearest to the footprint's measured pad pitch
# (within AXIAL_PITCH_TOL_MM). Horizontal is the common board-mount orientation;
# the human re-orients/positions afterwards.
THT_AXIAL_FAMILY = {
    "DO-41": (_DIODE_THT, "D_DO-41_SOD81"),
    "DO-35": (_DIODE_THT, "D_DO-35_SOD27"),
    "DO-34": (_DIODE_THT, "D_DO-34_SOD68"),
    "DO-15": (_DIODE_THT, "D_DO-15"),
    "DO-201": (_DIODE_THT, "D_DO-201"),
    "DO-201AD": (_DIODE_THT, "D_DO-201AD"),
    "DO-201AE": (_DIODE_THT, "D_DO-201AE"),
}

# --- 3. THT TO families: CERN package -> KiCad TO family base name ------------
# KiCad TO models are named "<family>-<leads>_<orientation>.step" (e.g.
# TO-220-3_Vertical, TO-247-2_Vertical, TO-220-2_Horizontal_TabUp). Neither the
# orientation nor the lead count lives reliably in the CERN *package* string —
# CERN puts mounting (-v/-h/FLIP) and often the lead count in the *footprint*
# name. So the resolver takes orientation + leads from the caller (derived from
# the footprint) and builds the filename, verifying it exists before using it.
TO_FAMILY = {
    "TO-220-V": "TO-220", "TO-220-H": "TO-220", "TO-220-2": "TO-220",
    "TO-220AC": "TO-220", "TO-247": "TO-247",
}
_TO_LEADS = (2, 3, 4, 5)  # lead counts KiCad ships models for

# --- Deliberate non-mappings: package -> reason (documented, not silent) -------
# These have no bundled KiCad model that fits; they go to the download tail /
# human review. Recorded here so future runs don't re-investigate them.
SKIP_REASON = {
    "": "blank package — no package string to map; needs per-MPN lookup",
    "SOD57": "no SOD57 model in KiCad; glass axial, sizes vary by lead-spacing",
    "DFN2": "2-lead DFN; KiCad ships only multi-pin dimensioned DFN models",
    "SON10": "vendor-specific SON; no generic KiCad model",
    "SOT-227B": "power module; no bundled model",
    "TO-46": "CERN TO-46 parts are fiber-coupled InGaAs detectors, not plain "
             "TO-46 cans — bundled TO-46 model geometry would not match",
    "TO-277A (SMPC)": "SMPC power package; no exact bundled model",
    "DO-219AB": "MicroSMF; no bundled model",
}

_PITCH_RE = re.compile(r"_P([0-9.]+)mm_Horizontal\.step$")

# resolved KiCad 3dmodels root, cached after first lookup
_dir_cache: list[Path | None] = []


def kicad_3dmodel_dir() -> Path | None:
    """Resolve the real filesystem path of KiCad's bundled 3dmodels root.

    Honors ``KICAD10_3DMODEL_DIR`` / ``KICAD9_3DMODEL_DIR`` env vars, then the
    standard install locations. Returns None if none exist (e.g. CI without
    KiCad) — callers then can't pitch-match and fall back to declining.
    """
    if _dir_cache:
        return _dir_cache[0]
    candidates = [
        os.environ.get("KICAD10_3DMODEL_DIR"),
        os.environ.get("KICAD9_3DMODEL_DIR"),
        "/usr/share/kicad/3dmodels",
        os.path.expanduser("~/.local/share/kicad/10.0/3dmodels"),
        os.path.expanduser("~/.local/share/kicad/9.0/3dmodels"),
        "/usr/local/share/kicad/3dmodels",
        "/opt/kicad/share/kicad/3dmodels",
    ]
    found = next((Path(c) for c in candidates if c and Path(c).is_dir()), None)
    _dir_cache.append(found)
    return found


def _ref(lib: str, fname: str) -> str:
    return f"{ENV}/{lib}/{fname}"


def _nearest_axial(lib: str, prefix: str, pitch_mm: float) -> str | None:
    """Pick the horizontal model in ``lib`` whose pitch is nearest ``pitch_mm``.

    Returns None if no model is within AXIAL_PITCH_TOL_MM (or the KiCad dir is
    unavailable) — i.e. no shipped geometry actually fits the footprint.
    """
    root = kicad_3dmodel_dir()
    if root is None:
        return None
    libdir = root / lib
    best: tuple[float, str] | None = None
    for f in libdir.glob(f"{prefix}*_P*mm_Horizontal.step"):
        m = _PITCH_RE.search(f.name)
        if not m:
            continue
        delta = abs(float(m.group(1)) - pitch_mm)
        if best is None or delta < best[0]:
            best = (delta, f.name)
    if best is None or best[0] > AXIAL_PITCH_TOL_MM:
        return None
    return _ref(lib, best[1])


def _resolve_to(family: str, orientation: str | None,
                leads: int | None) -> str | None:
    """Build a TO-family model ref from orientation + lead count.

    ``orientation`` is "v"/"h" (from the footprint name); default vertical, the
    common board orientation. Falls back to a 2-lead model (diodes are 2-lead)
    when the requested lead count has no shipped model.
    """
    root = kicad_3dmodel_dir()
    if root is None:
        return None
    libdir = root / _TO_SOT_THT
    suffix = "Horizontal_TabUp" if orientation == "h" else "Vertical"
    want = leads if leads in _TO_LEADS else 2
    for n in (want, 2):  # prefer the requested lead count, else 2-lead
        fname = f"{family}-{n}_{suffix}.step"
        if (libdir / fname).is_file():
            return _ref(_TO_SOT_THT, fname)
    return None


def resolve_model(package: str, *, pad_pitch_mm: float | None = None,
                  pin_count: int | None = None,
                  orientation: str | None = None,
                  leads: int | None = None) -> str | None:
    """Return a ``${KICAD10_3DMODEL_DIR}/...`` model ref for a CERN package.

    Footprint-derived context the resolver may need:
    - ``pad_pitch_mm`` — measured lead pitch; required for THT axial families.
    - ``orientation`` — "v"/"h" from the footprint name; for TO families.
    - ``leads`` — lead count from the footprint name (falls back to
      ``pin_count``); for TO families.

    Returns None when nothing suitable is bundled (see ``SKIP_REASON``).
    """
    p = (package or "").strip()
    if p in SMD_PACKAGE_MODEL:
        return _ref(*SMD_PACKAGE_MODEL[p])
    fam = THT_AXIAL_FAMILY.get(p)
    if fam and pad_pitch_mm is not None:
        return _nearest_axial(fam[0], fam[1], pad_pitch_mm)
    to = TO_FAMILY.get(p)
    if to:
        return _resolve_to(to, orientation, leads if leads is not None else pin_count)
    return None


def model_ref(package: str) -> str | None:
    """Back-compat: resolve packages that don't need footprint geometry."""
    return resolve_model(package)
