#!/usr/bin/env python3
"""Molex KK 396 friction-lock headers: 3.96 mm (0.156"), single row, 2-18 circuits.

The SWTPC/S-100-era power and wire-to-board header, still in production.
  - series 41791, vertical: 26-60-40NN0 (engineering 41791-00NN), sales drawing
    SDA-41791-000 (datasheets/molex/kk-396-41791-vertical-header-sd.pdf)
  - series 41792, right-angle: 26-60-50NN0 (41792-00NN), sales drawing
    datasheets/molex/kk-396-41792-right-angle-header-sd.pdf
NN = circuits; the trailing 0 is tin plating (the drawings also list a 3 = second
plating, not generated). Molex's catalog number drops the dashes and adds a leading
00 (0026604020); the printed part number 26-60-4020 is the MPN, as distributors use.

Ratings from product specification PS-08-50-001 rev. U (2021-11-24,
datasheets/molex/kk-396-product-spec-ps-08-50-001.pdf): agency 600 V (UL) / 250 V
(CSA) and 7 A single circuit for both series; operating -40 to 80 C with brass pins
(the headers' pin material). Molex's part pages disagree (41791 page: 5.0 A / 600 V;
41792 page: 7.0 A / 250 V); the specification is used: 7.0 A, 600 V.

Mates with KK 396 crimp housings 2139, 3069, 41695 and 6442 (crimp terminals 2478,
2578, 2878) and the 41815 PCB connector, per the Molex part pages and the spec.

Lifecycle: all 34 codes Active at Molex and listed at Mouser, 2026-11-21.
Symbol Connector_Generic:Conn_01xNN; footprints the stock
Connector_Molex:Molex_KK-396_A-4179x-00NN_1xNN_P3.96mm_{Vertical,Horizontal}
(with KiCad's 3D models).

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
Each part also has a per-pin symbol row (`-pins`, _connkit.py).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _connkit import numeric_pins_id, numeric_pins_symbol, with_pins, write_symbols  # noqa: E402
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "connectors_generated_370_molex_kk396.sql"
CREATED_BY = Path(__file__).name

CIRCUITS = range(2, 19)
DS = "${TERRA_EDA_LIB}/datasheets/molex"
MATING = ("Molex KK 396 crimp housings 2139, 3069, 41695, 6442 "
          "(crimp terminals 2478, 2578, 2878); KK 396 PCB connector 41815")

SERIES = {
    "41791": dict(prefix="26-60-4", orientation="vertical", fp_style="Vertical",
                  word="Vertical", datasheet=f"{DS}/kk-396-41791-vertical-header-sd.pdf",
                  tail="3.56mm PC tail"),
    "41792": dict(prefix="26-60-5", orientation="right-angle", fp_style="Horizontal",
                  word="Right-Angle", datasheet=f"{DS}/kk-396-41792-right-angle-header-sd.pdf",
                  tail="3.96mm PC tail"),
}

FAMILY = {
    "connector_category": "wire-to-board", "connector_family": "Molex KK 396",
    "connector_type": "header", "rows": 1, "pitch_mm": 3.96,
    "termination_type": "Through Hole", "gender": "male", "polarized": "yes",
    "keying_detail": "polarizing back wall, friction-lock ramp",
    "locking_mechanism": "friction", "shielding": "unshielded", "color": "natural",
    "current_rating": 7.0, "voltage_rating": 600.0, "signal_type": "power",
    "flammability_rating": "UL94-V0", "mating_family": MATING,
    "mates_with": "2139/3069/41695/6442 crimp housing, same circuit count",
    "temp_operating_min": -40.0, "temp_operating_max": 80.0,
}

COLS = [
    "unique_id", "variant", "part_locator", "mpn", "manufacturer", "value", "description",
    "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "connector_category", "connector_family", "connector_series", "connector_type",
    "positions", "rows", "pitch_mm", "orientation", "termination_type", "gender",
    "polarized", "keying_detail", "locking_mechanism", "shielding", "color",
    "current_rating", "voltage_rating", "signal_type", "flammability_rating",
    "mating_family", "mates_with",
]


def parts():
    for series, s in SERIES.items():
        for n in CIRCUITS:
            mpn = f"{s['prefix']}{n:02d}0"            # 26-60-4020
            catalog = "00" + mpn.replace("-", "")       # 0026604020
            yield {
                **FAMILY,
                "unique_id": f"Molex-{mpn}",
                "part_locator": f"conn-header-{n}pos-3.96mm-1row-th-{s['orientation']}-tin",
                "mpn": mpn, "manufacturer": "Molex", "value": mpn,
                "description": (
                    f"Molex KK 396 {mpn} header, 3.96mm pitch, 1x{n:02d}, "
                    f"{s['orientation']}, friction lock, through-hole, tin plating, "
                    f"{s['tail']}"),
                "datasheet": s["datasheet"],
                "manufacturer_link": f"https://www.molex.com/en-us/products/part-detail/{catalog[2:]}",
                "kicad_symbol": f"Connector_Generic:Conn_01x{n:02d}",
                "kicad_footprint": (
                    f"Connector_Molex:Molex_KK-396_A-{series}-{n:04d}_1x{n:02d}"
                    f"_P3.96mm_{s['fp_style']}"),
                "lifecycle_status": "Active", "rohs": "Yes",
                "allow_substitution": "No", "tracking": "No",
                "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
                "keywords": (
                    f"connector,header,molex,kk396,kk 396,3.96mm,0.156in,friction lock,"
                    f"{s['orientation']},{series},{mpn},{catalog},{series}-{n:04d},"
                    f"power,SWTPC,vintage"),
                "pin_count": str(n), "positions": n, "connector_series": series,
                "orientation": s["orientation"],
            }


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def insert(p):
    vals = ", ".join(sql(p.get(c)) for c in COLS)
    return f"INSERT INTO connectors ({', '.join(COLS)}) VALUES ({vals});"


def main():
    write_symbols([numeric_pins_symbol(n) for n in CIRCUITS])
    rows = with_pins(list(parts()), lambda r: numeric_pins_id(r["positions"]))
    ids = [p["unique_id"] for p in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        sys.exit(f"duplicate unique_id: {dupes}")
    for s in SERIES.values():
        if not (ROOT / s["datasheet"].replace("${TERRA_EDA_LIB}/", "")).exists():
            sys.exit(f"datasheet missing: {s['datasheet']}")
    lines = [
        "-- Terra EDA Library - Molex KK 396 friction-lock headers (41791 vertical, 41792 right-angle)",
        f"-- Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
        *(insert(p) for p in rows),
        "",
        "COMMIT;",
        "",
    ]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} parts")


if __name__ == "__main__":
    main()
