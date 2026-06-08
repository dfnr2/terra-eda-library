"""Lock the footprint type-attribute derivation (smd / through_hole)."""
from tools.fix_footprint_attrs import fix, footprint_type

_SMD = '''\
(footprint "X"
\t(layer "F.Cu")
\t(descr "a smd part")
\t(pad "1" smd roundrect (at 0 0))
)
'''

_THT = '''\
(footprint "Y"
\t(layer "F.Cu")
\t(descr "a tht part")
\t(attr allow_missing_courtyard)
\t(pad "1" thru_hole circle (at 0 0))
\t(pad "2" smd roundrect (at 5 0))
)
'''

_NPTH = '''\
(footprint "Z"
\t(layer "F.Cu")
\t(descr "a mounting hole")
\t(pad "" np_thru_hole circle (at 0 0))
)
'''


def test_type_from_pads():
    assert footprint_type(_SMD) == "smd"
    assert footprint_type(_THT) == "through_hole"   # any thru_hole pad wins
    assert footprint_type(_NPTH) is None


def test_inserts_attr_after_descr():
    new, changed = fix(_SMD)
    assert changed and "(attr smd)" in new
    # inserted right after the descr line
    assert new.index("(attr smd)") > new.index("(descr")


def test_preserves_existing_flags():
    new, changed = fix(_THT)
    assert changed
    assert "(attr through_hole allow_missing_courtyard)" in new


def test_idempotent():
    once, _ = fix(_SMD)
    twice, changed = fix(once)
    assert not changed and twice == once


def test_npth_left_unset():
    new, changed = fix(_NPTH)
    assert not changed and "(attr" not in new
