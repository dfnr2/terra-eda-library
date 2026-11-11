# tests/test_passive_units.py
"""Passive value strings carry unit signs; Sim.Params carries the same number."""
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from passive_units import parse_si, sim_params, unit_value  # noqa: E402

# table -> (sim device, unit sign, Sim.Params key)
PASSIVE_TABLES = {
    "resistors_smt": ("R", "Ω", "r"),
    "resistors_th": ("R", "Ω", "r"),
    "capacitors_smt": ("C", "F", "c"),
    "capacitors_th": ("C", "F", "c"),
    "capacitors_electrolytic_th": ("C", "F", "c"),
    "inductors": ("L", "H", "l"),
}


@pytest.mark.parametrize("text,unit,expected", [
    ("0.5p", "F", "0.5pF"), ("1u", "F", "1µF"), ("100n", "F", "100nF"),
    ("1.1n", "F", "1.1nF"), ("910µF", "F", "910µF"),
    ("1000u", "F", "1000µF"), ("10000µF", "F", "10000µF"),
    ("10kΩ", "Ω", "10kΩ"), ("1.02MΩ", "Ω", "1.02MΩ"), ("9mΩ", "Ω", "9mΩ"),
    ("22uH", "H", "22µH"), ("68 µH", "H", "68µH"),
])
def test_unit_value(text, unit, expected):
    assert unit_value(text, unit) == expected


@pytest.mark.parametrize("device,text,expected", [
    ("R", "4.7MΩ", "r=4.7Meg"),   # SPICE: bare M/m is milli, mega is Meg
    ("R", "1.02MΩ", "r=1.02Meg"),
    ("R", "10kΩ", "r=10k"),
    ("R", "9mΩ", "r=9m"),
    ("R", "0Ω", "r=1u"),          # ngspice rejects a zero-valued resistor
    ("C", "0.5p", "c=0.5p"),
    ("C", "910µF", "c=910u"),
    ("C", "10000µF", "c=10m"),
    ("L", "22µH", "l=22u"),
])
def test_sim_params(device, text, expected):
    assert sim_params(device, text) == expected


def test_parse_si_rejects_junk():
    with pytest.raises(ValueError):
        parse_si("IND Bourns 10uH 1.1A rms")


def _spice_number(text):
    """Parse a Sim.Params number, where 'Meg' is mega and 'm' is milli."""
    return parse_si(text.replace("Meg", "M"))


@pytest.fixture(scope="module")
def db():
    path = ROOT / "db" / "terra.db"
    if not path.exists():
        pytest.skip("db/terra.db not built")
    con = sqlite3.connect(path)
    yield con
    con.close()


@pytest.mark.parametrize("table", PASSIVE_TABLES)
def test_passive_rows_have_unit_sign_and_matching_sim_params(db, table):
    device, unit, key = PASSIVE_TABLES[table]
    rows = db.execute(f'SELECT unique_id, value, sim_device, sim_params FROM "{table}"').fetchall()
    assert rows, f"{table} is empty"
    bad = []
    for uid, value, sim_device, params in rows:
        if sim_device != device or not value or not value.endswith(unit):
            bad.append((uid, value, sim_device, params))
            continue
        name, _, number = (params or "").partition("=")
        if name != key or not number:
            bad.append((uid, value, sim_device, params))
            continue
        want, got = parse_si(value), _spice_number(number)
        zero_jumper = want == 0 and got <= 1e-6
        if not zero_jumper and abs(want - got) > 1e-9 * max(want, got):
            bad.append((uid, value, sim_device, params))
    assert not bad, f"{len(bad)} {table} rows with bad value/sim_params, e.g. {bad[:3]}"
