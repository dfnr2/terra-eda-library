from tools.cern_datasheets import verify


def test_exact_mpn_required():
    text = "EATON 0402ESDA-MLP  Working Voltage 8kV  ESD Suppressor"
    assert verify.check_text(text, "0402ESDA-MLP", params=["8kV"]) == "ok"


def test_mpn_mismatch():
    text = "Some other part 1N4148  100V"
    assert verify.check_text(text, "0402ESDA-MLP", params=["8kV"]) == "mpn_mismatch"


def test_unparseable_empty_text():
    assert verify.check_text("", "0402ESDA-MLP", params=["8kV"]) == "unparseable"


def test_param_missing_is_review():
    text = "EATON 0402ESDA-MLP ESD Suppressor"
    assert verify.check_text(text, "0402ESDA-MLP", params=["8kV"]) == "param_missing"
