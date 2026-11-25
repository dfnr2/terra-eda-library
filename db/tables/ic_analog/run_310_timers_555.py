#!/usr/bin/env python3
"""555/556-family RC timers: TI bipolar and CMOS parts and the Renesas ICM7555/7556.

Each device has a BASE spec block, transcribed from its data sheet, and a list of
ordering codes (VARIANTS). PDIP is the primary row; the SOIC twin is added when the
same data sheet lists it as orderable, following the ic_logic N/D convention. Where
TI has obsoleted the SOIC tube (NE555D, SA555D, NE556D, TLC555CD/ID, LMC555CM), the
reel code is used instead, as ic_logic does for SN7404DR.

Data sheets (datasheets/ti/ and datasheets/renesas/):
  - ne555.pdf     SLFS022K, Mar 2026: NE555/SA555/SE555. VCC 4.5-16 V (SE555 to 18 V),
                  output +/-200 mA, ICC 3 mA typ at 5 V / 10 mA at 15 V (output low),
                  "use at maximum frequency of 100kHz or below" (astable).
  - ne556.pdf     SLFS023I, Mar 2025: NE556/SA556. Same ratings, ICC 6 mA typ at 5 V.
  - tlc555.pdf    SLFS043K, Jan 2026: VDD 2-15 V (C), 3-15 V (I); sink 100 mA / source
                  10 mA typ; IDD 180 uA typ at 5 V; fmax 2.1 MHz typ.
  - tlc556.pdf    SLFS047D, Mar 2026: VDD 2-15 V; same outputs; IDD 360 uA typ at 5 V
                  (both timers); fmax 2.1 MHz typ.
  - lmc555.pdf    SNAS558O, Nov 2026: specified from 1.5 V; the sheet gives no recommended
                  maximum, so 15 V is the absolute maximum (tables run to 12 V). IS 180 uA
                  typ at 5 V; fMAX 2.4 MHz typ (the rev O change from 3 MHz); tested to
                  -10 mA / 50 mA output.
  - lm555.pdf     SNAS548D, Jan 2015: VCC 4.5-16 V (electrical table; ROC lists 18 V max),
                  source or sink 200 mA, ICC 3 mA typ at 5 V. No maximum frequency stated.
  - icm7555-icm7556.pdf  Renesas FN2867 Rev 10.01, Mar 2020: VDD 2-18 V; IDD 40 uA
                  (ICM7555) / 80 uA (ICM7556) typ at 5 V; fMAX 1 MHz typ; VOL 0.4 V at
                  20 mA sink, VOH 14.3 V min at 0.8 mA source (15 V).

Lifecycle (2026-11-25): TI ordering-code status from the ti.com product pages'
orderable-part data (the same status the data sheets' package addenda print); Renesas
part-detail pages (ICM7555IPAZ/IBAZ Active, ICM7556IPDZ Obsolete, which Digi-Key and
Octopart also show). Mouser and Digi-Key refuse scripted fetches.

Symbols: stock KiCad Timer library, one per device and package. The TLC556 has no stock
symbol; its pinout matches the NE556 pin for pin (TLC556 data sheet table 4-1), so it
uses Timer:NE556.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_analog_generated_310_timers_555.sql")
CREATED_BY = Path(__file__).name
TABLE = "ic_analog"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking", "created_by",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "function_type", "channels", "resolution_bits", "interface",
    "supply_voltage_min", "supply_voltage_max",
]

DEFAULTS = dict(
    rohs="Yes", allow_substitution="No", tracking="No", created_by=CREATED_BY,
    source=None, dump_priority=0, tier=2, function_type="timer",
    resolution_bits=None, interface=None,
)

TI = "Texas Instruments"
RENESAS = "Renesas"
DS = "${TERRA_EDA_LIB}/datasheets/"

# package -> (footprint, pin_count)
PKG = {
    "PDIP-8": ("Package_DIP:DIP-8_W7.62mm", "8"),
    "SOIC-8": ("Package_SO:SOIC-8_3.9x4.9mm_P1.27mm", "8"),
    "PDIP-14": ("Package_DIP:DIP-14_W7.62mm", "14"),
    "SOIC-14": ("Package_SO:SOIC-14_3.9x8.7mm_P1.27mm", "14"),
}

BIPOLAR_555 = ("bipolar 555 timer, astable or monostable, output sinks or sources "
               "200mA, up to 100kHz astable, 3mA typ supply at 5V")
BIPOLAR_556 = ("dual bipolar 555 timer, astable or monostable, outputs sink or source "
               "200mA, up to 100kHz astable, 6mA typ supply at 5V (both timers)")
BIPOLAR_KW = ["555", "timer", "bipolar", "astable", "monostable", "oscillator",
              "pulse generator", "one-shot"]
CMOS_KW = ["555", "timer", "CMOS", "low power", "astable", "monostable", "oscillator",
           "pulse generator", "one-shot"]

# value -> base spec; temps are per grade, so they live on the variant.
BASE = {
    "NE555": dict(
        manufacturer=TI, ds="ti/ne555.pdf", link="https://www.ti.com/product/NE555",
        tech="bipolar", channels=1, vmin=4.5, vmax=16.0, text=BIPOLAR_555,
        kw=BIPOLAR_KW + ["NE555"]),
    "SA555": dict(
        manufacturer=TI, ds="ti/ne555.pdf", link="https://www.ti.com/product/SA555",
        tech="bipolar", channels=1, vmin=4.5, vmax=16.0, text=BIPOLAR_555,
        kw=BIPOLAR_KW + ["SA555", "NE555", "industrial"]),
    "SE555": dict(
        manufacturer=TI, ds="ti/ne555.pdf", link="https://www.ti.com/product/SE555",
        tech="bipolar", channels=1, vmin=4.5, vmax=18.0, text=BIPOLAR_555,
        kw=BIPOLAR_KW + ["SE555", "NE555", "military temperature"]),
    "LM555": dict(
        manufacturer=TI, ds="ti/lm555.pdf", link="https://www.ti.com/product/LM555",
        tech="bipolar", channels=1, vmin=4.5, vmax=16.0,
        text=("bipolar 555 timer, astable or monostable, output sinks or sources "
              "200mA, 3mA typ supply at 5V, direct replacement for NE555/SE555"),
        kw=BIPOLAR_KW + ["LM555", "NE555"]),
    "NE556": dict(
        manufacturer=TI, ds="ti/ne556.pdf", link="https://www.ti.com/product/NE556",
        tech="bipolar", channels=2, vmin=4.5, vmax=16.0, text=BIPOLAR_556,
        kw=BIPOLAR_KW + ["556", "dual", "NE556"]),
    "SA556": dict(
        manufacturer=TI, ds="ti/ne556.pdf", link="https://www.ti.com/product/SA556",
        tech="bipolar", channels=2, vmin=4.5, vmax=16.0, text=BIPOLAR_556,
        kw=BIPOLAR_KW + ["556", "dual", "SA556", "NE556", "industrial"]),
    "TLC555": dict(
        manufacturer=TI, ds="ti/tlc555.pdf", link="https://www.ti.com/product/TLC555",
        tech="cmos", channels=1, vmin=None, vmax=15.0,  # vmin per grade
        text=("CMOS 555 timer, NE555 pin-compatible, rail-to-rail output sinks 100mA / "
              "sources 10mA typ, up to 2.1MHz astable, 180µA typ supply at 5V"),
        kw=CMOS_KW + ["TLC555", "NE555 replacement"]),
    "TLC556": dict(
        manufacturer=TI, ds="ti/tlc556.pdf", link="https://www.ti.com/product/TLC556",
        tech="cmos", channels=2, vmin=2.0, vmax=15.0,
        text=("dual CMOS 555 timer, NE556 pin-compatible, rail-to-rail outputs sink "
              "100mA / source 10mA typ, up to 2.1MHz astable, 360µA typ supply at 5V "
              "(both timers)"),
        kw=CMOS_KW + ["556", "dual", "TLC556", "NE556 replacement"]),
    "LMC555": dict(
        manufacturer=TI, ds="ti/lmc555.pdf", link="https://www.ti.com/product/LMC555",
        tech="cmos", channels=1, vmin=1.5, vmax=15.0,
        text=("CMOS 555 timer, 555 pin-compatible, specified from 1.5V (supply max "
              "is the 15V absolute maximum), up to 2.4MHz astable, 180µA typ supply "
              "at 5V, output tested to -10mA / 50mA"),
        kw=CMOS_KW + ["LMC555", "NE555 replacement", "1.5V"]),
    "ICM7555": dict(
        manufacturer=RENESAS, ds="renesas/icm7555-icm7556.pdf",
        link="https://www.renesas.com/en/products/icm7555",
        tech="cmos", channels=1, vmin=2.0, vmax=18.0,
        text=("CMOS 555 timer, NE555 pin-compatible, up to 1MHz astable, "
              "40µA typ supply at 5V, CONT needs no decoupling, no supply crowbarring"),
        kw=CMOS_KW + ["ICM7555", "7555", "Intersil", "NE555 replacement"]),
    "ICM7556": dict(
        manufacturer=RENESAS, ds="renesas/icm7555-icm7556.pdf",
        link="https://www.renesas.com/en/products/icm7556",
        tech="cmos", channels=2, vmin=2.0, vmax=18.0,
        text=("dual CMOS 555 timer, NE556 pin-compatible, up to 1MHz astable, "
              "80µA typ supply at 5V (both timers), CONT needs no decoupling"),
        kw=CMOS_KW + ["556", "dual", "ICM7556", "7556", "Intersil", "NE556 replacement"]),
}

# value -> [(mpn, package, kicad_symbol, temp_min, temp_max, lifecycle, vmin override)]
VARIANTS = {
    "NE555": [
        ("NE555P", "PDIP-8", "Timer:NE555P", 0, 70, "Active", None),
        ("NE555DR", "SOIC-8", "Timer:NE555D", 0, 70, "Active", None),
    ],
    "SA555": [
        ("SA555P", "PDIP-8", "Timer:SA555P", -40, 85, "Active", None),
        ("SA555DR", "SOIC-8", "Timer:SA555D", -40, 85, "Active", None),
    ],
    "SE555": [
        ("SE555P", "PDIP-8", "Timer:SE555P", -55, 125, "Active", None),
        ("SE555DR", "SOIC-8", "Timer:SE555D", -55, 125, "Active", None),
    ],
    "LM555": [
        ("LM555CN/NOPB", "PDIP-8", "Timer:LM555xN", 0, 70, "Active", None),
        ("LM555CM/NOPB", "SOIC-8", "Timer:LM555xM", 0, 70, "Active", None),
    ],
    "NE556": [
        ("NE556N", "PDIP-14", "Timer:NE556", 0, 70, "Active", None),
        ("NE556DR", "SOIC-14", "Timer:NE556", 0, 70, "Active", None),
    ],
    "SA556": [
        ("SA556N", "PDIP-14", "Timer:SA556", -40, 85, "Active", None),
    ],
    "TLC555": [
        ("TLC555CP", "PDIP-8", "Timer:TLC555xP", 0, 70, "Active", 2.0),
        ("TLC555CDR", "SOIC-8", "Timer:TLC555xD", 0, 70, "Active", 2.0),
        ("TLC555IP", "PDIP-8", "Timer:TLC555xP", -40, 85, "Active", 3.0),
        ("TLC555IDR", "SOIC-8", "Timer:TLC555xD", -40, 85, "Active", 3.0),
    ],
    "TLC556": [
        ("TLC556CN", "PDIP-14", "Timer:NE556", 0, 70, "Active", None),
        ("TLC556CD", "SOIC-14", "Timer:NE556", 0, 70, "Active", None),
        ("TLC556IN", "PDIP-14", "Timer:NE556", -40, 85, "Active", None),
        ("TLC556ID", "SOIC-14", "Timer:NE556", -40, 85, "Active", None),
    ],
    "LMC555": [
        ("LMC555CN/NOPB", "PDIP-8", "Timer:LMC555xN", -40, 85, "Active", None),
        ("LMC555CMX/NOPB", "SOIC-8", "Timer:LMC555xM", -40, 85, "Active", None),
    ],
    "ICM7555": [
        ("ICM7555IPAZ", "PDIP-8", "Timer:ICM7555xP", -25, 85, "Active", None),
        ("ICM7555IBAZ", "SOIC-8", "Timer:ICM7555xB", -25, 85, "Active", None),
    ],
    "ICM7556": [
        ("ICM7556IPDZ", "PDIP-14", "Timer:ICM7556", -25, 85, "Obsolete", None),
    ],
}


def fmt_temp(t):
    return f"+{t}" if t > 0 else str(t)


def records():
    for value, base in BASE.items():
        mfr = base["manufacturer"]
        uid_prefix = mfr.replace(" ", "_")
        for mpn, package, ksym, tmin, tmax, life, vmin_override in VARIANTS[value]:
            footprint, pin_count = PKG[package]
            vmin = vmin_override if vmin_override is not None else base["vmin"]
            vmax = base["vmax"]
            pkgtoken = package.lower().replace("-", "")
            kind = "556" if base["channels"] == 2 else "555"
            note = ", reel" if mpn.endswith(("DR", "MX/NOPB")) else ""
            yield dict(
                DEFAULTS,
                unique_id=f"{uid_prefix}-{mpn}",
                part_locator=f"timer-{kind}-{base['tech']}-{pkgtoken}",
                mpn=mpn, manufacturer=mfr, package=package, value=value,
                description=(f"{mfr} {value} {base['text']}, {vmin:g}-{vmax:g}V, "
                             f"{fmt_temp(tmin)} to {fmt_temp(tmax)}°C, {package}{note}"),
                datasheet=DS + base["ds"], manufacturer_link=base["link"],
                kicad_symbol=ksym, kicad_footprint=footprint, lifecycle_status=life,
                keywords=",".join(dict.fromkeys(base["kw"] + [mpn])),
                pin_count=pin_count, temp_operating_min=float(tmin),
                temp_operating_max=float(tmax), channels=base["channels"],
                supply_voltage_min=vmin, supply_voltage_max=vmax,
            )


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    root = Path(__file__).resolve().parents[3]
    recs = list(records())
    seen = set()
    for r in recs:
        if r["unique_id"] in seen:
            raise SystemExit(f"duplicate unique_id: {r['unique_id']}")
        seen.add(r["unique_id"])
        path = root / r["datasheet"].replace("${TERRA_EDA_LIB}/", "")
        if not path.is_file():
            raise SystemExit(f"missing datasheet {r['datasheet']}")
    lines = [
        "-- Terra EDA Library - ic_analog 555/556-family timers (TI, Renesas)",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO {TABLE} ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} rows across {len(BASE)} devices")


if __name__ == "__main__":
    main()
