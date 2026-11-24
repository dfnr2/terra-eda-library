#!/usr/bin/env python3
"""RS-232 quad line drivers and receivers: MC1488/SN75188 and MC1489/MC1489A/SN75189/A.

The classic pair behind the serial ports of 1970s-80s computers (OSI C2/C3, C4P and
others). TI documents both generations in one sheet each:
  - SLLS094C (May 2004), MC1488, SN55188, SN75188 (datasheets/ti/mc1488-sn75188.pdf):
    VCC+ 7.5-15 V and VCC- -7.5 to -15 V (nominal +/-9 V), VIH 1.9 V, VIL 0.8 V,
    VOH 7 V typ / VOL -7 V typ at +/-9 V into 3 kohm, IOS 6-12 mA, power-off output
    resistance 300 ohm, tPLH 220/350 ns, tPHL 100/175 ns (typ/max), 0-70 C,
    Tstg -65 to 150 C. Driver 1 is an inverter; drivers 2-4 are 2-input NANDs.
  - SLLS095D (Oct 1998), MC1489/A, SN55189/A, SN75189/A
    (datasheets/ti/mc1489-sn75189.pdf): VCC 4.5-5.5 V, inputs +/-25 V (abs +/-30 V),
    VIT+ 1.0-1.5 V ('89) or 1.75-2.25 V ('89A), VIT- 0.75-1.25 V, VOH 2.6 V min,
    VOL 0.45 V at 10 mA, ICC 20/26 mA, tPLH 25/85 ns, tPHL 25/50 ns, 0-70 C.

Ordering codes and lifecycle from each sheet's package-option addendum (2026-11-24):
the MC1488N, MC1489N and MC1489AN are Obsolete; the SN75188/SN75189/SN75189A PDIP
and SOIC codes are Active. The SN75188D SOIC tube is Obsolete, so its
reel (DR) is used. The SN75188/SN75189A are TI's drop-in replacements for the MC
parts, but the MC rows are kept for restorations, as plans/vintage-computer-parts.md
decides.

Symbols: KiCad has none, so terra_symbols_ic_drivers:MC1488 and :MC1489 are drawn
from db/tables/ic_drivers/_pinouts.py with tools/make_dip_symbol.py. All four MC/SN
pairs share their pinout in every 14-pin package.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_drivers_generated_330_rs232_1488_1489.sql")
CREATED_BY = Path(__file__).name

DS_DRV = "${TERRA_EDA_LIB}/datasheets/ti/mc1488-sn75188.pdf"
DS_RCV = "${TERRA_EDA_LIB}/datasheets/ti/mc1489-sn75189.pdf"

PKG = {
    "N": ("pdip-14", "Package_DIP:DIP-14_W7.62mm"),
    "D": ("soic-14", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"),
}

DRIVER = dict(
    sym="terra_symbols_ic_drivers:MC1488", ds=DS_DRV, vmin=7.5, vmax=15.0,
    kind="driver", output_type="push-pull, current-limited",
    spec=("4 channels (1 inverter + 3 2-input NAND), +/-7.5 to 15V supplies, "
          "TTL inputs, VOH/VOL +/-7V typ into 3k at +/-9V, IOS 6-12mA, "
          "power-off ro 300 ohm, tPLH 350ns / tPHL 175ns max"))
RCV = dict(
    sym="terra_symbols_ic_drivers:MC1489", ds=DS_RCV, vmin=4.5, vmax=5.5,
    kind="receiver", output_type="totem-pole with pull-up",
    spec=("4 channels, 5V supply, +/-25V inputs, 3-7k input resistance, "
          "{thr}, VIT- 0.75-1.25V, response-control pins, VOL 0.45V @ 10mA, "
          "tPLH 85ns / tPHL 50ns max"))
THR_89 = "VIT+ 1.0-1.5V (MC1489 thresholds)"
THR_89A = "VIT+ 1.75-2.25V (MC1489A thresholds, wider hysteresis)"

# mpn, value (base), family, package code, status, threshold (receivers)
PARTS = [
    ("MC1488N", "MC1488", DRIVER, "N", "Obsolete", None),
    ("SN75188N", "SN75188", DRIVER, "N", "Active", None),
    ("SN75188DR", "SN75188", DRIVER, "D", "Active", None),
    ("MC1489N", "MC1489", RCV, "N", "Obsolete", THR_89),
    ("MC1489AN", "MC1489A", RCV, "N", "Obsolete", THR_89A),
    ("SN75189N", "SN75189", RCV, "N", "Active", THR_89),
    ("SN75189D", "SN75189", RCV, "D", "Active", THR_89),
    ("SN75189AN", "SN75189A", RCV, "N", "Active", THR_89A),
    ("SN75189AD", "SN75189A", RCV, "D", "Active", THR_89A),
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking", "created_by",
    "source", "dump_priority", "tier", "keywords", "pin_count", "temp_operating_min",
    "temp_operating_max", "temp_storage_min", "temp_storage_max", "driver_type",
    "channels", "supply_voltage_min", "supply_voltage_max", "output_type",
]


def records():
    for mpn, base, fam, code, status, thr in PARTS:
        package, footprint = PKG[code]
        kind = fam["kind"]
        spec = fam["spec"].format(thr=thr) if thr else fam["spec"]
        locator = (f"rs232-quad-{kind}-{'89a' if thr == THR_89A else '89' if thr else '88'}"
                   f"-{package.replace('-', '')}")
        pkg_text = "SOIC-14 reel" if mpn.endswith("DR") else package.upper()
        compat = {"MC1488": "SN75188", "SN75188": "MC1488", "MC1489": "SN75189",
                  "SN75189": "MC1489", "MC1489A": "SN75189A", "SN75189A": "MC1489A"}[base]
        yield {
            "unique_id": f"TI-{mpn}", "part_locator": locator, "mpn": mpn,
            "manufacturer": "TI", "package": package, "value": base,
            "description": (f"TI {base} quadruple RS-232 (TIA-232/V.28) line {kind}, "
                            f"{spec}, 0-70C, {pkg_text}"),
            "datasheet": fam["ds"],
            "manufacturer_link": f"https://www.ti.com/product/{base}",
            "kicad_symbol": fam["sym"], "kicad_footprint": footprint,
            "lifecycle_status": status, "rohs": "Yes" if status == "Active" else "No",
            "allow_substitution": "Yes", "tracking": "No", "created_by": CREATED_BY,
            "source": None, "dump_priority": 0, "tier": 2,
            "keywords": ",".join(dict.fromkeys(
                ["RS-232", "EIA-232", "V.28", f"line {kind}", "quad", base, compat, mpn])),
            "pin_count": "14",
            "temp_operating_min": 0.0, "temp_operating_max": 70.0,
            "temp_storage_min": -65.0, "temp_storage_max": 150.0,
            "driver_type": "interface ic", "channels": 4,
            "supply_voltage_min": fam["vmin"], "supply_voltage_max": fam["vmax"],
            "output_type": fam["output_type"],
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
    root = Path(__file__).resolve().parents[3]
    for ds in {DS_DRV, DS_RCV}:
        if not (root / ds.replace("${TERRA_EDA_LIB}/", "")).is_file():
            raise SystemExit(f"missing datasheet {ds}")
    lines = [
        "-- Terra EDA Library - ic_drivers RS-232 MC1488/MC1489 line drivers and receivers",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
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
