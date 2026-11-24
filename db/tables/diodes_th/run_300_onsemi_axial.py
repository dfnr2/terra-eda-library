#!/usr/bin/env python3
"""onsemi axial-lead diodes: the everyday JEDEC through-hole parts.

Four onsemi data sheets, parked in datasheets/onsemi/:
  - 1n914-d.pdf (1N914/D Rev 6, Sep 2024): 1N914, 1N4148, 1N4448 small-signal switching
    diodes, DO-35 (DO-204AH). VRRM 100 V, IO 200 mA, IF 300 mA, IFSM 4 A (1 ms) / 1 A (1 s),
    PD 500 mW, trr 4 ns, TJ -55 to +175 C.
  - 1n4001-d.pdf (1N4001/D Rev 18, Jun 2024): 1N4001-1N4007 1 A rectifiers, Case 59-10
    (DO-41). IO 1.0 A, IFSM 30 A, vF 1.1 V max at 1 A, TJ -65 to +150 C. The un-suffixed
    leaded codes (1N4001 ...) are DISCONTINUED there; the Pb-free "G" codes are current.
  - 1n5817-d.pdf (1N5817/D Rev 11, Aug 2021): 1N5817/8/9 1 A Schottky rectifiers, Case 59
    (DO-41). IO 1.0 A, IFSM 25 A, TJ -65 to +125 C.
  - 1n5400-d.pdf (1N5400/D Rev 12, Aug 2021): 1N5400-1N5408 3 A rectifiers, Case 267-05
    (DO-201AD). onsemi makes no 1N5403 or 1N5405. IO 3.0 A, IFSM 200 A, vF 1.0 V max at
    3 A, TJ -65 to +150 C.

Ordering codes are the bulk/bag (or box) packs: 1N914, 1N4148, 1N4448, 1N400xG, 1N581xG,
1N540xG. All were in stock at Mouser from onsemi on 2026-11-24, so all are Active.
`value` is the JEDEC number, which is what a schematic shows.

Symbols are KiCad's stock Diode:<JEDEC> (pin 1 = K, pin 2 = A), footprints the ones those
symbols name: DO-35 at 7.62 mm, DO-41 at 10.16 mm, DO-201AD at 15.24 mm, horizontal.
Plan: plans/diodes-th.md.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _diodes_th import PKG, check_datasheets, write  # noqa: E402

OUTPUT_FILE = HERE / "diodes_th_generated_300_onsemi_axial.sql"
CREATED_BY = Path(__file__).name
MFR_LINK = "https://www.onsemi.com/products/discrete-power-modules"

# (JEDEC, VF text) for the small-signal sheet.
SMALL_SIGNAL = [
    ("1N914", "1.0V @ 10mA", "4pF"),
    ("1N4148", "1.0V @ 10mA", "4pF"),
    ("1N4448", "1.0V @ 100mA (0.62-0.72V @ 5mA)", "2pF"),
]
R1A = [("1N4001", 50), ("1N4002", 100), ("1N4003", 200), ("1N4004", 400),
       ("1N4005", 600), ("1N4006", 800), ("1N4007", 1000)]
SCHOTTKY = [("1N5817", 20, "0.45V"), ("1N5818", 30, "0.55V"), ("1N5819", 40, "0.6V")]
R3A = [("1N5400", 50), ("1N5401", 100), ("1N5402", 200), ("1N5404", 400),
       ("1N5406", 600), ("1N5407", 800), ("1N5408", 1000)]


def base(jedec, mpn, pkg, ds, link):
    return {
        "unique_id": f"onsemi-{mpn}", "mpn": mpn, "manufacturer": "onsemi",
        "value": jedec, "package": pkg, "pin_count": "2",
        "datasheet": f"${{TERRA_EDA_LIB}}/datasheets/onsemi/{ds}",
        "manufacturer_link": f"{MFR_LINK}/{link}/{jedec.lower()}",
        "kicad_symbol": f"Diode:{jedec}", "kicad_footprint": PKG[pkg],
        "lifecycle_status": "Active", "rohs": "Yes", "allow_substitution": "Yes",
        "tracking": "No", "created_by": CREATED_BY,
    }


def parts():
    for jedec, vf, ct in SMALL_SIGNAL:
        yield {
            **base(jedec, jedec, "DO-35", "1n914-d.pdf", "small-signal-switching-diodes"),
            "part_locator": "diode-small-signal-100v-200ma-do35",
            "description": (f"Small-signal switching diode {jedec}, 100V, 200mA (IF 300mA), "
                            f"VF {vf}, trr 4ns, CT {ct}, 500mW, DO-35"),
            "keywords": f"diode,small signal,switching,signal diode,{jedec},DO-35,axial,through-hole",
            "diode_type": "small-signal", "voltage_rating": "100V", "forward_voltage": vf,
            "forward_current": "300mA", "current_rating": "200mA", "power_rating": "500mW",
            "temp_operating_min": -55.0, "temp_operating_max": 175.0,
            "temp_storage_min": -65.0, "temp_storage_max": 200.0,
        }
    for jedec, v in R1A:
        yield {
            **base(jedec, f"{jedec}G", "DO-41", "1n4001-d.pdf", "rectifiers"),
            "part_locator": f"diode-rectifier-{v}v-1a-do41",
            "description": (f"Standard-recovery rectifier {jedec}, {v}V, 1A, IFSM 30A, "
                            "VF 1.1V @ 1A, glass passivated, DO-41"),
            "keywords": f"diode,rectifier,1A,{jedec},{jedec}G,DO-41,axial,through-hole",
            "diode_type": "rectifier", "voltage_rating": f"{v}V", "forward_voltage": "1.1V @ 1A",
            "forward_current": "1A", "current_rating": "1A",
            "temp_operating_min": -65.0, "temp_operating_max": 150.0,
            "temp_storage_min": -65.0, "temp_storage_max": 150.0,
        }
    for jedec, v, vf in SCHOTTKY:
        yield {
            **base(jedec, f"{jedec}G", "DO-41", "1n5817-d.pdf",
                   "schottky-diodes-schottky-rectifiers"),
            "part_locator": f"diode-schottky-{v}v-1a-do41",
            "description": f"Schottky rectifier {jedec}, {v}V, 1A, IFSM 25A, VF {vf} @ 1A, DO-41",
            "keywords": f"diode,schottky,rectifier,1A,{jedec},{jedec}G,DO-41,axial,through-hole",
            "diode_type": "schottky", "voltage_rating": f"{v}V", "forward_voltage": f"{vf} @ 1A",
            "forward_current": "1A", "current_rating": "1A",
            "temp_operating_min": -65.0, "temp_operating_max": 125.0,
            "temp_storage_min": -65.0, "temp_storage_max": 125.0,
        }
    for jedec, v in R3A:
        yield {
            **base(jedec, f"{jedec}G", "DO-201AD", "1n5400-d.pdf", "rectifiers"),
            "part_locator": f"diode-rectifier-{v}v-3a-do201ad",
            "description": (f"Standard-recovery rectifier {jedec}, {v}V, 3A, IFSM 200A, "
                            "VF 1.0V @ 3A, DO-201AD"),
            "keywords": f"diode,rectifier,3A,{jedec},{jedec}G,DO-201AD,axial,through-hole",
            "diode_type": "rectifier", "voltage_rating": f"{v}V", "forward_voltage": "1.0V @ 3A",
            "forward_current": "3A", "current_rating": "3A",
            "temp_operating_min": -65.0, "temp_operating_max": 150.0,
            "temp_storage_min": -65.0, "temp_storage_max": 150.0,
        }


def main():
    rows = list(parts())
    check_datasheets(rows)
    write(OUTPUT_FILE, "onsemi axial-lead diodes", CREATED_BY, rows)


if __name__ == "__main__":
    main()
