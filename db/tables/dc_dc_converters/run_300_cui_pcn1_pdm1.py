#!/usr/bin/env python3
"""CUI PCN1-S (active) and PDM1-S5-D15-S (discontinued) 1 W isolated DC-DC converters.

PCN1-S: all 18 models in the 2025-04-24 datasheet (5/12/24 V in; 5/12/15 V single and
+/-5/12/15 V dual out), datasheets/cui/PCN1-S.pdf.
PDM1-S5-D15-S: the Asteroids adapter's VR1. CUI stamps the PDM1-S datasheet
DISCONTINUED, so the row is `Obsolete` and its bom_comment names the replacement. The
other PDM1-S models are not listed (discontinued, and nothing uses them).

Parameters come from the datasheet tables: the model table (input range, output,
current, power, ripple, efficiency) and the INPUT/OUTPUT/SAFETY/ENVIRONMENTAL tables.
Plan: plans/dc-dc-cui-pcn1.md. Generated output (dump_priority=0, source=NULL) is not
dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "dc_dc_converters_generated_300_cui_pcn1_pdm1.sql"
CREATED_BY = Path(__file__).name

PCN_DATASHEET = "${TERRA_EDA_LIB}/datasheets/cui/PCN1-S.pdf"
PDM_DATASHEET = "${TERRA_EDA_LIB}/datasheets/cui/PDM1-S.pdf"
LINK = "https://www.cui.com/product/dc-dc-converters"
SYM_SINGLE = "terra_symbols_dc_dc_converters:DCDC_Isolated_Single"
SYM_DUAL = "terra_symbols_dc_dc_converters:DCDC_Isolated_Dual"
FP_LIB = "terra_footprints_dc_dc_converters:"

# Input voltage class -> (nominal V, min V, max V, footprint; 24 V models have a wider body).
INPUTS = {
    5:  (5.0, 4.5, 5.5, FP_LIB + "CUI_PCN1-S_SIP-5_P2.54mm"),
    12: (12.0, 10.8, 13.2, FP_LIB + "CUI_PCN1-S_SIP-5_P2.54mm"),
    24: (24.0, 21.6, 26.4, FP_LIB + "CUI_PCN1-S24_SIP-5_P2.54mm"),
}

# Output code -> (config, volts per rail, max amps per rail). Per-rail currents are the
# datasheet "max" column; for dual models that is the current of each of the two rails.
OUTPUTS = {
    "S5":  ("single", 5.0, 0.200), "S12": ("single", 12.0, 0.084), "S15": ("single", 15.0, 0.067),
    "D5":  ("dual", 5.0, 0.100), "D12": ("dual", 12.0, 0.042), "D15": ("dual", 15.0, 0.033),
}

# Typical efficiency (%) per model, from the datasheet model table.
EFFICIENCY = {
    (5, "S5"): 79, (5, "S12"): 79, (5, "S15"): 79, (5, "D5"): 74, (5, "D12"): 78, (5, "D15"): 78,
    (12, "S5"): 80, (12, "S12"): 81, (12, "S15"): 81, (12, "D5"): 77, (12, "D12"): 80, (12, "D15"): 81,
    (24, "S5"): 80, (24, "S12"): 83, (24, "S15"): 81, (24, "D5"): 79, (24, "D12"): 81, (24, "D15"): 82,
}

REPLACEMENT = "PCN1-S5-D15-S"   # like-for-like: 5 V in, +/-15 V out, +/-33 mA, same pinout

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "value", "description",
    "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking", "bom_comment",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count", "package",
    "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max",
    "temp_soldering", "input_voltage_nominal", "input_voltage_min", "input_voltage_max",
    "output_config", "output_voltage", "output_current", "output_power", "isolated",
    "isolation_voltage", "regulated", "efficiency", "ripple_noise",
]


def rail_text(cfg, v):
    return f"+/-{v:g}V dual" if cfg == "dual" else f"{v:g}V single"


def pcn_parts():
    for vin, (nom, lo, hi, fp) in INPUTS.items():
        for out, (cfg, v, amps) in OUTPUTS.items():
            mpn = f"PCN1-S{vin}-{out}-S"
            yield {
                "unique_id": f"CUI-{mpn}", "mpn": mpn, "value": mpn,
                "part_locator": f"dcdc-isolated-1w-{nom:g}vin-{cfg}-{v:g}v",
                "description": (
                    f"CUI {mpn} isolated DC-DC converter, {nom:g}V in ({lo:g}-{hi:g}V), "
                    f"{rail_text(cfg, v)} out, {amps * 1000:g}mA per rail, 1W, 1500Vdc isolation, "
                    "unregulated, SIP"),
                "datasheet": PCN_DATASHEET, "kicad_footprint": fp,
                "kicad_symbol": SYM_DUAL if cfg == "dual" else SYM_SINGLE,
                "lifecycle_status": "Active", "bom_comment": None,
                "pin_count": "5" if cfg == "dual" else "4",
                "temp_operating_min": -40, "temp_operating_max": 100,
                "input_voltage_nominal": nom, "input_voltage_min": lo, "input_voltage_max": hi,
                "output_config": cfg, "output_voltage": v, "output_current": amps,
                "efficiency": EFFICIENCY[(vin, out)], "ripple_noise": 75,
            }


def pdm_part():
    mpn = "PDM1-S5-D15-S"
    nom, lo, hi, _ = INPUTS[5]
    return {
        "unique_id": f"CUI-{mpn}", "mpn": mpn, "value": mpn,
        "part_locator": "dcdc-isolated-1w-5vin-dual-15v",
        "description": (
            "CUI PDM1-S5-D15-S isolated DC-DC converter, 5V in (4.5-5.5V), +/-15V dual out, "
            "34mA per rail, 1W, 1500Vdc isolation, unregulated, SIP. DISCONTINUED"),
        "datasheet": PDM_DATASHEET, "kicad_footprint": INPUTS[5][3],   # same pad pattern as the PCN1-S (checked against both layouts)
        "kicad_symbol": SYM_DUAL,
        "lifecycle_status": "Obsolete",
        "bom_comment": (f"Discontinued by CUI (datasheet stamped DISCONTINUED). "
                        f"Recommended replacement: {REPLACEMENT}."),
        "pin_count": "5",
        "temp_operating_min": -40, "temp_operating_max": 105,
        "input_voltage_nominal": nom, "input_voltage_min": lo, "input_voltage_max": hi,
        "output_config": "dual", "output_voltage": 15.0, "output_current": 0.034,
        "efficiency": 80, "ripple_noise": 60,
    }


COMMON = {
    "manufacturer": "CUI", "manufacturer_link": LINK, "rohs": "Yes",
    "allow_substitution": "No", "tracking": "No", "created_by": CREATED_BY,
    "source": None, "dump_priority": 0, "tier": 2, "package": "SIP",
    "temp_storage_min": -55, "temp_storage_max": 125, "temp_soldering": 260,
    "output_power": 1.0, "isolated": "yes", "isolation_voltage": 1500.0, "regulated": "no",
}


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def keywords(p):
    return ("dc-dc,converter,isolated,module,sip,1w,"
            f"{p['output_config']},{p['output_voltage']:g}v,{p['input_voltage_nominal']:g}v-in,cui,"
            + p["mpn"])


def main():
    rows = [{**COMMON, **p, "keywords": keywords(p)} for p in [*pcn_parts(), pdm_part()]]
    ids = [r["unique_id"] for r in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        sys.exit(f"duplicate unique_id: {dupes}")
    if REPLACEMENT not in {r["mpn"] for r in rows}:
        sys.exit(f"replacement {REPLACEMENT} is not in this table")
    lines = [
        "-- Terra EDA Library - CUI PCN1-S and PDM1-S isolated 1 W DC-DC converters",
        f"-- Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "", "BEGIN TRANSACTION;", "",
        *(f"INSERT INTO dc_dc_converters ({', '.join(COLS)}) VALUES "
          f"({', '.join(sql(r.get(c)) for c in COLS)});" for r in rows),
        "", "COMMIT;", "",
    ]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} parts")
    for d in (PCN_DATASHEET, PDM_DATASHEET):
        if not (ROOT / d.replace("${TERRA_EDA_LIB}/", "")).exists():
            print(f"WARNING: datasheet missing: {d}")


if __name__ == "__main__":
    main()
