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


def test_cern_nicks_are_not_in_generated_lib_tables():
    """CERN libraries are present as source material, not registered in KiCad."""
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for nick in lm.SYMBOL_LIB_NICK.values():
        assert f'(name "{nick}")' not in sym, f"registered quarantined symbol nick: {nick}"
    for nick in lm.FOOTPRINT_LIB_NICK.values():
        assert f'(name "{nick}")' not in fp, f"registered quarantined footprint nick: {nick}"


def test_terra_owned_libs_are_in_generated_lib_tables():
    """Only terra-owned libraries should be exposed through the generated tables."""
    sym = (ROOT / "kicad_symbols/sym-lib-table").read_text()
    fp = (ROOT / "kicad_footprints/fp-lib-table").read_text()
    for path in sorted((ROOT / "kicad_symbols").glob("terra*.kicad_sym")):
        assert f'(name "{path.stem}")' in sym, f"unregistered terra symbol lib: {path.stem}"
    for path in sorted((ROOT / "kicad_footprints").glob("terra*.pretty")):
        assert f'(name "{path.stem}")' in fp, f"unregistered terra footprint lib: {path.stem}"
