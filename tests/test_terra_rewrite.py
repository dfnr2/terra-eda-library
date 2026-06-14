# tests/test_terra_rewrite.py
# Locks in the stage-4b safe core: pin parsing + the pin-preserving transform search.
# The contract: terra pins land on the same board coords as the legacy pins of the
# SAME number, so (reference, pin-number) -> net membership is preserved.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import terra_rewrite as tr  # noqa: E402


def _abs_after(terra_pins, t):
    """Absolute coords of terra pins under a found transform, keyed by pin number."""
    pl = tr.Placement(t.x, t.y, t.rot, t.mirror)
    return {p.number: tr._place(p.x, p.y, pl) for p in terra_pins}


def _legacy_abs(legacy_pins, at):
    return {p.number: tr._place(p.x, p.y, at) for p in legacy_pins}


def test_parse_pins_connection_points():
    sym = '''(symbol "R_US_1_1"
        (rectangle (start -1 -2) (end 1 2))
        (pin passive line (at 0 3.81 270) (length 1.27) (name "~" ...) (number "1" ...))
        (pin passive line (at 0 -3.81 90) (length 1.27) (name "~" ...) (number "2" ...)))'''
    pins = tr.parse_pins(sym)
    assert {(p.number, p.x, p.y) for p in pins} == {("1", 0.0, 3.81), ("2", 0.0, -3.81)}


# Real geometry from the boards: legacy nema resistor is horizontal (origin at pin 2);
# Device:R_US is vertical and centered. Instance placed at (52.07, 63.5, 90).
LEGACY_RES = [tr.Pin("1", "", 7.62, 0.0), tr.Pin("2", "", 0.0, 0.0)]
TERRA_R_US = [tr.Pin("1", "", 0.0, 3.81), tr.Pin("2", "", 0.0, -3.81)]
RES_AT = tr.Placement(52.07, 63.5, 90)


def test_resistor_transform_preserves_pins():
    t = tr.find_transform(LEGACY_RES, RES_AT, TERRA_R_US)
    assert t is not None
    # the proof: every same-numbered terra pin lands on its legacy pin's coordinate
    assert _abs_after(TERRA_R_US, t) == _legacy_abs(LEGACY_RES, RES_AT)


def test_transform_is_by_pin_number_not_just_position():
    # A polarized 2-pin part (pins carry roles via number). The transform must map
    # terra pin "1" onto legacy pin "1" (anode->anode), never swap them.
    legacy = [tr.Pin("1", "A", 2.54, 0.0), tr.Pin("2", "K", -2.54, 0.0)]
    terra = [tr.Pin("1", "A", 0.0, 2.54), tr.Pin("2", "K", 0.0, -2.54)]
    at = tr.Placement(100.0, 100.0, 0)
    t = tr.find_transform(legacy, at, terra)
    assert t is not None
    after, before = _abs_after(terra, t), _legacy_abs(legacy, at)
    assert after == before
    assert after["1"] == before["1"] and after["2"] == before["2"]


def test_no_transform_when_pin_counts_differ():
    terra3 = TERRA_R_US + [tr.Pin("3", "", 0.0, 0.0)]
    assert tr.find_transform(LEGACY_RES, RES_AT, terra3) is None


def test_no_transform_when_pin_span_differs():
    # terra pins 5.08 apart vs legacy 7.62 apart -> no rotation/mirror+translation aligns them
    terra_narrow = [tr.Pin("1", "", 0.0, 2.54), tr.Pin("2", "", 0.0, -2.54)]
    assert tr.find_transform(LEGACY_RES, RES_AT, terra_narrow) is None


def test_idempotent_same_symbol_is_identity():
    # legacy already == terra symbol -> a transform exists (rot 0, zero offset)
    t = tr.find_transform(LEGACY_RES, tr.Placement(10.0, 20.0, 0), LEGACY_RES)
    assert t is not None and t.rot == 0 and t.mirror is None and (t.x, t.y) == (10.0, 20.0)
