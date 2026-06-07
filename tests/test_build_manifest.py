from tools.cern_datasheets import build_manifest as bm


def test_manifest_dedups_by_filename():
    rows = [
        {"Manufacturer Part Number": "A1", "Manufacturer": "M",
         "Datasheet": "${CERN_DATASHEET_DIR}\\\\1.5KE.pdf"},
        {"Manufacturer Part Number": "A2", "Manufacturer": "M",
         "Datasheet": "${CERN_DATASHEET_DIR}\\\\1.5KE.pdf"},
        {"Manufacturer Part Number": "B1", "Manufacturer": "N",
         "Datasheet": "${CERN_DATASHEET_DIR}\\\\OTHER.pdf"},
    ]
    man = bm.build(rows)
    assert set(man) == {"1.5KE.pdf", "OTHER.pdf"}
    assert sorted(man["1.5KE.pdf"]["mpns"]) == ["A1", "A2"]
    assert man["1.5KE.pdf"]["status"] == "pending"
    assert man["OTHER.pdf"]["verify"] == "unchecked"
