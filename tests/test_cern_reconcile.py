from tools import cern_reconcile as rc


def test_reuses_existing_unique_id_case_insensitive():
    index = {("onsemi", "mbr0530t1g"): "OnSemi-MBR0530T1G"}
    assert rc.resolve_unique_id("OnSemi", "MBR0530T1G", index) == "OnSemi-MBR0530T1G"
    assert rc.resolve_unique_id("ONSEMI", " mbr0530t1g ", index) == "OnSemi-MBR0530T1G"


def test_mints_new_id_when_no_match():
    assert rc.resolve_unique_id("EATON", "0402ESDA-MLP", {}) == "EATON-0402ESDA-MLP"


def test_index_from_rows():
    rows = [
        {"manufacturer": "EATON", "mpn": "X1", "unique_id": "EATON-X1"},
        {"manufacturer": "Foo", "mpn": "Y2", "unique_id": "Foo-Y2"},
    ]
    idx = rc.index_from_rows(rows)
    assert idx[("eaton", "x1")] == "EATON-X1"
    assert len(idx) == 2
