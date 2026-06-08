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

# Axial models are chosen by nearest lead pitch. Two thresholds:
#  - GOODFIT: within this the model matches the footprint cleanly (e.g. DO-15 at
#    13.97mm -> the 15.24mm model, off by 1.27).
#  - MAX_DELTA: a hard cap. Within it we still take the nearest as a best effort
#    (e.g. DO-201AD at 20.32mm -> the 15.24mm model, leads render a touch short;
#    a human repositions). Beyond it no shipped model plausibly fits -> decline.
AXIAL_GOODFIT_TOL_MM = 1.5
AXIAL_MAX_DELTA_MM = 8.0

_DIODE_SMD = "Diode_SMD.3dshapes"
_DIODE_THT = "Diode_THT.3dshapes"
_TO_SOT_SMD = "Package_TO_SOT_SMD.3dshapes"
_TO_SOT_THT = "Package_TO_SOT_THT.3dshapes"
_SO = "Package_SO.3dshapes"
_DIP = "Package_DIP.3dshapes"

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
    "SOT23-6": (_TO_SOT_SMD, "SOT-23-6.step"), "SOT23-8": (_TO_SOT_SMD, "SOT-23-8.step"),
    "SOT323": (_TO_SOT_SMD, "SOT-323_SC-70.step"),
    "SOT363": (_TO_SOT_SMD, "SOT-363_SC-70-6.step"),
    "SOT143": (_TO_SOT_SMD, "SOT-143.step"), "SOT143B": (_TO_SOT_SMD, "SOT-143.step"),
    "SOT89": (_TO_SOT_SMD, "SOT-89-3.step"),
    "DPAK": (_TO_SOT_SMD, "TO-252-2.step"), "D-PAK": (_TO_SOT_SMD, "TO-252-2.step"),
    "D2PAK": (_TO_SOT_SMD, "TO-263-2.step"),
    "SOT223": (_TO_SOT_SMD, "SOT-223.step"), "SOT-223": (_TO_SOT_SMD, "SOT-223.step"),
    "SOT353": (_TO_SOT_SMD, "SOT-353_SC-70-5.step"),
    # TO-263 (D2PAK) multi-lead; tab defaults to the centre-ish pin.
    "TO-263-3": (_TO_SOT_SMD, "TO-263-3_TabPin2.step"),
    "TO-263-5": (_TO_SOT_SMD, "TO-263-5_TabPin3.step"),
    "TO-263-7": (_TO_SOT_SMD, "TO-263-7_TabPin4.step"),
    # SO / MSOP / TSSOP / SSOP small-outline IC bodies (op-amps, logic, analog)
    "SOIC8": (_SO, "SOIC-8_3.9x4.9mm_P1.27mm.step"),
    "SOIC14": (_SO, "SOIC-14_3.9x8.7mm_P1.27mm.step"),
    "SOIC16": (_SO, "SOIC-16_3.9x9.9mm_P1.27mm.step"),
    "SOIC16W": (_SO, "SOIC-16W_7.5x10.3mm_P1.27mm.step"),
    "SOIC20": (_SO, "SOIC-20W_7.5x12.8mm_P1.27mm.step"),
    "SOIC24": (_SO, "SOIC-24W_7.5x15.4mm_P1.27mm.step"),
    "SOIC28": (_SO, "SOIC-28W_7.5x17.9mm_P1.27mm.step"),
    "MSOP8": (_SO, "MSOP-8_3x3mm_P0.65mm.step"),
    "MSOP10": (_SO, "MSOP-10_3x3mm_P0.5mm.step"),
    "TSSOP8": (_SO, "TSSOP-8_3x3mm_P0.65mm.step"),
    "TSSOP14": (_SO, "TSSOP-14_4.4x5mm_P0.65mm.step"),
    "TSSOP16": (_SO, "TSSOP-16_4.4x5mm_P0.65mm.step"),
    "TSSOP20": (_SO, "TSSOP-20_4.4x6.5mm_P0.65mm.step"),
    "TSSOP24": (_SO, "TSSOP-24_4.4x7.8mm_P0.65mm.step"),
    "TSSOP48": (_SO, "TSSOP-48_6.1x12.5mm_P0.5mm.step"),
    "SSOP16": (_SO, "SSOP-16_3.9x4.9mm_P0.635mm.step"),
    "SSOP28": (_SO, "SSOP-28_5.3x10.2mm_P0.65mm.step"),
    # DIP (THT); CERN <pkg>-300 == 300mil == W7.62mm
    "DIP8-300": (_DIP, "DIP-8_W7.62mm.step"),
    "DIP14-300": (_DIP, "DIP-14_W7.62mm.step"),
    "DIP16-300": (_DIP, "DIP-16_W7.62mm.step"),
    "DIP20-300": (_DIP, "DIP-20_W7.62mm.step"),
    # TO-92 (THT): many footprint variants; inline 3-lead is the common default.
    "TO-92": (_TO_SOT_THT, "TO-92_Inline.step"),
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
    "TO-220": "TO-220", "TO-220-V": "TO-220", "TO-220-H": "TO-220",
    "TO-220-2": "TO-220", "TO-220AC": "TO-220",
    "TO-247": "TO-247",
    "TO-126": "TO-126", "TO-264": "TO-264",
    "TO-3P": "TO-3P", "TO-3PN": "TO-3P",
}
_TO_LEADS = (2, 3, 4, 5)  # lead counts KiCad ships models for

# Metal-can families: models are named "<family>-<leads>.step" (no orientation),
# e.g. TO-18-3, TO-39-2. Lead count from pin_count, clamped to what ships (2/3).
# (TO-46 is intentionally excluded — CERN's TO-46 parts are fiber-coupled
# detectors, not plain cans; see SKIP_REASON.)
CAN_FAMILY = {"TO-5", "TO-18", "TO-39", "TO-52"}

# --- 4. Bridge rectifiers: body code (in footprint name) -> bridge model -------
# The package column is usually blank for these; the body code lives in the
# footprint name (e.g. FAIRCHILD_GBU_V, VISHAY_KBU). Only codes with an exact
# Diode_Bridge model are mapped; others (GBPC/GSIB/WOG/PB) are in SKIP_REASON.
BRIDGE_BODY = {
    "GBU": "Diode_Bridge_Vishay_GBU.step",
    "KBPM": "Diode_Bridge_Vishay_KBPM.step",
    "KBU": "Diode_Bridge_Vishay_KBU.step",
    "KBL": "Diode_Bridge_Vishay_KBL.step",
    "GBL": "Diode_Bridge_Vishay_GBL.step",
}

# --- 5. SMD body codes embedded in footprint names (package blank) ------------
# IPC/vendor footprint names encode the body but the package column is blank.
# SODFL = SOD flat-lead, DIOMELF = MELF; both size-split via the digits that
# follow the token (e.g. SODFL3516 -> 3.5mm wide). PowerDI/PowerMite are direct.
SMD_BODY_DIRECT = {
    "POWERDI123": (_DIODE_SMD, "D_PowerDI-123.step"),
    "POWERMITE": (_DIODE_SMD, "D_Powermite_LargeCathode.step"),
}

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
    "GBPC": "no exact KiCad GBPC bridge model (KBPC differs physically)",
    "GSIB": "in-line GSIB bridge; no bundled model",
    "WOG": "round WOG bridge; no exact bundled model",
    "PB": "Vishay PB bridge; no bundled model",
}

# All package keys the package-based resolver knows, for footprint-name fallback.
_PACKAGE_KEYS = set(SMD_PACKAGE_MODEL) | set(THT_AXIAL_FAMILY) | set(TO_FAMILY)

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


_fp_dir_cache: list[Path | None] = []
_native_centroid_cache: dict[str, tuple[float, float] | None] = {}
_PAD_AT_RE = re.compile(r"\(at\s+(-?[0-9.]+)\s+(-?[0-9.]+)")


def kicad_footprint_dir() -> Path | None:
    """Resolve the real path of KiCad's bundled footprint (.pretty) root."""
    if _fp_dir_cache:
        return _fp_dir_cache[0]
    candidates = [
        os.environ.get("KICAD10_FOOTPRINT_DIR"),
        os.environ.get("KICAD9_FOOTPRINT_DIR"),
        "/usr/share/kicad/footprints",
        os.path.expanduser("~/.local/share/kicad/10.0/footprints"),
        os.path.expanduser("~/.local/share/kicad/9.0/footprints"),
        "/usr/local/share/kicad/footprints",
        "/opt/kicad/share/kicad/footprints",
    ]
    found = next((Path(c) for c in candidates if c and Path(c).is_dir()), None)
    _fp_dir_cache.append(found)
    return found


def native_centroid(model_ref: str) -> tuple[float, float] | None:
    """Pad centroid of the KiCad *native* footprint that owns ``model_ref``.

    A model ``…/<Lib>.3dshapes/<stem>.step`` is authored for the same-stem
    footprint ``<Lib>.pretty/<stem>.kicad_mod`` placed at offset 0. Its pad
    centroid tells us where the model's origin sits relative to the pads, so a
    CERN footprint can offset the model to match. Returns None if not found.
    """
    if model_ref in _native_centroid_cache:
        return _native_centroid_cache[model_ref]
    root = kicad_footprint_dir()
    result = None
    try:
        rel = model_ref.split("}/", 1)[1]                 # Lib.3dshapes/stem.step
        lib3d, fname = rel.split("/", 1)
        stem = fname.rsplit(".step", 1)[0].rsplit(".stp", 1)[0]
        pretty = lib3d.replace(".3dshapes", ".pretty")
        f = (root / pretty / f"{stem}.kicad_mod") if root else None
        if f and f.is_file():
            cs = [(float(m.group(1)), float(m.group(2)))
                  for ch in f.read_text().split("(pad ")[1:]
                  for m in [_PAD_AT_RE.search(ch)] if m]
            if cs:
                result = (sum(x for x, _ in cs) / len(cs),
                          sum(y for _, y in cs) / len(cs))
    except (IndexError, ValueError, OSError):
        result = None
    _native_centroid_cache[model_ref] = result
    return result


def _nearest_axial(lib: str, prefix: str, pitch_mm: float) -> str | None:
    """Pick the horizontal model in ``lib`` whose pitch is nearest ``pitch_mm``.

    Takes the nearest model as a best effort up to AXIAL_MAX_DELTA_MM; beyond
    that no shipped geometry plausibly fits, so returns None (also None if the
    KiCad dir is unavailable).
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
    if best is None or best[0] > AXIAL_MAX_DELTA_MM:
        return None
    return _ref(lib, best[1])


_BODY_WIDTH_RE_CACHE: dict[str, re.Pattern] = {}


def _body_width(name_uc: str, token: str) -> int | None:
    """Width tens-digits following a body token: 'SODFL3516..' / token 'SODFL' -> 35."""
    pat = _BODY_WIDTH_RE_CACHE.get(token)
    if pat is None:
        pat = _BODY_WIDTH_RE_CACHE[token] = re.compile(re.escape(token) + r"(\d{2})")
    m = pat.search(name_uc)
    return int(m.group(1)) if m else None


# CERN IPC footprint name for a quad/dual flat(-no-lead) part, e.g.
# "QFN50P700X700X90-49N-S580" = QFN, 0.50mm pitch, 7.00x7.00mm body, 49 pads;
# "QFP50P900X900X160-48N"     = QFP, 0.50mm pitch, 9.00x9.00mm lead-span, 48 leads.
_QUAD_RE = re.compile(r"^[PVT]?(QFN|DFN|QFP|LQFP|TQFP)(\d+)P(\d+)X(\d+)X\d+-(\d+)N", re.I)
# KiCad parametric model names (optionally vendor-prefixed):
_QFNDFN_MODEL = re.compile(
    r"^(QFN|DFN)-(\d+)(?:-\d+EP)?_([0-9.]+)x([0-9.]+)mm_P([0-9.]+)mm", re.I)
_QFP_MODEL = re.compile(
    r"^(?:[A-Za-z0-9]+_)?(LQFP|TQFP|QFP|PQFP)-(\d+)(?:-\d+EP)?_"
    r"([0-9.]+)x([0-9.]+)mm_P([0-9.]+)mm", re.I)
_QFN_DFN = "Package_DFN_QFN.3dshapes"
_QFP = "Package_QFP.3dshapes"
_QFP_PREFER = ("LQFP", "TQFP", "QFP", "PQFP")

# CERN BGA footprint name, e.g. "BGA484C80P22X22_1900X1900X325" = 484 balls,
# 0.80mm pitch, 22x22 grid, 19.00x19.00mm body.
_BGA_RE = re.compile(r"^BGA(\d+)C(\d+)P\d+X\d+_(\d+)X(\d+)X", re.I)
# KiCad model, e.g. "BGA-256_17.0x17.0mm_Layout16x16_P1.0mm_…" (vendor prefix optional).
_BGA_MODEL_RE = re.compile(
    r"^(?:[A-Za-z0-9]+_)?BGA-(\d+)_([0-9.]+)x([0-9.]+)mm_Layout\d+x\d+_P([0-9.]+)mm", re.I)
_BGA = "Package_BGA.3dshapes"


def _resolve_bga(name: str) -> str | None:
    """Dimensioned BGA model from the IPC footprint name.

    Matches exact ball count + pitch (which disambiguates same-ball-count bodies,
    e.g. BGA-256 at 0.5/0.8/1.0mm) + nearest body. None if KiCad has no model for
    that ball count (large FPGA counts like 676/672/1517 aren't bundled).
    """
    m = _BGA_RE.match(name)
    if not m:
        return None
    root = kicad_3dmodel_dir()
    if root is None:
        return None
    balls = int(m.group(1))
    pitch = int(m.group(2)) / 100
    bx, by = int(m.group(3)) / 100, int(m.group(4)) / 100
    best = None
    for f in (root / _BGA).glob(f"*BGA-{balls}_*"):
        mm = _BGA_MODEL_RE.match(f.name)
        if not mm or int(mm.group(1)) != balls:
            continue
        if abs(float(mm.group(4)) - pitch) > 0.02:
            continue
        d = abs(float(mm.group(2)) - bx) + abs(float(mm.group(3)) - by)
        if best is None or d < best[0]:
            best = (d, f.name)
    if best is None or best[0] > 3.0:
        return None
    return _ref(_BGA, best[1])


def _best_quad(libdir, rx, fams, leads, pitch, tx, ty, tol):
    """Pick the model whose body is nearest (tx,ty) among matching family/leads/pitch."""
    best = None
    for f in libdir.glob("*.step"):
        mm = rx.match(f.name)
        if not mm or mm.group(1).upper() not in fams:
            continue
        if int(mm.group(2)) not in leads or abs(float(mm.group(5)) - pitch) > 0.02:
            continue
        d = abs(float(mm.group(3)) - tx) + abs(float(mm.group(4)) - ty)
        pri = _QFP_PREFER.index(mm.group(1).upper()) if mm.group(1).upper() in _QFP_PREFER else 0
        key = (round(d, 2), pri)
        if best is None or key < best[0]:
            best = (key, f.name)
    if best is None or best[0][0] > tol:
        return None
    return _ref(libdir.name, best[1])


def _resolve_quad(name: str) -> str | None:
    """Resolve a dimensioned QFN/DFN/QFP model from the IPC footprint name.

    Matches family + pitch + lead count (N or N-1, since CERN's pad count may
    include the thermal pad) + nearest body. QFN/DFN body in the name is the true
    body; QFP names give the lead-span, so subtract ~2mm to get the model body.
    Returns None if nothing is within tolerance or the KiCad dir is unavailable.
    """
    m = _QUAD_RE.match(name)
    if not m:
        return None
    root = kicad_3dmodel_dir()
    if root is None:
        return None
    fam = m.group(1).upper()
    pitch = int(m.group(2)) / 100
    bx, by = int(m.group(3)) / 100, int(m.group(4)) / 100
    n = int(m.group(5))
    leads = {n, n - 1}
    if fam in ("QFN", "DFN"):
        return _best_quad(root / _QFN_DFN, _QFNDFN_MODEL, {fam}, leads, pitch, bx, by, 1.5)
    # QFP family: CERN body == lead-span; KiCad body ≈ span − 2mm.
    return _best_quad(root / _QFP, _QFP_MODEL, set(_QFP_PREFER), leads, pitch,
                      bx - 2.0, by - 2.0, 2.0)


def resolve_from_footprint(name: str, *, pad_pitch_mm: float | None = None,
                           orientation: str | None = None,
                           leads: int | None = None) -> str | None:
    """Resolve a model from a footprint *name* when the package column is blank.

    CERN leaves ``package`` empty for many parts but encodes the body in the
    footprint name (``FAIRCHILD_GBU_V``, ``SODFL3516X80N``, ``DIOMELF1911N``).
    Handles bridges, SMD flat-lead/MELF bodies, then falls back to any known
    package token embedded in the name.
    """
    uc = name.upper().replace(" ", "")
    root = kicad_3dmodel_dir()
    quad = _resolve_quad(name)             # dimensioned QFN/DFN/QFP by IPC name
    if quad:
        return quad
    bga = _resolve_bga(name)               # dimensioned BGA by IPC name
    if bga:
        return bga
    for code, fname in BRIDGE_BODY.items():
        if code in uc and (root is None or (root / _DIODE_THT / fname).is_file()):
            return _ref(_DIODE_THT, fname)
    if "SODFL" in uc:  # SOD flat-lead; wide ones use the larger SOD-128 body
        w = _body_width(uc, "SODFL")
        return _ref(_DIODE_SMD, "D_SOD-128.step" if w and w >= 45 else "D_SOD-123F.step")
    if "MELF" in uc:   # DIOMELF<WWLL>: 50->MELF, 30->MiniMELF, else MicroMELF
        w = _body_width(uc, "MELF")
        f = ("D_MELF.step" if w and w >= 50
             else "D_MiniMELF.step" if w and w >= 30 else "D_MicroMELF.step")
        return _ref(_DIODE_SMD, f)
    for token, (lib, fname) in SMD_BODY_DIRECT.items():
        if token in uc:
            return _ref(lib, fname)
    # last resort: a known package key appears in the footprint name (compare
    # with hyphens stripped on both sides, so 'DO-201' matches footprint 'DO-201')
    uc_nodash = uc.replace("-", "")
    for k in sorted(_PACKAGE_KEYS, key=len, reverse=True):
        if k.upper().replace("-", "") in uc_nodash:
            r = resolve_model(k, pad_pitch_mm=pad_pitch_mm,
                              orientation=orientation, leads=leads)
            if r:
                return r
    return None


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


def _resolve_can(family: str, leads: int | None) -> str | None:
    """Metal-can model '<family>-<leads>.step'; leads clamped to what ships (2/3)."""
    root = kicad_3dmodel_dir()
    if root is None:
        return None
    libdir = root / _TO_SOT_THT
    want = leads if leads in (2, 3) else 3  # transistors are typically 3-lead
    for n in (want, 3, 2):
        fname = f"{family}-{n}.step"
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
    if p in CAN_FAMILY:
        return _resolve_can(p, leads if leads is not None else pin_count)
    return None


def model_ref(package: str) -> str | None:
    """Back-compat: resolve packages that don't need footprint geometry."""
    return resolve_model(package)
