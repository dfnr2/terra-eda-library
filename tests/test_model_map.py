"""Lock the codified CERN package -> KiCad 3D model resolution rules.

The point of tools/model_map is that the mapping is decided once, in code.
These tests pin the decisions so a future edit can't silently change them.
"""
import pytest

from tools.model_map import (
    AXIAL_PITCH_TOL_MM, kicad_3dmodel_dir, resolve_model,
)

_HAVE_KICAD = kicad_3dmodel_dir() is not None
_needs_kicad = pytest.mark.skipif(
    not _HAVE_KICAD, reason="KiCad bundled 3dmodels not installed")


def test_exact_smd_package():
    assert resolve_model("DO-214AC").endswith("/Diode_SMD.3dshapes/D_SMA.step")
    assert resolve_model("SOD-123").endswith("/Diode_SMD.3dshapes/D_SOD-123.step")
    assert resolve_model("SOT23-3").endswith("/Package_TO_SOT_SMD.3dshapes/SOT-23.step")


def test_unknown_package_is_none():
    assert resolve_model("NO-SUCH-PACKAGE") is None


def test_axial_needs_pitch():
    # Without a measured pitch an axial family cannot be resolved.
    assert resolve_model("DO-41") is None


@_needs_kicad
def test_axial_exact_pitch():
    ref = resolve_model("DO-41", pad_pitch_mm=10.16)
    assert ref.endswith("_P10.16mm_Horizontal.step")
    assert "D_DO-41_SOD81" in ref


@_needs_kicad
def test_axial_nearest_within_tolerance():
    # DO-15 at 13.97mm has no exact model; nearest (15.24) is within tolerance.
    ref = resolve_model("DO-15", pad_pitch_mm=13.97)
    assert ref is not None and ref.endswith("_P15.24mm_Horizontal.step")


@_needs_kicad
def test_axial_gross_mismatch_declined():
    # DO-201AD footprint at 20.32mm exceeds any bundled model -> no fit.
    assert resolve_model("DO-201AD", pad_pitch_mm=20.32) is None
    # DO-41 ships 7.62/10.16/12.70mm; 20mm is beyond all of them -> declined.
    assert resolve_model("DO-41", pad_pitch_mm=20.0) is None


@_needs_kicad
def test_to_orientation_and_leads():
    v = resolve_model("TO-247", orientation="v", leads=2)
    assert v.endswith("/Package_TO_SOT_THT.3dshapes/TO-247-2_Vertical.step")
    h = resolve_model("TO-220-2", orientation="h", leads=2)
    assert h.endswith("/Package_TO_SOT_THT.3dshapes/TO-220-2_Horizontal_TabUp.step")


@_needs_kicad
def test_to_horizontal_to247_declined():
    # KiCad ships only Vertical TO-247 models; horizontal has no fit.
    assert resolve_model("TO-247", orientation="h", leads=2) is None
