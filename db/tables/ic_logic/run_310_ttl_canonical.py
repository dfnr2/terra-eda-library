#!/usr/bin/env python3
"""Canonical 74LS TTL parts — the landing-check set before the full harvest.

Five iconic 7400-series functions (NAND, inverter, D flip-flop, 3-to-8 decoder,
octal 3-state buffer) in the 74LS family, each in its PDIP and SOIC package, on
KiCad's stock 74xx: symbols and standard DIP/SO footprints. Electrical specs are
the 74LS recommended-operating values from the TI datasheets (stored locally).

Once this set proves the schema/footprint/symbol wiring, run_320+ fans out across
the rest of the 74xx KiCad symbol library. Generated output (dump_priority=0) is
not dumped back to static SQL.
"""
import re
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_logic_generated_310_ttl_canonical.sql")

# IEEE rectangular-symbol lib (bare device numbers like 7400); covers a subset.
IEEE_CANDIDATES = [
    "/usr/share/kicad/symbols/74xx_IEEE.kicad_sym",
    "/usr/local/share/kicad/symbols/74xx_IEEE.kicad_sym",
]

COLS = [
    "unique_id", "variant", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "standards_version", "source", "dump_priority", "tier", "lifecycle_status",
    "pin_count", "temp_operating_min", "temp_operating_max",
    "logic_family", "base_number", "gate_function", "function_category",
    "channels", "inputs_per_gate", "bit_width", "logic_polarity", "output_type",
    "schmitt_trigger", "supply_voltage_min", "supply_voltage_max",
    "vih_min", "vil_max", "voh_min", "vol_max", "propagation_delay",
    "max_frequency", "output_current", "supply_current",
]

# 74LS recommended operating conditions / guaranteed levels, shared family-wide.
DEFAULTS = dict(
    manufacturer="Texas Instruments", logic_family="74LS",
    rohs="Yes", allow_substitution="Yes", tracking="No",
    standards_version="1.0", source="ti_74xx", dump_priority=0, tier=2,
    lifecycle_status="Active", temp_operating_min=0, temp_operating_max=70,
    schmitt_trigger="no", supply_voltage_min=4.75, supply_voltage_max=5.25,
    vih_min=2.0, vil_max=0.8, voh_min=2.7, vol_max=0.5,
    output_current="IOL 8mA / IOH -0.4mA",
)

# Packages keyed by pin count: (package, MPN suffix, footprint).
PKG = {
    14: [("PDIP-14", "N", "Package_DIP:DIP-14_W7.62mm"),
         ("SOIC-14", "D", "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm")],
    16: [("PDIP-16", "N", "Package_DIP:DIP-16_W7.62mm"),
         ("SOIC-16", "D", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm")],
    20: [("PDIP-20", "N", "Package_DIP:DIP-20_W7.62mm"),
         ("SOIC-20W", "DW", "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm")],
}


def D(**kw):
    return kw


# value = the schematic part name; mpn_base = TI ordering root; ds = local datasheet stem.
DEVICES = [
    D(base="00", value="74LS00", mpn_base="74LS00", ds="sn74ls00", pins=14,
      gate_function="Quad 2-input NAND gate", function_category="gate",
      channels=4, inputs_per_gate=2, bit_width=None, logic_polarity="inverting",
      output_type="totem-pole", propagation_delay="9 ns typ / 15 ns max",
      max_frequency=None, supply_current="4.4 mA max"),
    D(base="04", value="74LS04", mpn_base="74LS04", ds="sn74ls04", pins=14,
      gate_function="Hex inverter", function_category="gate",
      channels=6, inputs_per_gate=1, bit_width=None, logic_polarity="inverting",
      output_type="totem-pole", propagation_delay="9 ns typ / 15 ns max",
      max_frequency=None, supply_current="6.6 mA max"),
    D(base="74", value="74LS74", mpn_base="74LS74A", ds="sn74ls74a", pins=14,
      gate_function="Dual D-type positive-edge-triggered flip-flop with preset and clear",
      function_category="flip-flop",
      channels=2, inputs_per_gate=None, bit_width=None,
      logic_polarity="non-inverting", output_type="totem-pole",
      propagation_delay="25 ns max", max_frequency="25 MHz",
      supply_current="8 mA max"),
    D(base="138", value="74LS138", mpn_base="74LS138", ds="sn74ls138", pins=16,
      gate_function="3-to-8 line decoder/demultiplexer", function_category="decoder",
      channels=1, inputs_per_gate=None, bit_width=None, logic_polarity="inverting",
      output_type="totem-pole", propagation_delay="22 ns max",
      max_frequency=None, supply_current="6.3 mA max"),
    D(base="244", value="74LS244", mpn_base="74LS244", ds="sn74ls244", pins=20,
      gate_function="Octal buffer/line driver, 3-state", function_category="buffer",
      channels=8, inputs_per_gate=1, bit_width=8, logic_polarity="non-inverting",
      output_type="3-state", propagation_delay="12 ns typ", max_frequency=None,
      supply_current="17 mA typ", output_current="IOL 24mA / IOH -15mA"),
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    rows = []
    for dev in DEVICES:
        for pkg, suffix, fp in PKG[dev["pins"]]:
            mpn = f"SN{dev['mpn_base']}{suffix}"
            row = {
                **DEFAULTS, **dev,
                "unique_id": f"TI-{mpn}",
                "base_number": dev["base"],
                "part_locator": f"IC_LOGIC {dev['value']} {pkg}",
                "mpn": mpn, "package": pkg, "pin_count": str(dev["pins"]),
                "description": f"{dev['gate_function']}, 74LS, {pkg}",
                "datasheet": f"${{TERRA_EDA_LIB}}/datasheets/ti/{dev['ds']}.pdf",
                "manufacturer_link": f"https://www.ti.com/product/SN{dev['mpn_base']}",
                "kicad_symbol": f"74xx:{dev['value']}",
                "kicad_footprint": fp,
            }
            rows.append(row)

    # IEEE-symbol variants: clone any row whose IEEE glyph exists (matched by the
    # bare device number 74<base>), swapping symbol + tagging variant='IEEE'.
    ieee_lib = next((p for p in IEEE_CANDIDATES if Path(p).exists()), None)
    ieee_names = set(re.findall(r'^\t\(symbol "([^"]+)"', Path(ieee_lib).read_text(), re.M)) if ieee_lib else set()
    for r in list(rows):
        cand = f"74{r['base_number']}"
        if cand in ieee_names:
            rows.append({**r, "variant": "IEEE",
                         "unique_id": r["unique_id"] + "-IEEE",
                         "kicad_symbol": f"74xx_IEEE:{cand}"})

    lines = [
        "-- Terra EDA Library - canonical 74LS TTL set",
        f"-- Generated by {Path(__file__).name}. dump_priority=0: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in rows:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_logic ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} rows across {len(DEVICES)} devices")


if __name__ == "__main__":
    main()
