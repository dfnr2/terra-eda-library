from tools import cern_libmap as lm


def test_symbol_rewrite():
    assert lm.rewrite_ref("Diodes:Diode TVS Bi-Directional", lm.SYMBOL_LIB_NICK) \
        == "cern-diodes:Diode TVS Bi-Directional"


def test_footprint_rewrite():
    assert lm.rewrite_ref("ICs And Semiconductors SMD:EATON_0402ESDA-MLP", lm.FOOTPRINT_LIB_NICK) \
        == "cern-ics-and-semiconductors-smd:EATON_0402ESDA-MLP"


def test_unknown_lib_passthrough():
    assert lm.rewrite_ref("Other:Thing", lm.FOOTPRINT_LIB_NICK) == "Other:Thing"


def test_empty_and_no_colon():
    assert lm.rewrite_ref("", lm.SYMBOL_LIB_NICK) == ""
    assert lm.rewrite_ref("NoColon", lm.SYMBOL_LIB_NICK) == "NoColon"
