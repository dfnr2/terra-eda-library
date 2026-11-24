#!/usr/bin/env python3
"""Renesas (ex-RCA, Intersil) CA3130 and CA3130A BiMOS op amps.

The CA3130 has a PMOS input stage and a CMOS output, so it swings to both rails and
has picoamp input current. It is in the OSI C2/C3 and C4P parts lists, among others.

Data sheet: datasheets/renesas/ca3130.pdf (FN817 Rev 6.00, Aug 2005). Figures are
the 25 C, V+ = 15 V, V- = 0 V table unless noted:
  - VIO 8/15 mV (CA3130) and 2/5 mV (CA3130A), typ/max at VS = 7.5 V; drift 10 uV/C.
  - II 5/50 pA (CA3130) and 5/30 pA (CA3130A).
  - CMRR 90 dB typ; PSRR 32 uV/V typ.
  - VOM+ 13.3 V at 2 kohm (15 V unloaded), VOM- 2 mV; IOM 22 mA source / 20 mA sink.
  - Supply current 10 mA at VO = 7.5 V, 2 mA at VO = 0 V.
  - Supply 5-16 V (+/-2.5-8 V); abs max 16 V.
  - fT 15 MHz uncompensated, 4 MHz with 47 pF for unity-gain stability; slew rate
    30 V/us open loop, 10 V/us closed loop with 56 pF.
  - Noise 23 uV over 0.2 MHz, RS 1 Mohm. The sheet gives no nV/rtHz figure.
  - Operating range -50 to 125 C, storage -65 to 150 C.

Codes: Renesas's CA3130 and CA3130A pages list the Pb-free CA3130EZ (PDIP),
CA3130MZ and CA3130AMZ (SOIC), plus their 96 reels, as orderable on 2026-11-24.
The leaded E/M codes and the CA3130AE PDIP in the sheet's ordering table are no
longer offered. Reels are left out.

Symbol: stock Amplifier_Operational:CA3130 (offset null 1 and 5, strobe 8), which
matches the sheet's pinout.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_opamp_generated_340_renesas_ca3130.sql")
CREATED_BY = Path(__file__).name
DATASHEET = "${TERRA_EDA_LIB}/datasheets/renesas/ca3130.pdf"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "amplifier_type", "input_type", "channels", "gain_bandwidth", "slew_rate",
    "input_offset", "input_offset_drift", "input_bias_current", "cmrr", "psrr",
    "quiescent_current", "output_current", "rail_to_rail", "positive_rail",
    "negative_rail", "supply_voltage_min", "supply_voltage_max",
    "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max",
]

COMMON = dict(
    manufacturer="Renesas", datasheet=DATASHEET,
    kicad_symbol="Amplifier_Operational:CA3130", lifecycle_status="Active",
    rohs="Yes", allow_substitution="No", tracking="No", created_by=CREATED_BY,
    source=None, dump_priority=0, tier=2, pin_count="8",
    amplifier_type="general-purpose", input_type="MOSFET (PMOS)", channels=1,
    gain_bandwidth="15MHz", slew_rate="30V/µs", input_offset_drift="10µV/°C",
    cmrr="90dB", psrr="32µV/V", quiescent_current="10mA", output_current="22mA",
    rail_to_rail="output", positive_rail="V+ (15V unloaded, 13.3V into 2k)",
    negative_rail="V- (incl. inputs to V- -0.5V)",
    supply_voltage_min=5.0, supply_voltage_max=16.0,
    temp_operating_min=-50.0, temp_operating_max=125.0,
    temp_storage_min=-65.0, temp_storage_max=150.0,
)

PKG = {
    "E": ("pdip-8", "Package_DIP:DIP-8_W7.62mm", "PDIP-8"),
    "M": ("soic-8", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "SOIC-8"),
}

# mpn, value, package code, VIO typ/max, II typ/max
PARTS = [
    ("CA3130EZ", "CA3130", "E", "8mV (15mV max)", "5pA (50pA max)"),
    ("CA3130MZ", "CA3130", "M", "8mV (15mV max)", "5pA (50pA max)"),
    ("CA3130AMZ", "CA3130A", "M", "2mV (5mV max)", "5pA (30pA max)"),
]


def records():
    for mpn, value, code, vio, ii in PARTS:
        package, footprint, pkg_text = PKG[code]
        grade = "a" if value.endswith("A") else ""
        yield dict(
            COMMON, unique_id=f"Renesas-{mpn}", mpn=mpn, value=value, package=package,
            part_locator=f"opamp-bimos-pmos-in-cmos-out-15mhz{('-' + grade) if grade else ''}"
                         f"-{package.replace('-', '')}",
            kicad_footprint=footprint, input_offset=vio, input_bias_current=ii,
            manufacturer_link=f"https://www.renesas.com/en/products/{value.lower()}",
            description=(f"Renesas {value} BiMOS op amp, PMOS input / CMOS output, "
                         f"15MHz fT (4MHz with 47pF for unity gain), 30V/µs, VIO {vio}, "
                         f"II {ii}, output swings to both rails, offset null and "
                         f"strobe, 5-16V supply, {pkg_text}, Pb-free"),
            keywords=",".join(dict.fromkeys(
                ["opamp", "op amp", "single", "BiMOS", "MOSFET input", "CMOS output",
                 "rail-to-rail output", "single-supply", "CA3130", value, mpn, "RCA",
                 "Intersil"])),
        )


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    recs = list(records())
    root = Path(__file__).resolve().parents[3]
    if not (root / DATASHEET.replace("${TERRA_EDA_LIB}/", "")).is_file():
        raise SystemExit(f"missing datasheet {DATASHEET}")
    lines = [
        "-- Terra EDA Library - ic_opamp Renesas CA3130/CA3130A BiMOS op amps",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_opamp ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} parts")


if __name__ == "__main__":
    main()
