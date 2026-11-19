#!/usr/bin/env python3
"""Signetics 8T-series 3-state bus buffers and transceivers: 8T26A, 8T28, 8T95-8T98.

Vintage Schottky bus interface parts with 48 mA low-state drive, common on 1970s-80s
microcomputer boards. Every orderable code in the Signetics ordering tables is
emitted: commercial N-grade (0 to 70 C) in plastic (N suffix) and ceramic (F suffix)
DIP, plus the military S-grade (-55 to 125 C) ceramic codes the book lists. All of
these parts are obsolete.

Source: Signetics "Logic Interface" data book, October 1981, sections stored locally
in datasheets/signetics/.

Symbols are IEEE style:
  - 8T95/96/97/98 have the 74365/366/367/368 pinout pin for pin (DIS1 = pin 1,
    DIS2 = pin 15; 8T97/98 split 4+2), so they use the stock 74xx_IEEE symbols.
    Signetics' active-high DISn are the stock symbols' active-low ~En/~nG.
  - 8T26A/8T28 have no stock equivalent; terra_symbols_ic_logic carries IEEE-style
    symbols drawn from the data book's pin configuration.
Plastic and ceramic DIP share the stock DIP-16 0.3in land pattern.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_logic_generated_340_8t_buffers.sql")
CREATED_BY = Path(__file__).name

DS_XCVR = "${TERRA_EDA_LIB}/datasheets/signetics/8t26a-8t28-quad-bus-transceiver.pdf"
DS_HEX = "${TERRA_EDA_LIB}/datasheets/signetics/8t95-8t98-hex-3-state-buffers.pdf"

# Signetics no longer exists and NXP (its successor through Philips) has no product
# pages for these parts; this is NXP's page for obsolete parts and authorized EOL resellers.
MFR_LINK = "https://www.nxp.com/support/sample-and-buy/obsolete-products:WTOBUY_OBSOL"

FOOTPRINT = "Package_DIP:DIP-16_W7.62mm"
PACKAGES = {"N": "PDIP-16", "F": "CDIP-16"}

# Grade -> (MPN prefix, temp min, temp max, Vcc min, Vcc max)
GRADES = {
    "commercial": ("N", 0, 70, 4.75, 5.25),
    "military": ("S", -55, 125, 4.5, 5.5),
}


def D(**kw):
    return kw


# Electrical values are from each section's recommended operating conditions, DC and
# AC tables. Typical delay / supply current are the front-page figures; maxima are
# the AC and DC table limits. Military rows override the output ratings that differ.
DEVICES = [
    D(base="26A", symbol="terra_symbols_ic_logic:8T26A", ds=DS_XCVR,
      gate_function="Quad 3-state bus transceiver, inverting",
      function_category="transceiver", channels=4, logic_polarity="inverting",
      propagation_delay="7 ns typ / 14 ns max (driver CL=300pF, receiver CL=30pF)",
      supply_current="48 mA typ / 87 mA max",
      voh_min=2.4,
      output_current="driver IOL 48mA / IOH -10mA; receiver IOL 20mA",
      mil_output_current="driver IOL 32mA / IOH -2mA; receiver IOL 12mA",
      enables="active-low receiver enable, active-high driver enable",
      kw=["bus transceiver", "quad transceiver", "bidirectional"],
      codes={"commercial": "NF", "military": "F"}),
    D(base="28", symbol="terra_symbols_ic_logic:8T28", ds=DS_XCVR,
      gate_function="Quad 3-state bus transceiver, non-inverting",
      function_category="transceiver", channels=4, logic_polarity="non-inverting",
      propagation_delay="10 ns typ / 17 ns max (driver CL=300pF, receiver CL=30pF)",
      supply_current="67 mA typ / 110 mA max",
      voh_min=2.4,
      output_current="driver IOL 48mA / IOH -10mA; receiver IOL 20mA",
      mil_output_current="driver IOL 32mA / IOH -2mA; receiver IOL 12mA",
      enables="active-low receiver enable, active-high driver enable",
      kw=["bus transceiver", "quad transceiver", "bidirectional"],
      codes={"commercial": "NF", "military": "F"}),
    D(base="95", symbol="74xx_IEEE:74LS365", ds=DS_HEX,
      gate_function="Hex 3-state buffer, non-inverting",
      function_category="buffer", channels=6, logic_polarity="non-inverting",
      propagation_delay="8 ns typ / 13 ns max (CL=50pF)",
      supply_current="65 mA typ / 98 mA max",
      voh_min=2.4, output_current="IOL 48mA / IOH -5.2mA", mil_output_current=None,
      enables="common 2-input disable", pinout="74365",
      kw=["hex buffer", "bus driver"],
      codes={"commercial": "NF", "military": "F"}),
    D(base="96", symbol="74xx_IEEE:74LS366", ds=DS_HEX,
      gate_function="Hex 3-state inverter",
      function_category="buffer", channels=6, logic_polarity="inverting",
      propagation_delay="6.5 ns typ / 11 ns max (CL=50pF)",
      supply_current="59 mA typ / 89 mA max",
      voh_min=2.4, output_current="IOL 48mA / IOH -5.2mA", mil_output_current=None,
      enables="common 2-input disable", pinout="74366",
      kw=["hex inverter", "bus driver"],
      codes={"commercial": "NF"}),
    D(base="97", symbol="74xx_IEEE:74LS367", ds=DS_HEX,
      gate_function="Hex 3-state buffer, non-inverting",
      function_category="buffer", channels=6, logic_polarity="non-inverting",
      propagation_delay="8 ns typ / 13 ns max (CL=50pF)",
      supply_current="65 mA typ / 98 mA max",
      voh_min=2.4, output_current="IOL 48mA / IOH -5.2mA", mil_output_current=None,
      enables="4+2 split disables", pinout="74367",
      kw=["hex buffer", "bus driver"],
      codes={"commercial": "NF", "military": "F"}),
    D(base="98", symbol="74xx_IEEE:74LS368", ds=DS_HEX,
      gate_function="Hex 3-state inverter",
      function_category="buffer", channels=6, logic_polarity="inverting",
      propagation_delay="6.5 ns typ / 11 ns max (CL=50pF)",
      supply_current="59 mA typ / 89 mA max",
      voh_min=2.4, output_current="IOL 48mA / IOH -5.2mA", mil_output_current=None,
      enables="4+2 split disables", pinout="74368",
      kw=["hex inverter", "bus driver"],
      codes={"commercial": "NF", "military": "F"}),
]

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "variant", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking", "standards_version",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "logic_family", "base_number", "gate_function", "function_category", "channels",
    "inputs_per_gate", "bit_width", "logic_polarity", "output_type", "schmitt_trigger",
    "supply_voltage_min", "supply_voltage_max", "vih_min", "vil_max", "voh_min",
    "vol_max", "propagation_delay", "max_frequency", "output_current", "supply_current",
]


def records():
    for dev in DEVICES:
        part = f"8T{dev['base']}"
        for grade, pkg_codes in dev["codes"].items():
            prefix, tmin, tmax, vmin, vmax = GRADES[grade]
            for code in pkg_codes:
                mpn = f"{prefix}{part}{code}"
                package = PACKAGES[code]
                military = grade == "military"
                notes = [dev["enables"], "48mA bus drive"]
                if dev.get("pinout"):
                    notes.append(f"{dev['pinout']} pinout")
                if military:
                    notes.append("military -55 to 125C")
                yield {
                    "unique_id": f"Signetics-{mpn}",
                    "part_locator": f"logic-{part.lower()}-dip16",
                    "mpn": mpn, "manufacturer": "Signetics", "package": package,
                    "value": part,
                    "description": f"Signetics {part} {dev['gate_function'].lower()}, "
                                   f"{', '.join(notes)}, {package}",
                    "datasheet": dev["ds"], "manufacturer_link": MFR_LINK,
                    "kicad_symbol": dev["symbol"], "kicad_footprint": FOOTPRINT,
                    "lifecycle_status": "Obsolete", "rohs": "No",
                    "allow_substitution": "Yes", "tracking": "No",
                    "standards_version": "1.0", "created_by": CREATED_BY,
                    "source": None, "dump_priority": 0, "tier": 2,
                    "keywords": ", ".join(
                        [part, "Signetics", "8T", "3-state", "tri-state", "Schottky",
                         "vintage"] + dev["kw"]
                        + ([f"{dev['pinout']} pinout"] if dev.get("pinout") else [])),
                    "pin_count": "16",
                    "temp_operating_min": tmin, "temp_operating_max": tmax,
                    "logic_family": "8T", "base_number": part,
                    "gate_function": dev["gate_function"],
                    "function_category": dev["function_category"],
                    "channels": dev["channels"], "logic_polarity": dev["logic_polarity"],
                    "output_type": "3-state", "schmitt_trigger": "no",
                    "supply_voltage_min": vmin, "supply_voltage_max": vmax,
                    # 8T95-98 military VIL is 0.7 V (S8T only, per the recommended
                    # operating conditions note); 8T26A/28 keep 0.8 V in both grades.
                    "vih_min": 2.0,
                    "vil_max": 0.7 if military and dev["base"] in ("95", "96", "97", "98") else 0.8,
                    "voh_min": dev["voh_min"], "vol_max": 0.5,
                    "propagation_delay": dev["propagation_delay"],
                    "output_current": (dev["mil_output_current"] if military and dev["mil_output_current"]
                                       else dev["output_current"]),
                    "supply_current": dev["supply_current"],
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
        "-- Terra EDA Library - ic_logic Signetics 8T bus buffers and transceivers",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_logic ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} parts")


if __name__ == "__main__":
    main()
