"""Curated map: CERN package string -> KiCad bundled 3D model reference.

Phase 2a (diodes). Covers the unambiguous standard SMD packages; THT/TO and
exotic/blank packages are intentionally left unmapped (handled by the download
tail + human review). Every target is a model KiCad ships under
``${KICAD10_3DMODEL_DIR}``.
"""
from __future__ import annotations

ENV = "${KICAD10_3DMODEL_DIR}"
_SMD = "Diode_SMD.3dshapes"
_SOT = "Package_TO_SOT_SMD.3dshapes"

# CERN package -> (kicad 3dshapes lib, model filename)
PACKAGE_MODEL = {
    # DO-214 family == SMA/SMB/SMC
    "DO-214AC": (_SMD, "D_SMA.step"), "SMA": (_SMD, "D_SMA.step"),
    "DO-214AA": (_SMD, "D_SMB.step"), "SMB": (_SMD, "D_SMB.step"),
    "DO-214AB": (_SMD, "D_SMC.step"), "SMC": (_SMD, "D_SMC.step"),
    # SOD family
    "SOD-123": (_SMD, "D_SOD-123.step"), "SOD123": (_SMD, "D_SOD-123.step"),
    "SOD-123FL": (_SMD, "D_SOD-123F.step"), "SOD-123F": (_SMD, "D_SOD-123F.step"),
    "SOD123F": (_SMD, "D_SOD-123F.step"),
    "SOD-323": (_SMD, "D_SOD-323.step"), "SOD323": (_SMD, "D_SOD-323.step"),
    "SOD-323F": (_SMD, "D_SOD-323F.step"),
    "SOD-523": (_SMD, "D_SOD-523.step"), "SOD523": (_SMD, "D_SOD-523.step"),
    "SOD-128": (_SMD, "D_SOD-128.step"),
    "SOD-110": (_SMD, "D_SOD-110.step"), "SOD110": (_SMD, "D_SOD-110.step"),
    "SOD-923": (_SMD, "D_SOD-923.step"),
    "SOD-882": (_SMD, "D_SOD-882.step"), "SOD882": (_SMD, "D_SOD-882.step"),
    # MELF family (SOD-80 / DO-213)
    "SOD-80": (_SMD, "D_MiniMELF.step"), "SOD-80C": (_SMD, "D_MiniMELF.step"),
    "SOD80": (_SMD, "D_MiniMELF.step"), "DO-213AB": (_SMD, "D_MiniMELF.step"),
    # chip
    "0402": (_SMD, "D_0402_1005Metric.step"),
    "0603": (_SMD, "D_0603_1608Metric.step"),
    # SOT / power SMD
    "SOT23-3": (_SOT, "SOT-23.step"), "SOT23-5": (_SOT, "SOT-23-5.step"),
    "SOT23-6": (_SOT, "SOT-23-6.step"),
    "SOT323": (_SOT, "SOT-323_SC-70.step"),
    "SOT363": (_SOT, "SOT-363_SC-70-6.step"),
    "SOT143": (_SOT, "SOT-143.step"), "SOT143B": (_SOT, "SOT-143.step"),
    "SOT89": (_SOT, "SOT-89-3.step"),
    "DPAK": (_SOT, "TO-252-2.step"), "D-PAK": (_SOT, "TO-252-2.step"),
    "D2PAK": (_SOT, "TO-263-2.step"),
}


def model_ref(package: str) -> str | None:
    """Return a ``${KICAD10_3DMODEL_DIR}/...`` model reference, or None if unmapped."""
    entry = PACKAGE_MODEL.get((package or "").strip())
    if not entry:
        return None
    lib, fname = entry
    return f"{ENV}/{lib}/{fname}"
