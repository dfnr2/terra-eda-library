#!/usr/bin/env python3
"""4-bit I2C/SMBus GPIO expanders: NXP PCA9536DP and TI TCA9536DGKR.

Both share the industry 9536 pinout (IO0-IO2, VSS, IO3, SCL, SDA, VDD) and the fixed
address 0x41, so they are drop-in alternatives on a TSSOP/VSSOP-8 3x3 mm land.

  PCA9536DP    PCA9536 data sheet Rev. 6 (7 Nov 2017), datasheets/nxp/pca9536.pdf
               2.3-5.5 V, 400 kHz, 100 k pull-ups always on, -40..85 C.
               Stock Interface_Expansion:PCA9536DP symbol.
  TCA9536DGKR  SCPS275A (Dec 2021), datasheets/ti/tca9536.pdf
               1.65-5.5 V, 1 MHz Fm+, software-switchable pull-ups, P3 can be
               repurposed as an open-drain INT output, -40..125 C.
               terra TCA9536DGK symbol (stock PCA9536DP layout, TI pin names incl. P3/INT).

Only the TSSOP/VSSOP parts are emitted. The PCA9536D (SO8) was fully withdrawn by NXP
DN 202507021 (LTB 13 Apr 2026). PCA9536TK (HVSON8) and TCA9536DTMR (X2SON-8) are left out
for now.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_drivers_generated_320_i2c_io_expanders.sql")

PARTS = [
    {
        "mpn": "PCA9536DP", "manufacturer": "NXP", "base": "PCA9536",
        "package": "tssop-8", "pin_count": "8",
        "kicad_symbol": "Interface_Expansion:PCA9536DP",
        "kicad_footprint": "Package_SO:TSSOP-8_3x3mm_P0.65mm",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/nxp/pca9536.pdf",
        "manufacturer_link": "https://www.nxp.com/part/PCA9536DP",
        "data_rate": "400 kHz", "supply_voltage_min": 2.3, "supply_voltage_max": 5.5,
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -65, "temp_storage_max": 150,
        # Limiting values: 50 mA per IOn, 100 mA through VSS (no recommended IOL is given).
        "i_max_channel": "50 mA", "i_max_device": "100 mA",
        "output_type": "push-pull",
        "features": "400 kHz, 100k pull-ups",
    },
    {
        "mpn": "TCA9536DGKR", "manufacturer": "Texas Instruments", "base": "TCA9536",
        "package": "vssop-8", "pin_count": "8",
        "kicad_symbol": "terra_symbols_ic_drivers:TCA9536DGK",
        "kicad_footprint": "Package_SO:VSSOP-8_3x3mm_P0.65mm",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/ti/tca9536.pdf",
        "manufacturer_link": "https://www.ti.com/product/TCA9536",
        "data_rate": "1 MHz", "supply_voltage_min": 1.65, "supply_voltage_max": 5.5,
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150,
        # Recommended operating: IOL 25 mA (VCC > 1.8 V), IOH -10 mA; 160 mA through VCC.
        "i_max_channel": "25 mA", "i_max_device": "160 mA",
        "output_type": "push-pull",
        "features": "1 MHz Fm+, switchable pull-ups, P3 as INT",
    },
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max",
    "driver_type", "channels", "data_rate", "supply_voltage_min", "supply_voltage_max",
    "i_max_device", "i_max_channel", "output_type",
]

COPY = [
    "mpn", "manufacturer", "package", "pin_count", "kicad_symbol", "kicad_footprint",
    "datasheet", "manufacturer_link", "data_rate", "supply_voltage_min",
    "supply_voltage_max", "temp_operating_min", "temp_operating_max",
    "temp_storage_min", "temp_storage_max", "i_max_channel", "i_max_device",
    "output_type",
]


def records():
    for p in PARTS:
        rec = {k: p[k] for k in COPY}
        rec.update({
            "unique_id": f"{p['manufacturer']}-{p['mpn']}",
            "part_locator": f"io-expander-i2c-4bit-0x41-{p['package'].replace('-', '')}",
            "value": p["base"],
            "description": (
                f"{p['manufacturer']} {p['base']} 4-bit I2C/SMBus GPIO expander, "
                f"fixed address 0x41, {p['features']}, "
                f"{p['supply_voltage_min']:g}-{p['supply_voltage_max']:g}V, "
                f"{p['package'].upper()}"
            ),
            "lifecycle_status": "Active", "rohs": "Yes",
            "allow_substitution": "Yes", "tracking": "No",
            "source": None, "dump_priority": 0, "tier": 2,
            "keywords": f"I2C, SMBus, GPIO, I/O expander, port expander, 9536, {p['base']}",
            "driver_type": "io expander", "channels": 4,
        })
        yield rec


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    recs = list(records())
    ids = [r["unique_id"] for r in recs]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"duplicate unique_id: {dupes}")
    lines = [
        "-- Terra EDA Library - ic_drivers 4-bit I2C GPIO expanders (9536)",
        f"-- Generated by {Path(__file__).name}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_drivers ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} parts")


if __name__ == "__main__":
    main()
