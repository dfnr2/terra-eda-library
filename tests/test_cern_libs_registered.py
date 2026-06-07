from pathlib import Path
from tools import cern_libmap as lm

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_lib_present():
    assert (ROOT / "kicad_symbols/cern-diodes.kicad_sym").is_file()


def test_footprint_libs_present():
    for d in ["cern-ics-and-semiconductors-smd.pretty",
              "cern-ics-and-semiconductors-thd.pretty",
              "cern-ics-and-semiconductors-bonding.pretty"]:
        assert (ROOT / "kicad_footprints" / d).is_dir()


def test_every_nick_is_in_generated_lib_tables():
    """The build-generated lib-tables must register every nickname the parts use."""
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for nick in lm.SYMBOL_LIB_NICK.values():
        assert f'(name "{nick}")' in sym, f"unregistered symbol nick: {nick}"
    for nick in lm.FOOTPRINT_LIB_NICK.values():
        assert f'(name "{nick}")' in fp, f"unregistered footprint nick: {nick}"
