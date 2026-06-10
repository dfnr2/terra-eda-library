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
    "DIP4-300": (_DIP, "DIP-4_W7.62mm.step"),
    "DIP6-300": (_DIP, "DIP-6_W7.62mm.step"),
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

# --- 6. Crystals & oscillators: standard SMD bodies + vendor series -----------
# CERN's Crystals & Oscillators footprints leave `package` blank and encode the
# body in the footprint name, three ways:
#   a. vendor series KiCad ships a model for (XTAL_EPSON_TSX-3225, XTAL_TXC_7M);
#   b. a standard body-size code embedded in the name (CX3225SB, SG7050VEN);
#   c. a dimensioned IPC-ish name (XTAL1160X490X430, OSCSC254P500X700X190-6N).
# Body-size tables are keyed by (long, short) mm; the generic 7050/5032/2520
# oscillator bodies use KiCad's Abracon ASV / EuroQuartz XO53 / Epson SG210
# models (same industry-standard 4-pad ceramic bodies).
_CRYSTAL = "Crystal.3dshapes"
_OSC = "Oscillator.3dshapes"

XTAL_BODY_MODEL = {
    (11.05, 4.65): "Crystal_SMD_HC49-SD.step",
    (6.0, 3.5): "Crystal_SMD_0603-4Pin_6.0x3.5mm.step",  # crystal "0603" = 6.0x3.5mm
    (5.0, 3.2): "Crystal_SMD_5032-2Pin_5.0x3.2mm.step",
    (3.2, 2.5): "Crystal_SMD_3225-4Pin_3.2x2.5mm.step",
    (3.2, 1.5): "Crystal_SMD_3215-2Pin_3.2x1.5mm.step",
    (2.5, 2.0): "Crystal_SMD_2520-4Pin_2.5x2.0mm.step",
    (2.0, 1.6): "Crystal_SMD_2016-4Pin_2.0x1.6mm.step",
    (1.2, 1.0): "Crystal_SMD_1210-4Pin_1.2x1.0mm.step",
}
OSC_BODY_MODEL = {
    (7.0, 5.0): "Oscillator_SMD_Abracon_ASV-4Pin_7.0x5.1mm.step",        # 7050
    (5.0, 3.2): "Oscillator_SMD_EuroQuartz_XO53-4Pin_5.0x3.2mm.step",    # 5032
    (2.5, 2.0): "Oscillator_SMD_SeikoEpson_SG210-4Pin_2.5x2.0mm.step",   # 2520
}
_XTAL_OSC_BODY_TOL_MM = 1.0  # max |dL|+|dW| between named dims and a body entry

# Size codes that are unambiguous body dimensions when embedded in a vendor name
# (restricted set so part-number digits like CVCO55CC-1912-2114 never match).
_XTAL_OSC_SIZE_TOKEN = {
    "3225": (3.2, 2.5), "2520": (2.5, 2.0), "2016": (2.0, 1.6),
    "5032": (5.0, 3.2), "1210": (1.2, 1.0), "3215": (3.2, 1.5),
    "7050": (7.0, 5.0),
}

# Vendor footprints whose body is known (KiCad ships the series model, or the
# series is a documented standard body the generic models match).
XTAL_OSC_FOOTPRINT_MODEL = {
    # crystals — KiCad ships the exact vendor series model
    "XTAL_EPSON_TSX-3225": (_CRYSTAL, "Crystal_SMD_SeikoEpson_TSX3225-4Pin_3.2x2.5mm.step"),
    "XTAL_EPSON_FA-238": (_CRYSTAL, "Crystal_SMD_SeikoEpson_FA238-4Pin_3.2x2.5mm.step"),
    "XTAL_EPSON_FA-238V": (_CRYSTAL, "Crystal_SMD_SeikoEpson_FA238V-4Pin_3.2x2.5mm.step"),
    "XTAL_EPSON_MA-506": (_CRYSTAL, "Crystal_SMD_SeikoEpson_MA506-4Pin_12.7x5.1mm.step"),
    "XTAL_TXC_7M": (_CRYSTAL, "Crystal_SMD_TXC_7M-4Pin_3.2x2.5mm.step"),
    "XTAL_ABRACON_ABM3B": (_CRYSTAL, "Crystal_SMD_Abracon_ABM3B-4Pin_5.0x3.2mm.step"),
    "XTAL_ABRACON_ABM8G": (_CRYSTAL, "Crystal_SMD_Abracon_ABM8G-4Pin_3.2x2.5mm.step"),
    "XTAL_MURATA_CSTNE_G": (_CRYSTAL, "Resonator_SMD_Murata_CSTxExxV-3Pin_3.0x1.1mm.step"),
    # crystals — documented standard bodies
    "XTAL_EPSON_FA-20H": (_CRYSTAL, "Crystal_SMD_2016-4Pin_2.0x1.6mm.step"),   # 2.0x1.6mm
    "XTAL_EPSON_FC-135": (_CRYSTAL, "Crystal_SMD_3215-2Pin_3.2x1.5mm.step"),   # 3.2x1.5mm tuning fork
    "XTAL_ABRACON_ABM3": (_CRYSTAL, "Crystal_SMD_Abracon_ABM3B-4Pin_5.0x3.2mm.step"),  # same 5.0x3.2 body
    "XTAL_ABRACON_ABLS": (_CRYSTAL, "Crystal_SMD_HC49-SD.step"),    # HC-49/US SMD 11.5x4.8
    "XTAL_ABRACON_ABLS2": (_CRYSTAL, "Crystal_SMD_HC49-SD.step"),
    "XTAL_ABRACON_ABLSG": (_CRYSTAL, "Crystal_SMD_HC49-SD.step"),
    "XTAL_TXC_7A": (_CRYSTAL, "Crystal_SMD_HC49-SD.step"),          # HC-49S SMD 11.4x4.8
    "XTAL_CITIZEN_HCM49": (_CRYSTAL, "Crystal_SMD_HC49-SD.step"),   # SMD HC-49
    "XTAL_HC-49_U": (_CRYSTAL, "Crystal_HC49-U_Vertical.step"),
    "XTAL_HC-49_U-S": (_CRYSTAL, "Crystal_HC49-4H_Vertical.step"),  # HC-49/US low profile
    # oscillators — vendor series on the standard 7050 / 5032 / 2520 bodies
    "OSC_EPSON_SG-210STF": (_OSC, "Oscillator_SMD_SeikoEpson_SG210-4Pin_2.5x2.0mm.step"),
    "OSC_EPSON_SG-8002CA": (_OSC, OSC_BODY_MODEL[(7.0, 5.0)]),   # SG-8002CA = 7.0x5.0
    "OSC_EPSON_EG-2121CA": (_OSC, OSC_BODY_MODEL[(7.0, 5.0)]),   # 7.0x5.0
    "OSC_EPSON_EG-2102CA": (_OSC, OSC_BODY_MODEL[(7.0, 5.0)]),   # 7.0x5.0
    "OSC_IQD_CFPS-73": (_OSC, OSC_BODY_MODEL[(7.0, 5.0)]),       # CFPS-73 = 7.0x5.0
    "OSC_IQD_CFPS-73_180": (_OSC, OSC_BODY_MODEL[(7.0, 5.0)]),
    "OSC_IQD_CFPS-72": (_OSC, OSC_BODY_MODEL[(5.0, 3.2)]),       # CFPS-72 = 5.0x3.2
    "OSC_FOX_FXO-HC73": (_OSC, OSC_BODY_MODEL[(7.0, 5.0)]),      # HC73 = 7.0x5.0
    "OSC_FOX_FXO-HC52": (_OSC, OSC_BODY_MODEL[(5.0, 3.2)]),      # HC52 = 5.0x3.2
    "OSC_ABRACON_ASFL1": (_OSC, OSC_BODY_MODEL[(5.0, 3.2)]),     # ASFL1 = 5.0x3.2
    "OSC_ABRACON_ASFLMPC": (_OSC, OSC_BODY_MODEL[(5.0, 3.2)]),   # ASFLMPC = 5.0x3.2
}

# Dimensioned crystal/oscillator footprint name, body dims in 0.01mm:
# "XTAL1160X490X430" (11.6x4.9), "OSCSC254P500X700X190-6N" (5.0x7.0, SC=side
# concave + 2.54mm pitch token), "OSCCC320X500X160-4N" (corner concave).
_XTAL_OSC_DIM_RE = re.compile(
    r"^(XTAL|OSC)[A-Z]{0,2}(?:\d+P)?(\d{3,4})X(\d{3,4})X\d+", re.I)
_OSC_DIP_RE = re.compile(r"^OSCDIP(\d+)", re.I)


def _resolve_xtal_osc(name: str) -> str | None:
    """Resolve a crystal/oscillator model from a CERN XTAL_*/OSC_* footprint name."""
    hit = XTAL_OSC_FOOTPRINT_MODEL.get(name)
    if hit:
        return _ref(*hit)
    uc = name.upper()
    if not uc.startswith(("XTAL", "OSC")):
        return None
    m = _OSC_DIP_RE.match(uc)                 # DIP-cased oscillator (metal can)
    if m and m.group(1) in ("8", "14"):
        return _ref(_OSC, f"Oscillator_DIP-{m.group(1)}.step")
    dims = None
    m = _XTAL_OSC_DIM_RE.match(uc)
    if m:
        a, b = int(m.group(2)) / 100, int(m.group(3)) / 100
        dims = (max(a, b), min(a, b))
    else:
        for tok, d in _XTAL_OSC_SIZE_TOKEN.items():
            if tok in uc:
                dims = d
                break
    if dims is None:
        return None
    table = XTAL_BODY_MODEL if uc.startswith("XTAL") else OSC_BODY_MODEL
    best = min(table, key=lambda k: abs(k[0] - dims[0]) + abs(k[1] - dims[1]))
    if abs(best[0] - dims[0]) + abs(best[1] - dims[1]) > _XTAL_OSC_BODY_TOL_MM:
        return None
    return _ref(_CRYSTAL if uc.startswith("XTAL") else _OSC, table[best])


# --- 7. Relays: CERN footprint name -> bundled Relay_THT/Relay_SMD model ------
# CERN relay footprints are vendor-series named (REL_<MFR>_<SERIES>) and the
# package column is blank, so resolution is an exact footprint-name map onto the
# relay series KiCad ships. Same-case variants reuse the series model:
#   - Finder 40.61/40.62 share the 40-series case with 40.51/40.52;
#   - Omron latching variants (G6AU/G6KU/G6SU) share the non-latching case;
#   - Schrack RT relays (RT1/RT2/RT3/RT4/RTD MPN families) all share the RT case
#     with RM5mm pinning - 1-pole families take the RT1 model, 2-pole the RT2.
# Several CERN footprints are drawn 90 degrees rotated relative to the KiCad
# native footprint; the model body still matches (human sets rotate-Z on review).
_RELAY_THT = "Relay_THT.3dshapes"
_RELAY_SMD = "Relay_SMD.3dshapes"

RELAY_FOOTPRINT_MODEL = {
    # Finder PCB relays
    "REL_FINDER_30.22": (_RELAY_THT, "Relay_DPDT_Finder_30.22.step"),
    "REL_FINDER_32.21": (_RELAY_THT, "Relay_SPDT_Finder_32.21-x000.step"),
    "REL_FINDER_32.21.X.XXX.X300": (_RELAY_THT, "Relay_SPST_Finder_32.21-x300.step"),
    "REL_FINDER_36.11": (_RELAY_THT, "Relay_SPDT_Finder_36.11.step"),
    "REL_FINDER_40.51": (_RELAY_THT, "Relay_SPDT_Finder_40.51.step"),
    "REL_FINDER_40.52": (_RELAY_THT, "Relay_DPDT_Finder_40.52.step"),
    "REL_FINDER_40.61": (_RELAY_THT, "Relay_SPDT_Finder_40.51.step"),    # same 40-series case
    "REL_FINDER_40.61.8": (_RELAY_THT, "Relay_SPDT_Finder_40.51.step"),  # same 40-series case
    "REL_FINDER_40.62": (_RELAY_THT, "Relay_DPDT_Finder_40.52.step"),    # same 40-series case
    # Omron signal relays (THT)
    "REL_OMRON_G5V-1": (_RELAY_THT, "Relay_SPDT_Omron_G5V-1.step"),
    "REL_OMRON_G5V-2": (_RELAY_THT, "Relay_DPDT_Omron_G5V-2.step"),
    "REL_OMRON_G6A-2": (_RELAY_THT, "Relay_DPDT_Omron_G6A.step"),
    "REL_OMRON_G6AK-2": (_RELAY_THT, "Relay_DPDT_Omron_G6AK.step"),
    "REL_OMRON_G6AU-2": (_RELAY_THT, "Relay_DPDT_Omron_G6A.step"),       # latching, same case
    "REL_OMRON_G6E-134P": (_RELAY_THT, "Relay_SPDT_Omron_G6E.step"),
    "REL_OMRON_G6H-2": (_RELAY_THT, "Relay_DPDT_Omron_G6H-2.step"),
    "REL_OMRON_G6K-2P-Y": (_RELAY_THT, "Relay_DPDT_Omron_G6K-2P-Y.step"),
    "REL_OMRON_G6S-2": (_RELAY_THT, "Relay_DPDT_Omron_G6S-2.step"),
    "REL_OMRON_G2RL-24": (_RELAY_THT, "Relay_DPDT_Omron_G2RL.step"),
    "REL_OMRON_G2RL-2A": (_RELAY_THT, "Relay_DPDT_Omron_G2RL.step"),     # DPST, same G2RL case
    # Omron signal relays (SMD)
    "REL_OMRON_G6K-2F": (_RELAY_SMD, "Relay_DPDT_Omron_G6K-2F.step"),
    "REL_OMRON_G6K-2F-Y": (_RELAY_SMD, "Relay_DPDT_Omron_G6K-2F-Y.step"),
    "REL_OMRON_G6K-2G-Y": (_RELAY_SMD, "Relay_DPDT_Omron_G6K-2G-Y.step"),
    "REL_OMRON_G6KU-2F-Y": (_RELAY_SMD, "Relay_DPDT_Omron_G6K-2F-Y.step"),  # latching, same case
    "REL_OMRON_G6S-2F": (_RELAY_SMD, "Relay_DPDT_Omron_G6S-2F.step"),
    "REL_OMRON_G6S-2G": (_RELAY_SMD, "Relay_DPDT_Omron_G6S-2G.step"),
    "REL_OMRON_G6SU-2G": (_RELAY_SMD, "Relay_DPDT_Omron_G6S-2G.step"),   # latching, same case
    # Kemet / Fujitsu(FCL) / Hongfa power relays
    "REL_KEMET_EC2_NU": (_RELAY_THT, "Relay_DPDT_Kemet_EC2_NU.step"),
    "REL_FCL_FTR-F1C": (_RELAY_THT, "Relay_DPDT_Fujitsu_FTR-F1C.step"),
    "REL_HONGFA_HF115F-2Z4": (_RELAY_THT, "Relay_DPDT_Hongfa_HF115F-2Z-x4.step"),
    # Tyco/Schrack RYII + RT series
    "REL_TYCO_SCHRACK_RYII_CO": (_RELAY_THT, "Relay_1-Form-C_Schrack-RYII_RM3.2mm.step"),
    "REL_TYCO_SCHRACK_RYII_NO": (_RELAY_THT, "Relay_1-Form-A_Schrack-RYII_RM5mm.step"),
    "REL_TYCO_SCHRACK_RT21xxxx": (_RELAY_THT, "Relay_SPDT_Schrack-RT1-FormC_RM5mm.step"),
    "REL_TYCO_SCHRACK_RT31xxxx": (_RELAY_THT, "Relay_SPDT_Schrack-RT1-FormC_RM5mm.step"),
    "REL_TYCO_SCHRACK_RT314FXX": (_RELAY_THT, "Relay_SPDT_Schrack-RT1-FormC_RM5mm.step"),
    "REL_TYCO_SCHRACK_RTD1xxxx": (_RELAY_THT, "Relay_SPDT_Schrack-RT1-FormC_RM5mm.step"),
    "REL_TYCO_SCHRACK_RT42XXXX": (_RELAY_THT, "Relay_DPDT_Schrack-RT2-FormC_RM5mm.step"),
    "REL_TYCO_SCHRACK_RT44XXXX": (_RELAY_THT, "Relay_DPDT_Schrack-RT2-FormC_RM5mm.step"),
}


def _resolve_relay(name: str) -> str | None:
    """Resolve a relay model from a CERN REL_* footprint name (exact map)."""
    hit = RELAY_FOOTPRINT_MODEL.get(name)
    return _ref(*hit) if hit else None


# --- 8. Fuses: SMD chip bodies + vendor cylinder/holder footprints ------------
# CERN's Fuses footprints leave `package` blank and encode the body in the
# footprint name, three ways:
#   a. SMD chip-fuse and chip-PTC bodies — a standard size code (0402/0603/0805/
#      1206/1210) embedded in the name (FUSC_AVX_F0603G, FUSR_LITTELFUSE_1206L012),
#      mapped to KiCad's Fuse_<size>_<metric> chip models;
#   b. dimensioned resettable IPC name (FUSRC3216X100N = 3.2x1.6mm body == 1206);
#   c. a vendor holder series KiCad ships an exact model for (Schurter 0031.7701
#      / 0031.8002 cylinder holders, Bulgin FX0457). Larger SMD bodies (1812/
#      2410/2920/3812) and bespoke holders/clips/arresters have no bundled model
#      -> SKIP_REASON / human drop-folder.
_FUSE = "Fuse.3dshapes"

# Standard SMD chip-fuse body size -> KiCad metric chip-fuse model. KiCad ships
# chip models only up to 1210; larger codes (1812/2410/2920/3812) decline.
_FUSE_CHIP_MODEL = {
    "0402": "Fuse_0402_1005Metric.step",
    "0603": "Fuse_0603_1608Metric.step",
    "0805": "Fuse_0805_2012Metric.step",
    "1206": "Fuse_1206_3216Metric.step",
    "1210": "Fuse_1210_3225Metric.step",
}
# Chip body codes appearing as discrete tokens in a fuse footprint name. A size
# code must be bounded by a non-digit (or the string end) on both sides so a
# part-number run of digits never matches (e.g. the '1206' in 'PTS181216' must
# not register — it is bounded by digits and is rejected).
_FUSE_CHIP_RE = re.compile(r"(?<!\d)(0402|0603|0805|1206|1210)(?!\d)")
# Larger SMD bodies KiCad ships no chip-fuse model for; matched so the resolver
# can decline explicitly rather than fall through to a wrong token.
_FUSE_BIG_CHIP_RE = re.compile(r"(?<!\d)(1812|2410|2920|3812|2016)(?!\d)")
# Dimensioned resettable footprint 'FUSRC<LL><WW>X<height>N': LL/WW are body
# length/width in 0.1mm, e.g. 'FUSRC3216X100N' = 3.2 x 1.6mm (== 1206),
# 'FUSRC4632X150N' = 4.6 x 3.2mm (1812 - no chip model). Classify to the nearest
# chip body by (long, short) in mm.
_FUSE_DIM_RE = re.compile(r"^FUSRC(\d\d)(\d\d)X\d+N?$", re.I)
_FUSE_CHIP_BODY = {  # (long_mm, short_mm) -> code, nearest-match within tol
    (1.0, 0.5): "0402", (1.6, 0.8): "0603", (2.0, 1.2): "0805",
    (3.2, 1.6): "1206", (3.2, 2.5): "1210",
}
_FUSE_BODY_TOL_MM = 0.7

# Vendor holder/fuse footprints KiCad ships an exact model for (5x20 / 6.3x32mm
# cylinder PCB holders). Bespoke clips, blade holders, TR5 radials and arresters
# have no exact bundled body -> SKIP_REASON.
FUSE_FOOTPRINT_MODEL = {
    "FUSH_SCHURTER_0031.7701": (_FUSE, "Fuseholder_Schurter_0031.7701.xx.step"),
    "FUSH_SCHURTER_0031.8002": (
        _FUSE, "Fuseholder_Cylinder-6.3x32mm_Schurter_0031-8002_Horizontal_Open.step"),
    "FUSH_BULGIN_FX0457": (
        _FUSE, "Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed.step"),
}


def _resolve_fuse(name: str) -> str | None:
    """Resolve a fuse/holder model from a CERN FUS*_ footprint name.

    Order: exact vendor-holder map, then dimensioned resettable body, then a
    standard SMD chip-fuse size token. Larger SMD bodies and non-chip dimensioned
    bodies have no bundled model and decline.
    """
    hit = FUSE_FOOTPRINT_MODEL.get(name)
    if hit:
        return _ref(*hit)
    uc = name.upper()
    if not uc.startswith(("FUSC", "FUSE", "FUSR", "FUSH", "FUSRC", "SAR")):
        return None
    m = _FUSE_DIM_RE.match(uc)               # dimensioned resettable body
    if m:
        a, b = int(m.group(1)) / 10, int(m.group(2)) / 10  # LL, WW in 0.1mm
        dims = (max(a, b), min(a, b))
        best = min(_FUSE_CHIP_BODY,
                   key=lambda k: abs(k[0] - dims[0]) + abs(k[1] - dims[1]))
        if abs(best[0] - dims[0]) + abs(best[1] - dims[1]) <= _FUSE_BODY_TOL_MM:
            return _ref(_FUSE, _FUSE_CHIP_MODEL[_FUSE_CHIP_BODY[best]])
        return None
    if _FUSE_BIG_CHIP_RE.search(uc):         # 1812/2410/2920/3812/2016 -> no model
        return None
    m = _FUSE_CHIP_RE.search(uc)             # standard SMD chip-fuse size code
    if m:
        return _ref(_FUSE, _FUSE_CHIP_MODEL[m.group(1)])
    return None


# --- 8b. Thermistors & Varistors: SMD chip bodies ------------------------------
# CERN's Thermistors And Varistors footprints encode SMD chip bodies as a
# dimensioned IPC-ish name (THERMC1608X90N = 1.6x0.8mm == 0603; VAR_3220X25 =
# 3.2x2.0mm; VAR_1005X55N = 1.0x0.5mm == 0402). These map to KiCad's
# Resistor_SMD chip models (a thermistor/varistor chip shares the resistor chip
# body). The `package` column also carries the size (0402/0603/0805/1206/1210),
# but it collides with the diode chip keys in SMD_PACKAGE_MODEL, so — like fuses
# — these footprints resolve purely from the footprint name (apply_3d_models
# routes THERM*/VAR_*/TCO*/TEXAS* names here, never through the package path).
# Bespoke vendor disc/leaded/metal bodies (THERM_<mfr>_*, VAR_<mfr>_*, the metal
# THERMM10080X380N, TCO/TEXAS) have no bundled chip model -> SKIP_REASON.
_RES_SMD = "Resistor_SMD.3dshapes"

# Standard SMD chip body size -> KiCad metric resistor chip model.
_TV_CHIP_MODEL = {
    "0402": "R_0402_1005Metric.step",
    "0603": "R_0603_1608Metric.step",
    "0805": "R_0805_2012Metric.step",
    "1206": "R_1206_3216Metric.step",
    "1210": "R_1210_3225Metric.step",
}
# (long_mm, short_mm) of each chip body -> size code, for nearest-body matching.
_TV_CHIP_BODY = {
    (1.0, 0.5): "0402", (1.6, 0.8): "0603", (2.0, 1.3): "0805",
    (3.2, 1.6): "1206", (3.2, 2.5): "1210",
}
_TV_BODY_TOL_MM = 0.7
# Dimensioned chip body in the footprint name: a 'C'/'M'-cased token or a
# VAR_<dims> tail, '<LL><WW>X<height>' with LL/WW the body length/width in 0.1mm.
# THERMC1608X90N -> 16,08; VAR_3220X25 -> 32,20; VAR_1005X55N -> 10,05.
_TV_DIM_RE = re.compile(r"(?:THERMC|VAR_?)(\d\d)(\d\d)X\d+", re.I)


def _resolve_thermistor_varistor(name: str) -> str | None:
    """Resolve a chip thermistor/varistor model from a CERN footprint name.

    Only the dimensioned SMD chip-body names (THERMC<LLWW>X.., VAR_<LLWW>X..)
    resolve, onto the matching KiCad Resistor_SMD chip model. Bespoke vendor
    disc/leaded/metal bodies decline (no bundled model).
    """
    uc = name.upper()
    if not uc.startswith(("THERM", "VAR")):
        return None
    m = _TV_DIM_RE.match(uc)
    if not m:
        return None
    a, b = int(m.group(1)) / 10, int(m.group(2)) / 10  # LL, WW in 0.1mm
    dims = (max(a, b), min(a, b))
    best = min(_TV_CHIP_BODY,
               key=lambda k: abs(k[0] - dims[0]) + abs(k[1] - dims[1]))
    if abs(best[0] - dims[0]) + abs(best[1] - dims[1]) > _TV_BODY_TOL_MM:
        return None  # e.g. THERMM10080X380N (10.0x8.0mm metal body) -> no model
    return _ref(_RES_SMD, _TV_CHIP_MODEL[_TV_CHIP_BODY[best]])


# --- 9. Switches: CERN footprint name -> bundled Button_Switch model ----------
# CERN's Switches footprints leave `package` blank and are vendor-series named
# (PB_<MFR>_<SERIES>, SW_<MFR>_<SERIES>), so resolution is an exact footprint-name
# map onto the switch bodies KiCad ships under Button_Switch_SMD/THT. The map
# covers the standard tactile (Omron B3F THT, B3S/B3U SMD), the Omron A6S/A6H DIP
# slide-switch arrays (keyed by switch-count series), and the C&K toggle/slide
# bodies KiCad authors (FSMSM, JS202011CQN, PCM12/PCM13). The bulk of the table is
# bespoke vendor switch bodies with no bundled KiCad model -> SKIP_REASON.
_BSW_SMD = "Button_Switch_SMD.3dshapes"
_BSW_THT = "Button_Switch_THT.3dshapes"

SWITCH_FOOTPRINT_MODEL = {
    # Omron tactile, THT (B3F series; CERN B3F-1xx0 -> KiCad B3F-1xxx family)
    "PB_OMRON_B3F-1000": (_BSW_THT, "SW_TH_Tactile_Omron_B3F-100x.step"),
    "PB_OMRON_B3F-1060": (_BSW_THT, "SW_TH_Tactile_Omron_B3F-106x.step"),
    "PB_OMRON_B3F-1070": (_BSW_THT, "SW_TH_Tactile_Omron_B3F-107x.step"),
    # Omron tactile, SMD (B3S / B3U series)
    "PB_OMRON_B3S-1000": (_BSW_SMD, "SW_SPST_B3S-1000.step"),
    "PB_OMRON_B3U-1100P": (_BSW_SMD, "SW_SPST_B3U-1100P.step"),
    "SW_OMRON_B3U-3000PM": (_BSW_SMD, "SW_SPST_B3U-3000P.step"),  # 3000PM, same 3000P body
    # Tyco / C&K toggle & slide bodies KiCad authors
    "PB_TYCO_FSMSM": (_BSW_SMD, "SW_SPST_FSMSM.step"),
    "SW_C&K_JS202011CQN": (_BSW_THT, "SW_CK_JS202011CQN_DPDT_Straight.step"),
    "SW_C&K_PCM12SMTR": (_BSW_SMD, "SW_SPDT_PCM12.step"),
    "SW_C&K_PCM13SMTR": (_BSW_SMD, "SW_SP3T_PCM13.step"),
    # Omron A6S/A6H DIP slide-switch arrays, keyed by switch count (CERN -x102/-x102-H
    # -> KiCad -x10x series body). A6S = W8.9mm P2.54mm, A6H = W6.15mm P1.27mm.
    "SW_OMRON_A6S-2102-H": (_BSW_SMD, "SW_DIP_SPSTx02_Slide_Omron_A6S-210x_W8.9mm_P2.54mm.step"),
    "SW_OMRON_A6S-4102-H": (_BSW_SMD, "SW_DIP_SPSTx04_Slide_Omron_A6S-410x_W8.9mm_P2.54mm.step"),
    "SW_OMRON_A6S-8102-H": (_BSW_SMD, "SW_DIP_SPSTx08_Slide_Omron_A6S-810x_W8.9mm_P2.54mm.step"),
    "SW_OMRON_A6H-2102": (_BSW_SMD, "SW_DIP_SPSTx02_Slide_Omron_A6H-2101_W6.15mm_P1.27mm.step"),
    "SW_OMRON_A6H-4102": (_BSW_SMD, "SW_DIP_SPSTx04_Slide_Omron_A6H-4101_W6.15mm_P1.27mm.step"),
    "SW_OMRON_A6H-6102": (_BSW_SMD, "SW_DIP_SPSTx06_Slide_Omron_A6H-6101_W6.15mm_P1.27mm.step"),
    "SW_OMRON_A6H-8102": (_BSW_SMD, "SW_DIP_SPSTx08_Slide_Omron_A6H-8101_W6.15mm_P1.27mm.step"),
}


def _resolve_switch(name: str) -> str | None:
    """Resolve a switch model from a CERN PB_*/SW_*/KNB_*/JUMP* footprint name.

    Exact map only: CERN switch footprints are bespoke vendor-series bodies, so
    only the ones KiCad ships a matching model for resolve; the rest decline.
    """
    hit = SWITCH_FOOTPRINT_MODEL.get(name)
    return _ref(*hit) if hit else None


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
    # crystals & oscillators (footprint-name families; package column is blank)
    "OSC 3225": "3.2x2.5mm oscillator body — KiCad ships no 3225 oscillator "
                "model (CFPS-32, SG-310, SG-8018CE, ASE/ASEMPC, Si510/511 3.2x5)",
    "OSC vendor body": "bespoke vendor oscillator bodies (IQD CFPT/CFPS-39/-69, "
                       "SiTime, SiLabs Si5xx 5x7, Crystek CVHD/CCHD/CCLD, "
                       "Connor-Winfield, Rakon, Abracon AST/AOCJY) — no bundled model",
    "OCXO/VCO module": "OCXO cans and RF VCO modules (Wenzel, Morion MV209, KVG, "
                       "AXTAL, Mini-Circuits ROS/CK, Crystek CVCO/CVCSO/CVSS) — "
                       "no bundled model",
    "XTAL_MICRO-CRYSTAL_*": "CERN parts are CC1F/CC6F/MS3V/RV-8803 variants; KiCad "
                            "ships only CC*V-T1A / MS1V bodies — geometry differs",
    "XTAL cylinder/THT misc": "MC-406 / ABL / ZTB / ATS / SMU5 cylinder and THT "
                              "bodies — no matching bundled model",
    # relays (footprint-name families; package column is blank)
    "REL TE Axicom IM": "KiCad ships only the J-leg IM model, authored 90° "
                        "rotated; CERN's gull-wing (IMxxxGX/IMExxxGX) and THT "
                        "(IMxxxTX/IMBxxTX) variants would render wrong",
    "REL reed (Coto/Meder/Pickering/Cynergy3/Celduc/Littelfuse)": "bespoke reed "
                        "relay bodies (Coto 23xx/9xxx, Meder BE/HI/LI/MRE/SHV/CRF/"
                        "CRR/DIL/KT, Pickering 1xx/63/200RF, Cynergy3 D-series) — "
                        "KiCad's StandexMeder SIL/DIP bodies don't match",
    "REL vendor power/industrial": "bespoke vendor bodies with no bundled model "
                        "(Finder 41/46/50/55/62/66/67, Omron G2R/G2RG/G5Q/G6B/G6C/"
                        "G6J/G6L/G6RL/G3VM, Panasonic AGN/AGQ/DK/DS/DSP/JS/NC4D/S/"
                        "SF/SFS/SP/ST/TQ/TX/TXS, Tyco-Axicom FP2/HF3/HF6/MT2/P2/"
                        "V23026/V23079, Schrack MSR/SNR/MT32/PT2/SR4/SR6, ABB/"
                        "Enerdis/Guenther/Teledyne/Zettler/NTE/etc.)",
    "RELS sockets": "relay sockets are bespoke vendor bodies; no bundled model",
    # fuses (footprint-name families; package column is blank)
    "FUSE cylinder cartridge": "5x20 / 6.3x32 / 10x38 / 6x46mm cartridge fuse "
                        "bodies (FUSE_5X20_*, FUSE_6.3X32_*, FUSE_10X38_*, vendor "
                        "MSF/MST/MGA/HVJ/TDC10/SFH/SR-5/186000) — KiCad ships the "
                        "matching cylinder *holders* but no bare-cartridge model",
    "FUSE big SMD chip": "1812/2410/2920/3812 SMD chip-fuse bodies — KiCad ships "
                        "Fuse chip models only up to 1210",
    "FUSE PTC vendor body": "bespoke resettable PTC bodies (Bourns MF-R/MF-RX "
                        "radial, MF-SM/NSMF/PSMF/USMF disc, Littelfuse NANOSMD/"
                        "MICROSMD/RXEF/RUEF/RHEF, BelFuse 0ZCJ, Bussmann PTS) — no "
                        "matching bundled chip/disc model",
    "FUSE holder/clip/cover": "fuse holders, clips and covers that are bespoke "
                        "vendor bodies (Keystone 3576/4245 5AG/6.3x32 holders, "
                        "Schurter OGN/3101/0031.25xx/35xx, Littelfuse 5xx/1xxxxx "
                        "blocks, Bussmann/Eaton/Mersen holders, TR5 radials) — no "
                        "exact bundled model",
    "Surge Arrester": "GDT / surge-arrester bodies (Bourns 20xx, Littelfuse CG/SE, "
                        "TDK/Epcos, Siemens, Dexerials) — no bundled KiCad model",
    # switches (footprint-name families; package column is blank)
    "SWITCH bespoke vendor body": "most CERN switch bodies are bespoke vendor "
                        "series with no bundled KiCad model: pushbuttons (APEM "
                        "MJTP2205/TP32/PT65, MultiMec 3ET/5GT, Mentor, Schneider "
                        "ZB6, Wurth, ALPS SKHH/SPUJ, MEC, E-Switch TL2243/TL3315, "
                        "C&K 8xxx/E1xx/KSC/KMR/KSS), toggle/slide/rocker (C&K 7101/"
                        "1101/AYZ/OS/JS-SCQN, NKK, APEM NDS/P36/P60, EAO, EOZ, "
                        "Knitter, NIDEC/Copal CS/CVS/CAS/CJS, Multicomp, RS, TT "
                        "EN16, TWSwitches), rotary/coded (C&K A20615/RB-231, CTS "
                        "20x, Lorlin CK, ERG SCS/SDD/SDES/SDLS/DS16, Tyco 15xx/18xx "
                        "GDH/ADE/ADP, EOZ, Hartmann, NIDEC, Unimec), encoders (ALPS "
                        "EC11/SRBM, Bourns), knobs (Mentor 1840, Omron B32), and "
                        "the SMD solder jumpers (JUMPSM3P/JUMPSMD0805) — KiCad ships "
                        "models only for the Omron B3F/B3S/B3U tactile, Omron A6S/"
                        "A6H DIP-slide, and C&K FSMSM/JS202011CQN/PCM12/PCM13 bodies "
                        "(mapped above). The rest go to the human drop-folder.",
    # transformers (footprint-name families; package column is blank)
    "XFMR vendor core": "CERN Transformers are bespoke vendor magnetics — BLOCK "
                        "(VB/PT/FL/AVB mains), Myrra (EI/UI mains), Talema/Nuvotem "
                        "(toroidal AC), Coilcraft/Mini-Circuits/Macom/MiniRF (RF "
                        "balun/wideband), Pulse/Wurth (pulse/CMC/Ethernet magnetics "
                        "modules), VAC (current-sense cores), Schaffner/Vigortronix/"
                        "ERA/Triad/Hammond (signal & power), CERN-custom HCRA*/EDA-* "
                        "cores. KiCad's Transformer_THT/SMD libs ship only a handful "
                        "of unrelated vendor-specific bodies (Breve TEZ, Hahn/CHK "
                        "EI, Lundahl, ETAL, Triad VPP16-310, Halo TG111-MSC13) — "
                        "none of which is the body of any CERN Transformers part "
                        "(CERN's lone Halo is TG111-E001J24RL on the J24 body, its "
                        "Triads are CST/CSE/TY/FS/SP series, not VPP16). 0/230 "
                        "covered is correct, not a regression; these go to the human "
                        "drop-folder under kicad_3dmodels/.",
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
# "QFP50P900X900X160-48N"     = QFP, 0.50mm pitch, 9.00x9.00mm lead-span, 48 leads;
# "SON95P300X300X80-7N"       = SON, 0.95mm pitch, 3.00x3.00mm body, 7 pads (the
#   dual-row small-outline no-lead body — physically identical to DFN, which is
#   where KiCad files its model, so SON resolves through the DFN family).
_QUAD_RE = re.compile(r"^[PVT]?(QFN|DFN|SON|QFP|LQFP|TQFP)(\d+)P(\d+)X(\d+)X\d+-(\d+)N", re.I)
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
    if fam == "SON":
        fam = "DFN"  # SON == DFN body; KiCad files the model under DFN.
    if fam in ("QFN", "DFN"):
        return _best_quad(root / _QFN_DFN, _QFNDFN_MODEL, {fam}, leads, pitch, bx, by, 1.5)
    # QFP family: CERN body == lead-span; KiCad body ≈ span − 2mm.
    return _best_quad(root / _QFP, _QFP_MODEL, set(_QFP_PREFER), leads, pitch,
                      bx - 2.0, by - 2.0, 2.0)


# --- Connectors: description-series + geometry -> KiCad Connector_* models ----
_PINHDR = "Connector_PinHeader_{p}mm.3dshapes"
_PINSKT = "Connector_PinSocket_{p}mm.3dshapes"
_DSUB = "Connector_Dsub.3dshapes"
_MOLEX = "Connector_Molex.3dshapes"
_STD_PITCH = (2.54, 2.00, 1.27, 1.00)
_DSUB_POS = (9, 15, 25, 37, 44, 62)
# Generic pin-header/socket fallback (#3) keys off pure grid geometry, so it must
# only fire when the part is actually a connector — otherwise a bespoke 2-pad
# sensor module on a clean 2.54mm grid (Hamamatsu SiPM, Teviso radiation sensor)
# gets a wrong PinHeader body. Every real CERN connector description carries one
# of these keywords; sensor/IC descriptions do not.
_CONNECTOR_KW = (
    "connector", "header", "socket", "receptacle", "contact", "terminal",
    "mezzanine", "board to board", "board-to-board", "wire to board",
    "pin strip", "pin row", "jumper", "shunt", "d-sub", "dsub", "idc",
)


def _nearest_std_pitch(p: float) -> float | None:
    for s in _STD_PITCH:
        if abs(p - s) <= 0.05:
            return s
    return None


def _glob_first(libdir, pattern, prefer=None):
    """First model matching pattern (prefer a name containing `prefer`)."""
    files = sorted(f.name for f in libdir.glob(pattern)) if libdir.is_dir() else []
    if not files:
        return None
    if prefer:
        pref = [f for f in files if prefer in f]
        if pref:
            return pref[0]
    return files[0]


def resolve_connector(description: str, *, pins: int | None = None,
                      rows: int | None = None, perrow: int | None = None,
                      pitch_mm: float | None = None,
                      orientation: str | None = None) -> str | None:
    """Resolve a KiCad Connector_* model from a CERN connector's description +
    footprint grid geometry. Covers D-Sub, Molex series KiCad ships (KK-254,
    PicoBlade), and generic pin headers/sockets (clean standard-pitch grids).
    Returns None for proprietary/irregular connectors (-> drop-folder).
    """
    root = kicad_3dmodel_dir()
    if root is None:
        return None
    d = (description or "")
    dl = d.lower()
    is_socket = any(k in dl for k in ("socket", "receptacle", "jack"))

    # 1. D-Sub: positions + gender.
    if "d-sub" in dl or "dsub" in dl or "d-subminiature" in dl:
        pos = next((n for n in _DSUB_POS if re.search(rf"\b{n}\b", d)), None)
        if pos:
            gender = "Socket" if is_socket or "female" in dl else "Pins"
            m = _glob_first(root / _DSUB, f"DSUB-{pos}_{gender}_*.step",
                            prefer="Housed_MountingHoles")
            if m:
                return _ref(_DSUB, m)

    # 2. Molex series KiCad actually ships (KK-254, PicoBlade), matched by pins.
    if pins:
        if re.search(r"\bKK\b", d) and "2.5" in d:
            m = _glob_first(root / _MOLEX, f"Molex_KK-254_*_1x{pins:02d}_*.step")
            if m:
                return _ref(_MOLEX, m)
        if "picoblade" in dl:
            m = _glob_first(root / _MOLEX, f"Molex_PicoBlade_*_1x{pins:02d}_*.step")
            if m:
                return _ref(_MOLEX, m)

    # 3. Generic pin header / socket from a clean rectangular grid — only when the
    # description is actually connector-like (guards against bespoke 2-pad sensor
    # modules that happen to sit on a 2.54mm grid).
    if rows and perrow and pitch_mm and any(k in dl for k in _CONNECTOR_KW):
        sp = _nearest_std_pitch(pitch_mm)
        if sp and rows in (1, 2, 3, 4):
            sp_s = f"{sp:g}"
            lib = (_PINSKT if is_socket else _PINHDR).format(p=sp_s)
            kind = "PinSocket" if is_socket else "PinHeader"
            fname = f"{kind}_{rows}x{perrow:02d}_P{sp_s}mm_Vertical.step"
            if (root / lib / fname).is_file():
                return _ref(lib, fname)
    return None


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
    relay = _resolve_relay(name)           # relay vendor-series bodies by name
    if relay:
        return relay
    if uc.startswith(("REL_", "RELS_")):
        # Relay/socket footprints resolve ONLY via the exact map above; the
        # generic package-token scan below would mis-read vendor suffixes (e.g.
        # the 'SMA' in RELS_FINDER_94.13SMA is a socket variant, not a diode).
        return None
    xo = _resolve_xtal_osc(name)           # crystal/oscillator bodies by name
    if xo:
        return xo
    if uc.startswith(("PB_", "SW_", "KNB_", "JUMP")) or "DIP_SW" in uc:
        # Switch/knob/jumper footprints resolve ONLY via the exact switch map;
        # the generic package-token scan below would mis-read embedded vendor
        # codes (e.g. a '0805' in JUMPSMD0805 as a diode 0805 chip, or 'TO'-like
        # runs in a vendor part number).
        return _resolve_switch(name)
    if uc.startswith(("FUSC", "FUSE", "FUSR", "FUSH", "SAR")):
        # Fuse/holder/arrester footprints resolve ONLY via the fuse resolver; the
        # generic package-token scan below would mis-read embedded size codes
        # (e.g. the '0603' in FUSC_AVX_F0603G as a diode 0603 model).
        return _resolve_fuse(name)
    if uc.startswith(("THERM", "VAR")):
        # Thermistor/varistor footprints resolve ONLY via the chip resolver; the
        # generic scan below would mis-read an embedded size as a diode chip or a
        # dimensioned token as a quad. Only the dimensioned chip bodies map;
        # bespoke vendor disc/leaded/metal bodies (THERM_<mfr>_*, VAR_<mfr>_*,
        # THERMM10080X380N) decline. The lone CERN TCO_*/TEXAS_* (TCO resistor
        # +fuse, polarized PTC) have no bundled body and fall through to None.
        return _resolve_thermistor_varistor(name)
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
        ku = k.upper().replace("-", "")
        if ku not in uc_nodash:
            continue
        # A pure-digit chip key (0402/0603) must be bounded by non-digits, or a
        # vendor part number's digit run would mis-match it (e.g. the '0402' in a
        # power-supply footprint 'PWS_HAMAMATSU_C11204-02' is not a 0402 chip).
        if ku.isdigit() and not re.search(rf"(?<!\d){re.escape(ku)}(?!\d)", uc_nodash):
            continue
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
