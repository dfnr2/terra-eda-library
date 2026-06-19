import importlib.util
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "db/tables/cern_diodes/run_100_cern_import.py"


def _load():
    spec = importlib.util.spec_from_file_location("cern_diodes_gen", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_sqlstr_escapes_quotes():
    mod = _load()
    assert mod.sqlstr("a'b") == "'a''b'"
    assert mod.sqlstr(None) == "''"


def test_diode_type_parsed():
    mod = _load()
    assert mod.diode_type_from_symbol("Diodes:Diode TVS Bi-Directional") == "TVS Bi-Directional"
    assert mod.diode_type_from_symbol("Diodes:Diode Schottky") == "Schottky"


def test_lifecycle_mapping():
    mod = _load()
    assert mod.map_lifecycle(None) == "Active"
    assert mod.map_lifecycle("") == "Active"
    assert mod.map_lifecycle("Obsolete") == "Obsolete"
    assert mod.map_lifecycle("Not Recommended") == "NRND"
    assert mod.map_lifecycle("Sourcing Difficulty") == "NRND"


def test_map_row_known_part():
    mod = _load()
    row = {
        "Part Number": "0402ESDA-MLP",
        "Manufacturer Part Number": "0402ESDA-MLP",
        "Manufacturer": "EATON",
        "Voltage": "8kV", "Power": None, "Pin Count": "2", "Case": "0402",
        "ComponentHeight": "0.44mm", "Status": None,
        "LibSymbol": "Diodes:Diode TVS Bi-Directional",
        "LibFootprint": "ICs And Semiconductors SMD:EATON_0402ESDA-MLP",
        "Part Description": "0.05pF 8kV Bidirectional ESD Voltage Suppressor",
        "Datasheet": "${CERN_DATASHEET_DIR}\\\\0402ESDA-MLP.pdf",
        "ComponentLink1URL": "",
    }
    m = mod.map_row(row)
    assert m["unique_id"] == "EATON-0402ESDA-MLP"
    assert m["part_locator"] == "0402ESDA-MLP"
    assert m["mpn"] == "0402ESDA-MLP"
    assert m["manufacturer"] == "EATON"
    assert m["package"] == "0402"
    assert m["voltage_rating"] == "8kV"
    assert m["power_rating"] == ""
    assert m["pin_count"] == "2"
    assert m["component_height"] == "0.44mm"
    assert m["lifecycle_status"] == "Active"
    assert m["diode_type"] == "TVS Bi-Directional"
    assert m["kicad_symbol"] == "cern-diodes:Diode TVS Bi-Directional"
    assert m["kicad_footprint"] == "cern-ics-and-semiconductors-smd:EATON_0402ESDA-MLP"
    assert m["datasheet"] == "0402ESDA-MLP.pdf"
    assert m["keywords"] == "diode"


def test_finalize_unique_id_disambiguates_on_collision():
    mod = _load()
    seen = {"VISHAY-16CTQ100G"}
    m = {"unique_id": "VISHAY-16CTQ100G", "manufacturer": "VISHAY"}
    row = {"Part Number Nocolon": "16CTQ100GPBF_h"}
    assert mod.finalize_unique_id(m, row, seen) == "VISHAY-16CTQ100GPBF_h"


def test_finalize_unique_id_passthrough_when_unique():
    mod = _load()
    m = {"unique_id": "EATON-0402ESDA-MLP", "manufacturer": "EATON"}
    assert mod.finalize_unique_id(m, {}, set()) == "EATON-0402ESDA-MLP"


def test_denylist_filters_nonparts():
    mod = _load()
    assert mod.is_denylisted({"Part Number": "Empty", "Part Description": ""})
    assert mod.is_denylisted({"Part Number": "FOO Read Me", "Part Description": "x"})
    assert not mod.is_denylisted({"Part Number": "0402ESDA-MLP", "Part Description": "x"})
