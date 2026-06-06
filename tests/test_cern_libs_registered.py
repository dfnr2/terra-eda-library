from pathlib import Path
from tools import cern_libmap as lm

ROOT = Path(__file__).resolve().parents[1]


def test_symbol_file_present():
    assert (ROOT / "assets/symbols/cern/Diodes.kicad_sym").is_file()


def test_footprint_dirs_present():
    for d in ["ICs And Semiconductors SMD.pretty",
              "ICs And Semiconductors THD.pretty",
              "ICs And Semiconductors BONDING.pretty"]:
        assert (ROOT / "assets/footprints/cern" / d).is_dir()


def test_every_nick_is_registered():
    sym = (ROOT / "kicad_config_templates/sym-lib-table").read_text()
    fp = (ROOT / "kicad_config_templates/fp-lib-table").read_text()
    for nick in lm.SYMBOL_LIB_NICK.values():
        assert f'(name "{nick}")' in sym
    for nick in lm.FOOTPRINT_LIB_NICK.values():
        assert f'(name "{nick}")' in fp
