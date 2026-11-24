#!/usr/bin/env python3
"""Standard (bipolar, no-letter) 7400-series TTL from TI: the plain SN74xx parts.

These are not the 74LS parts with a different name. Speed, input loading, output drive
and supply current all differ, and in timing circuits the difference shows: an SN74123
gives tw = 0.28 * RT * Cext * (1 + 0.7/RT), while an SN74LS123 gives about 0.45 * RT * Cext
with a 5-260 kohm Rext range instead of 5-50 kohm. A 7404 crystal oscillator biased for
standard TTL input current won't run the same on a 74LS04. So each part gets its own row,
value "7404" (not "74LS04"), data-sheet timing, and allow_substitution = 'No'.

Parts: what the OSI 470 board uses (7404, 7407, 7417, 7410, 7430, 7493A, 74123, 74390)
plus 7400, 7402 and 7454, which run_320_ttl_harvest.py used to emit from KiCad's only
three standard-TTL symbols. That harvest invented an SOIC row for each; here a package
gets a row only if TI's package-option addendum (in each data sheet, 2026 printing)
lists it:
  - Active: SN7400N/D, SN7402N, SN7404N/DR, SN7407N/DR, SN7417N/DR, SN74123N. The
    SOIC tube codes SN7404D/SN7407D/SN7417D are Obsolete there, so the reel code is used.
  - Gone from the addendum and from TI's product pages (404), Mouser lists them as
    obsolete or not at all (2026-11-24): SN7410N, SN7430N, SN7454N, SN7493AN, SN74390N.
    They are kept as Obsolete PDIP rows for restorations, which buy NOS/surplus.

Symbols: KiCad's 74xx library has standard-TTL symbols only for 7400, 7402 and 7454;
the rest use the 74LS symbol of the same pinout (the 7493A keeps the 74LS93's odd
VCC = 5 / GND = 10). 74xx_IEEE symbols are added as variant 'IEEE' rows where one exists.

Data sheets (datasheets/ti/, TI's file names; several cover the LS part too):
  sn7400.pdf, sn7402.pdf, sn7404.pdf (SDLS029C), sn7407.pdf (7407 and 7417),
  sn74123.pdf (SDLS043), sn74ls10.pdf (SDLS035A), sn74ls30.pdf (SDLS099),
  sn54ls54.pdf (SDLS115), sn74ls90.pdf (SDLS940A, '93A columns),
  sn74ls390.pdf (SDLS107).
Switching figures are at VCC = 5 V, TA = 25 C, RL = 400 ohm, CL = 15 pF unless noted.
Plan: plans/ic-logic-standard-ttl.md.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "ic_logic_generated_315_ttl_standard.sql"
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets/ti"

COLS = [
    "unique_id", "variant", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "standards_version", "source", "dump_priority", "tier", "lifecycle_status",
    "created_by", "keywords",
    "pin_count", "temp_operating_min", "temp_operating_max",
    "logic_family", "base_number", "gate_function", "function_category",
    "channels", "inputs_per_gate", "bit_width", "logic_polarity", "output_type",
    "schmitt_trigger", "supply_voltage_min", "supply_voltage_max",
    "vih_min", "vil_max", "voh_min", "vol_max", "propagation_delay",
    "max_frequency", "output_current", "supply_current",
]

# Standard-TTL recommended operating conditions (SN74 columns, every sheet here).
FAMILY = dict(
    manufacturer="Texas Instruments", logic_family="74", tracking="No",
    allow_substitution="No", standards_version="1.0", source=None, dump_priority=0,
    tier=2, created_by=CREATED_BY, temp_operating_min=0, temp_operating_max=70,
    schmitt_trigger="no", supply_voltage_min=4.75, supply_voltage_max=5.25,
    vih_min=2.0, vil_max=0.8, voh_min=2.4, vol_max=0.4, output_type="totem-pole",
    output_current="IOL 16mA / IOH -0.4mA",
)

FOOTPRINT = {
    ("PDIP", 14): "Package_DIP:DIP-14_W7.62mm",
    ("PDIP", 16): "Package_DIP:DIP-16_W7.62mm",
    ("SOIC", 14): "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
}
PKG_OF = {"N": "PDIP", "D": "SOIC", "DR": "SOIC"}


def tpd(*paths):
    """('A->Y', tplh_typ, tplh_max, tphl_typ, tphl_max) -> data-sheet text."""
    out = []
    for name, lt, lm, ht, hm in paths:
        pre = f"{name} " if name else ""
        if lt is None:
            out.append(f"{pre}tPHL {ht}/{hm} ns")
        elif ht is None:
            out.append(f"{pre}tPLH {lt}/{lm} ns")
        else:
            out.append(f"{pre}tPLH {lt}/{lm} ns, tPHL {ht}/{hm} ns")
    return "; ".join(out) + " (typ/max)"


def icc(h, l):
    return f"ICCH {h[0]}/{h[1]} mA, ICCL {l[0]}/{l[1]} mA (typ/max)"


def D(**kw):
    return kw


# codes: (MPN suffix, lifecycle). sym: the 74xx symbol used; ieee: 74xx_IEEE symbol or None.
DEVICES = [
    D(base="00", mpn="SN7400", codes=[("N", "Active"), ("D", "Active")], pins=14,
      sym="7400", ieee="7400", ds="sn7400.pdf", link=True,
      gate_function="Quadruple 2-input positive-NAND gate", function_category="gate",
      channels=4, inputs_per_gate=2, logic_polarity="inverting",
      propagation_delay=tpd(("", 11, 22, 7, 15)), supply_current=icc((4, 8), (12, 22)),
      kw="NAND,quad 2-input NAND"),
    D(base="02", mpn="SN7402", codes=[("N", "Active")], pins=14,
      sym="7402", ieee="7402", ds="sn7402.pdf", link=True,
      gate_function="Quadruple 2-input positive-NOR gate", function_category="gate",
      channels=4, inputs_per_gate=2, logic_polarity="inverting",
      propagation_delay=tpd(("", 12, 22, 8, 15)), supply_current=icc((8, 16), (14, 27)),
      kw="NOR,quad 2-input NOR"),
    D(base="04", mpn="SN7404", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS04", ieee="7404", ds="sn7404.pdf", link=True,
      gate_function="Hex inverter", function_category="gate",
      channels=6, inputs_per_gate=1, logic_polarity="inverting",
      propagation_delay=tpd(("", 12, 22, 8, 15)), supply_current=icc((6, 12), (18, 33)),
      kw="inverter,hex inverter,NOT,clock oscillator"),
    D(base="07", mpn="SN7407", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS07", ieee="7407", ds="sn7407.pdf", link=True,
      gate_function="Hex buffer/driver, open-collector high-voltage outputs (30 V)",
      function_category="buffer", channels=6, inputs_per_gate=1,
      logic_polarity="non-inverting", output_type="open-collector",
      voh_min=None, vol_max=0.7,
      output_current="IOL 40mA, VOH max 30V (VOL 0.7V at 40mA, 0.4V at 16mA)",
      propagation_delay=tpd(("", 6, 10, 20, 30)) + ", RL 110 ohm",
      supply_current=icc((29, 41), (21, 30)),
      kw="buffer,driver,open collector,open-collector,30V,hex buffer"),
    D(base="17", mpn="SN7417", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS07", ieee="7417", ds="sn7407.pdf", link=True,
      gate_function="Hex buffer/driver, open-collector high-voltage outputs (15 V)",
      function_category="buffer", channels=6, inputs_per_gate=1,
      logic_polarity="non-inverting", output_type="open-collector",
      voh_min=None, vol_max=0.7,
      output_current="IOL 40mA, VOH max 15V (VOL 0.7V at 40mA, 0.4V at 16mA)",
      propagation_delay=tpd(("", 6, 10, 20, 30)) + ", RL 110 ohm",
      supply_current=icc((29, 41), (21, 30)),
      kw="buffer,driver,open collector,open-collector,15V,hex buffer"),
    D(base="10", mpn="SN7410", codes=[("N", "Obsolete")], pins=14,
      sym="74LS10", ieee="7410", ds="sn74ls10.pdf", link=False,
      gate_function="Triple 3-input positive-NAND gate", function_category="gate",
      channels=3, inputs_per_gate=3, logic_polarity="inverting",
      propagation_delay=tpd(("", 11, 22, 7, 15)), supply_current=icc((3, 6), (9, 16.5)),
      kw="NAND,triple 3-input NAND"),
    D(base="30", mpn="SN7430", codes=[("N", "Obsolete")], pins=14,
      sym="74LS30", ieee="7430", ds="sn74ls30.pdf", link=False,
      gate_function="8-input positive-NAND gate", function_category="gate",
      channels=1, inputs_per_gate=8, logic_polarity="inverting",
      propagation_delay=tpd(("", 13, 22, 8, 15)), supply_current=icc((1, 2), (3, 6)),
      kw="NAND,8-input NAND"),
    D(base="54", mpn="SN7454", codes=[("N", "Obsolete")], pins=14,
      sym="7454", ieee="7454", ds="sn54ls54.pdf", link=False,
      gate_function="4-wide 2-2-2-2-input AND-OR-INVERT gate, Y = /(AB + CD + EF + GH)",
      function_category="gate", channels=1, inputs_per_gate=2,
      logic_polarity="inverting",
      propagation_delay=tpd(("", 13, 22, 8, 15)), supply_current=icc((4, 8), (5.1, 9.5)),
      kw="AND-OR-INVERT,AOI,and-nor"),
    D(base="93", mpn="SN7493A", codes=[("N", "Obsolete")], pins=14,
      sym="74LS93", ieee="7493", ds="sn74ls90.pdf", link=False,
      gate_function="4-bit binary counter (divide-by-2 and divide-by-8), VCC pin 5, GND pin 10",
      function_category="counter", channels=1, bit_width=4,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="CKA 32 MHz min / 42 MHz typ, CKB 16 MHz min",
      propagation_delay=tpd(("CKA->QA", 10, 16, 12, 18), ("CKA->QD", 46, 70, 46, 70),
                            ("R0->any", None, None, 26, 40)),
      supply_current="ICC 26/39 mA (typ/max)",
      kw="counter,binary counter,ripple counter,divide by 16"),
    D(base="123", mpn="SN74123", codes=[("N", "Active")], pins=16,
      sym="74LS123", ieee=None, ds="sn74123.pdf", link=True,
      gate_function="Dual retriggerable monostable multivibrator with clear",
      function_category="monostable", channels=2,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("A->Q", 22, 33, None, None), ("B->Q", 19, 28, None, None),
                            ("A->/Q", None, None, 30, 40), ("Clear->Q", None, None, 18, 27)),
      supply_current="ICC 46/66 mA (typ/max)",
      timing=("tw = 0.28 x RT x Cext x (1 + 0.7/RT) for Cext > 1000 pF (RT kohm, Cext pF, "
              "tw ns; 0.25 with the diode circuit); Rext 5-50 kohm external only; "
              "tw 3.03 us typ at 10 kohm / 1000 pF; tw(min) 45 ns typ. "
              "Not interchangeable with the 74LS123 (about 0.45 x RT x Cext)"),
      kw="monostable,one-shot,multivibrator,retriggerable,timer"),
    D(base="390", mpn="SN74390", codes=[("N", "Obsolete")], pins=16,
      sym="74LS390", ieee="74LS390", ds="sn74ls390.pdf", link=False,
      gate_function="Dual 4-bit decade counter (divide-by-2 and divide-by-5 sections)",
      function_category="counter", channels=2, bit_width=4,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="A 25 MHz min / 35 MHz typ, B 20 MHz min / 30 MHz typ",
      propagation_delay=tpd(("A->QA", 12, 20, 13, 20), ("A->QC", 37, 60, 39, 60),
                            ("Clear->any", None, None, 24, 39)),
      supply_current="ICC 42/69 mA (typ/max)",
      kw="counter,decade counter,BCD counter,divide by 10"),
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def rows():
    out = []
    for dev in DEVICES:
        value = f"74{dev['base']}"
        for suffix, status in dev["codes"]:
            kind = PKG_OF[suffix]
            pkg = f"{kind}-{dev['pins']}"
            mpn = f"{dev['mpn']}{suffix}"
            desc = f"{dev['gate_function']}, standard TTL (not 74LS), {pkg}"
            if dev.get("timing"):
                desc += f". {dev['timing']}"
            r = {
                **FAMILY,
                **{k: v for k, v in dev.items() if k in COLS},
                "unique_id": f"TI-{mpn}", "mpn": mpn, "value": value,
                "base_number": dev["base"], "package": pkg, "pin_count": str(dev["pins"]),
                "part_locator": f"IC_LOGIC {value} {pkg}",
                "description": desc,
                "datasheet": f"{DS}/{dev['ds']}",
                "manufacturer_link": (f"https://www.ti.com/product/{dev['mpn']}"
                                      if dev["link"] else None),
                "kicad_symbol": f"74xx:{dev['sym']}",
                "kicad_footprint": FOOTPRINT[(kind, dev["pins"])],
                "lifecycle_status": status,
                "rohs": "Yes" if status == "Active" else "No",
                "keywords": ",".join(dict.fromkeys(
                    ["TTL", "standard TTL", "74 series", value, f"SN{value}", dev["mpn"],
                     mpn] + dev["kw"].split(","))),
            }
            out.append(r)
            if dev["ieee"]:
                out.append({**r, "variant": "IEEE", "unique_id": r["unique_id"] + "-IEEE",
                            "kicad_symbol": f"74xx_IEEE:{dev['ieee']}"})
    return out


def check(rs):
    for dev in DEVICES:
        p = ROOT / "datasheets" / "ti" / dev["ds"]
        if not p.exists():
            raise SystemExit(f"missing data sheet {p}")
    ids = [r["unique_id"] for r in rs]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit(f"duplicate unique_id: {sorted(dup)}")


def main():
    rs = rows()
    check(rs)
    lines = [
        "-- Terra EDA Library - standard (no-letter) 74xx TTL, Texas Instruments",
        f"-- Generated by {CREATED_BY}. dump_priority=0: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in rs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_logic ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rs)} rows across {len(DEVICES)} devices")


if __name__ == "__main__":
    main()
