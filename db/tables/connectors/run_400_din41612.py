#!/usr/bin/env python3
"""Harting DIN 41612 (DIN-Signal) Eurocard connectors: types B and C, 64 and 96 contacts.

Each layout comes as an angled male (on the plug-in card) and a straight female (on
the backplane), performance level 2 (IEC 60603-2), solder pins:

  | Layout              | Male, angled (card) | Female, straight (backplane) |
  |---------------------|---------------------|------------------------------|
  | Type C, 96, a+b+c   | 09 03 196 6921      | 09 03 296 6825               |
  | Type B, 64, a+b     | 09 02 164 6921      | 09 02 264 6825               |
  | Type C, 64, a+c     | 09 03 164 6921      | 09 03 264 6825               |

Harting part numbers are stored without spaces (09031966921), as distributors list them.
Data sheets: datasheets/harting/harting-<pn>-din41612-*-datasheet.pdf (Harting
eCatalogue extracts, 2026-10), family drawings in harting-din41612-catalogue-chapter01.pdf.
All six give 2 A rated current (at 20 C, derating curve in the sheet), -55 to +125 C
limiting temperature, 1 kV r.m.s. test voltage, contact resistance <= 20 mOhm,
insulation resistance > 10^12 Ohm, >= 400 mating cycles, glass-filled thermoplastic
RAL 7032 pebble grey, UL94 V-0; coding with loss of contacts (coding pin 09 02 000 9901).
No rated working voltage is given, so voltage_rating stays blank.

Footprints are KiCad's stock Connector_DIN ones, which KiCad drew from Harting's
DIN 41612 catalogue (pads a1.., b1.., c1.., 88.9 mm fixing holes); type C uses KiCad's
3D models too. KiCad ships no type B models, so the two type B footprints are copied
unchanged into terra_footprints_connectors with their model path pointed at a generated
block model (model_specs below, from the catalogue drawings on chapter-01 pages 3 and 5:
male 85.2 mm body, 8.6 mm high, 3 mm tails; female 85 mm body, 8.1 mm deep, 11.6 mm
high, 7.9 mm flanges, 4.5 mm tails). Symbols:
stock Connector:DIN41612_02x32_AB / _AC for the 64-contact layouts; KiCad has only a
split 96-contact symbol, so the whole-connector 96 symbol is a terra one
(DIN41612_03x32_ABC: a and b down the left, c on the right beside a). Each part also gets
a `-pins` per-pin symbol row (_connkit.py). Plan: plans/connectors-din41612.md.
Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _conn156 import check_datasheets, write  # noqa: E402
from _conn156 import FP_LIB  # noqa: E402
from _connkit import SYM_LIB, dual_column_symbol, per_pin_symbol, with_pins, write_symbols  # noqa: E402

OUTPUT_FILE = HERE / "connectors_generated_400_din41612.sql"
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets/harting"

# (part number, type, rows, gender, Harting identification)
PARTS = [
    ("09031966921", "C", "abc", "male", "C096MS-3,0C1-2"),
    ("09032966825", "C", "abc", "female", "C096FS-4,5C1-2"),
    ("09021646921", "B", "ab", "male", "B064MS-3,0C1-2"),
    ("09022646825", "B", "ab", "female", "B064FS-4,5C1-2"),
    ("09031646921", "C", "ac", "male", "C064MS-3,0C1-2"),
    ("09032646825", "C", "ac", "female", "C064FS-4,5C1-2"),
]

ABC_WHOLE = "DIN41612_03x32_ABC"


def numbers(rows):
    return [f"{r}{i}" for r in rows for i in range(1, 33)]


def whole_symbol(rows):
    if rows == "ab":
        return "Connector:DIN41612_02x32_AB"
    if rows == "ac":
        return "Connector:DIN41612_02x32_AC"
    return f"{SYM_LIB}:{ABC_WHOLE}"


def pins_name(rows):
    return f"Conn_PerPin_DIN41612_{rows.upper()}_{len(rows)}x32"


def footprint(typ, rows, gender):
    n = len(rows)
    style = "Male_Horizontal" if gender == "male" else "Female_Vertical"
    lib = FP_LIB if typ == "B" else "Connector_DIN"    # type B: terra copy with a model
    return f"{lib}:DIN41612_{typ}_{n}x32_{style}_THT"


def model_specs():
    """Block models for the terra copies of KiCad's type B footprints (pin a1 at the
    origin; male: rows along +x, mating face toward -y; female: rows along +y)."""
    mid = 31 * 2.54 / 2
    male = [("box", "grey", mid - 42.6, -12.74, 0, mid + 42.6, -1.5, 8.6),
            ("box", "grey", -7.89, -5.0, 0, mid - 42.6, 0.26, 3.7),
            ("box", "grey", mid + 42.6, -5.0, 0, 86.37, 0.26, 3.7)]
    for i in range(32):
        x = i * 2.54
        male += [("pin", "tin", x, 0, -3.0, 2.54, 0.6), ("hpin", "tin", x, 0, -1.5, 2.54, 0.6),
                 ("pin", "tin", x, 2.54, -3.0, 5.08, 0.6), ("hpin", "tin", x, 2.54, -1.5, 5.08, 0.6)]
    female = [("box", "grey", -2.78, mid - 42.5, 0, 5.32, mid + 42.5, 11.6),
              ("box", "grey", -3.76, -8.13, 0, 5.32, mid - 42.5, 7.9),
              ("box", "grey", -3.76, mid + 42.5, 0, 5.32, 86.87, 7.9)]
    for i in range(32):
        female += [("pin", "tin", 0, i * 2.54, -4.5, 0.5, 0.6),
                   ("pin", "tin", 2.54, i * 2.54, -4.5, 0.5, 0.6)]
    return {"DIN41612_B_2x32_Male_Horizontal_THT": male,
            "DIN41612_B_2x32_Female_Vertical_THT": female}


def symbols():
    out = [(ABC_WHOLE, dual_column_symbol(
        ABC_WHOLE, numbers("a") + [None] + numbers("b"), numbers("c"),
        "DIN 41612 connector, type C, 3 rows a, b, c x 32 (96 contacts); rows a and b "
        "down the left, row c on the right", fp_filters="DIN41612*3x32*"))]
    for rows in ("ab", "ac", "abc"):
        name = pins_name(rows)
        out.append((name, per_pin_symbol(
            name, numbers(rows),
            f"DIN 41612 connector, rows {', '.join(rows)} x 32, one unit per contact",
            fp_filters=f"DIN41612*{len(rows)}x32*")))
    return out


FAMILY = {
    "connector_category": "board-to-board", "connector_family": "DIN 41612",
    "pitch_mm": 2.54, "termination_type": "Through Hole", "polarized": "no",
    "keying_detail": "optional coding pins (09 02 000 9901), coding with loss of contacts",
    "locking_mechanism": "none", "shielding": "unshielded",
    "color": "pebble grey (RAL 7032)", "current_rating": 2.0,
    "contact_resistance_mohm": 20.0, "insulation_resistance_mohm": 1.0e6,
    "dielectric_withstand_vrms": 1000.0, "signal_type": "mixed",
    "flammability_rating": "UL94-V0",
    "temp_operating_min": -55.0, "temp_operating_max": 125.0,
    "lifecycle_status": "Active", "rohs": "Yes",
    "allow_substitution": "No", "tracking": "No",
    "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
}

COLS_EXTRA = ["row_pitch_mm", "contact_resistance_mohm", "insulation_resistance_mohm",
              "dielectric_withstand_vrms"]


def spaced(pn):
    return f"{pn[:2]} {pn[2:4]} {pn[4:7]} {pn[7:]}"


def datasheet(pn, ident):
    return f"{DS}/harting-{pn}-din41612-{ident[:6].lower()}-datasheet.pdf"


def parts():
    for pn, typ, rows, gender, ident in PARTS:
        n = 32 * len(rows)
        male = gender == "male"
        orient = "right-angle" if male else "vertical"
        mate = next(p for p in PARTS if p[2] == rows and p[1] == typ and p[3] != gender)
        row_txt = "+".join(rows)
        yield {
            **FAMILY,
            "unique_id": f"Harting-{pn}",
            "part_locator": (f"conn-din41612-{typ.lower()}-{n}pos-{row_txt.replace('+', '')}-"
                             f"{gender}-{orient}-th"),
            "mpn": pn, "manufacturer": "Harting", "value": pn,
            "description": (
                f"Harting DIN-Signal {ident} ({spaced(pn)}), DIN 41612 type {typ}, "
                f"{n} contacts, rows {row_txt} x 32, 2.54mm pitch, {gender}, "
                f"{'angled solder pins (plug-in card)' if male else 'straight solder pins (backplane)'}, "
                "performance level 2, gold over nickel contacts, with fixing flange"),
            "datasheet": datasheet(pn, ident),
            "manufacturer_link": f"https://www.harting.com/en-US/p/{pn}",
            "kicad_symbol": whole_symbol(rows),
            "kicad_footprint": footprint(typ, rows, gender),
            "keywords": (
                f"connector,DIN 41612,DIN41612,IEC 60603-2,eurocard,VME,backplane,harting,"
                f"DIN-Signal,{ident},{pn},{spaced(pn)},type {typ},{n}-pin,{gender},{orient}"),
            "pin_count": str(n), "positions": n,
            "connector_series": f"DIN-Signal {typ}{n:03d}",
            "connector_type": "header" if male else "receptacle",
            "rows": len(rows), "row_pitch_mm": 5.08 if rows == "ac" else 2.54,
            "orientation": orient, "gender": gender,
            "mating_family": f"DIN 41612 type {typ} {n}-contact {'female' if male else 'male'} connectors",
            "mates_with": f"Harting {spaced(mate[0])} ({mate[4]})",
        }


def main():
    check_datasheets([datasheet(p[0], p[4]) for p in PARTS])
    write_symbols(symbols())
    rows = with_pins(list(parts()), lambda r: f"{SYM_LIB}:{pins_name(next(p[2] for p in PARTS if p[0] == r['mpn']))}")
    write(OUTPUT_FILE, "Harting DIN 41612 connectors", CREATED_BY, rows, extra_cols=COLS_EXTRA)


if __name__ == "__main__":
    main()
