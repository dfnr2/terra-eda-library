#!/usr/bin/env python3
"""3.3 V "348x" RS-485/RS-422 transceivers: ADI ADM348x, ADM348xE and Renesas ISL8348x.

Every family shares the industry pinouts, so symbols are picked by configuration:

  half duplex, 8-lead   RO ~RE DE DI GND A B VCC        Interface_UART:ADM3485xR
  full duplex, 8-lead   VCC RO DI GND Y Z B A           terra MAX3488E symbol (+ flipped)
  full duplex, 14-lead  NC RO ~RE DE DI GND GND NC Y Z B A VCC VCC
                                                        Interface_UART:ADM3491ExR

The full-duplex 8-lead parts reuse the MAX3488E symbol and footprint, so they get the
same "-flipped" variant. ISL83490IBZ is already in run_300_terra_sym_harvest.py and
keeps its unique_id there.

Only the Pb-free base MPNs from each ordering guide are emitted. Reels (-REEL7,
-T, -T7A), the leaded ADM3485EAR / ADM3491AR and the discontinued PDIPs are left
out. The non-E family has no ADM3486.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_drivers_generated_310_rs485_348x.sql")

DS_ADM_E = "${TERRA_EDA_LIB}/datasheets/analog-devices/adm3483e-adm3491e.pdf"
DS_ADM3485E = "${TERRA_EDA_LIB}/datasheets/analog-devices/adm3485e.pdf"
DS_ADM = "${TERRA_EDA_LIB}/datasheets/analog-devices/adm3483-adm3491.pdf"
DS_ISL = "${TERRA_EDA_LIB}/datasheets/renesas/isl83483-isl83491.pdf"

MAX3488E_SYM = "terra_symbols_ic_drivers:IC_DRIVER MAX3488E RS422 Tranceiver full duplex 3.3V 15kv ESD soic-8"
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
SOIC14 = "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"

# config -> (pin_count, symbol, footprint, package)
CONFIG = {
    "half": ("8", "Interface_UART:ADM3485xR", SOIC8, "soic-8"),
    "full": ("8", MAX3488E_SYM, SOIC8, "soic-8"),
    "full-en": ("14", "Interface_UART:ADM3491ExR", SOIC14, "soic-14"),
}

# Storage range differs by datasheet; operating is -40..85 C for every part.
STORAGE = {DS_ADM_E: (-65, 150), DS_ADM3485E: (-65, 150), DS_ADM: (-65, 125), DS_ISL: (-65, 150)}

# mpn, manufacturer, base part, config, data rate, slew limited, ±15 kV ESD, datasheet
# Data rates are each datasheet's headline guaranteed rate (feature list / Table 1).
PARTS = [
    # ADM3483E/ADM3486E/ADM3488E/ADM3490E/ADM3491E, Rev. A
    ("ADM3483EARZ", "Analog Devices", "ADM3483E", "half", "250 kbps", True, True, DS_ADM_E),
    ("ADM3486EARZ", "Analog Devices", "ADM3486E", "half", "2.5 Mbps", True, True, DS_ADM_E),
    ("ADM3488EARZ", "Analog Devices", "ADM3488E", "full", "250 kbps", True, True, DS_ADM_E),
    ("ADM3490EARZ", "Analog Devices", "ADM3490E", "full", "12 Mbps", False, True, DS_ADM_E),
    ("ADM3491EARZ", "Analog Devices", "ADM3491E", "full-en", "12 Mbps", False, True, DS_ADM_E),
    # ADM3485E, Rev. D
    ("ADM3485EARZ", "Analog Devices", "ADM3485E", "half", "12 Mbps", False, True, DS_ADM3485E),
    # ADM3483/ADM3485/ADM3488/ADM3490/ADM3491, Rev. E
    ("ADM3483ARZ", "Analog Devices", "ADM3483", "half", "250 kbps", True, False, DS_ADM),
    ("ADM3485ARZ", "Analog Devices", "ADM3485", "half", "10 Mbps", False, False, DS_ADM),
    ("ADM3488ARZ", "Analog Devices", "ADM3488", "full", "250 kbps", True, False, DS_ADM),
    ("ADM3490ARZ", "Analog Devices", "ADM3490", "full", "10 Mbps", False, False, DS_ADM),
    ("ADM3491ARZ", "Analog Devices", "ADM3491", "full-en", "10 Mbps", False, False, DS_ADM),
    # ISL83483/ISL83485/ISL83488/ISL83490/ISL83491, FN6052 Rev. 5.00
    ("ISL83483IBZ", "Renesas", "ISL83483", "half", "250 kbps", True, False, DS_ISL),
    ("ISL83485IBZ", "Renesas", "ISL83485", "half", "10 Mbps", False, False, DS_ISL),
    ("ISL83488IBZ", "Renesas", "ISL83488", "full", "250 kbps", True, False, DS_ISL),
    ("ISL83491IBZ", "Renesas", "ISL83491", "full-en", "10 Mbps", False, False, DS_ISL),
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "variant", "package",
    "value", "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking", "source",
    "dump_priority", "tier", "keywords", "pin_count", "temp_operating_min",
    "temp_operating_max", "temp_storage_min", "temp_storage_max", "driver_type",
    "channels", "data_rate", "supply_voltage_min", "supply_voltage_max",
]

DUPLEX = {"half": "half-duplex", "full": "full-duplex", "full-en": "full-duplex"}


def link(manufacturer, base):
    if manufacturer == "Renesas":
        return f"https://www.renesas.com/en/products/{base.lower()}"
    return f"https://www.analog.com/en/products/{base.lower()}.html"


def records():
    for mpn, mfr, base, config, rate, slew, esd, ds in PARTS:
        pins, symbol, footprint, package = CONFIG[config]
        rate_slug = rate.replace(" ", "").lower()
        features = [rate]
        if slew:
            features.append("slew-rate limited")
        if config != "full":
            features.append("driver/receiver enable")
        if esd:
            features.append("±15 kV ESD")
        rec = {
            "unique_id": f"{mfr}-{mpn}",
            "part_locator": f"rs485-{config}-{rate_slug}-3v3{'-esd' if esd else ''}-{package.replace('-', '')}",
            "mpn": mpn, "manufacturer": mfr, "package": package, "value": base,
            "description": (
                f"{mfr} {base} 3.3V {DUPLEX[config]} RS-485/RS-422 transceiver, "
                f"{', '.join(features)}, {package.upper()}"
            ),
            "datasheet": ds, "manufacturer_link": link(mfr, base),
            "kicad_symbol": symbol, "kicad_footprint": footprint,
            "rohs": "Yes", "allow_substitution": "Yes", "tracking": "No",
            "source": None, "dump_priority": 0, "tier": 2,
            "keywords": ", ".join(
                ["RS-485", "RS-422", "transceiver", DUPLEX[config], "3.3V"]
                + (["ESD"] if esd else [])
            ),
            "pin_count": pins,
            "temp_operating_min": -40, "temp_operating_max": 85,
            "temp_storage_min": STORAGE[ds][0], "temp_storage_max": STORAGE[ds][1],
            "driver_type": "interface ic", "channels": 1, "data_rate": rate,
            "supply_voltage_min": 3.0, "supply_voltage_max": 3.6,
        }
        yield rec
        if config == "full":
            yield {
                **rec,
                "unique_id": f"{rec['unique_id']}-flipped", "variant": "flipped",
                "part_locator": f"{rec['part_locator']}-flipped",
                "kicad_symbol": f"{MAX3488E_SYM} flipped",
            }


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
        "-- Terra EDA Library - ic_drivers 3.3V 348x RS-485/RS-422 transceivers",
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
