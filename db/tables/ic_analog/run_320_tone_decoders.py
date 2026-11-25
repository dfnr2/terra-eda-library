#!/usr/bin/env python3
"""PLL tone decoders and phase-locked loops: TI LM567C and Signetics NE565.

LM567C (datasheets/ti/lm567c.pdf, SNOSBQ4F, Jan 2022). Figures are the electrical
table at 25 C, V+ = 5 V:
  - Supply range 4.75-9 V (electrical table; the ROC table prints 3.5-8.5 V).
  - Quiescent current 7 mA typ (10 mA max), 12 mA typ activated.
  - Highest center frequency 500 kHz typ (100 kHz min); detection bandwidth up to
    14% typ of f0; output sinks 100 mA (saturated transistor to ground).
  - 0-70 C operating, per TI's orderable data.
  TI sells only the LM567C: LM567CN/NOPB (PDIP) and LM567CM/NOPB (SOIC), Active on the
  ti.com product page 2026-11-25. The military LM567 and the NE567 have no TI product
  page. Pinout matches the stock Timer:NE567 symbol pin for pin.

NE565 (datasheets/signetics/ne565-phase-locked-loop.pdf, Signetics NE/SE565 product
specification, July 1988):
  - Supply +/-6 V to +/-12 V (12-24 V across V+ to V-); 26 V absolute maximum.
  - Supply current 8 mA typ, 12.5 mA max.
  - VCO center frequency up to 500 kHz typ; 0.001 Hz-500 kHz operating range.
  - Square-wave VCO output sinks 1 mA / sources 10 mA typ.
  - 0-70 C (NE565).
  The NE565N (14-pin plastic DIP) is the only row: the NE565D SO-14 has a different
  ("non-standard") pinout and the F suffix is cerdip. No maker sells it today, so it
  is Obsolete, kept for restorations. KiCad has no 565 symbol; the custom
  terra_symbols_ic_analog:NE565 follows the N-package pinout. supply_voltage_min/max
  hold the total span (12/24 V) since the column has no split-supply form.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_analog_generated_320_tone_decoders.sql")
CREATED_BY = Path(__file__).name
TABLE = "ic_analog"
DS = "${TERRA_EDA_LIB}/datasheets/"

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
    allow_substitution="No", tracking="No", created_by=CREATED_BY, source=None,
    dump_priority=0, tier=2, channels=1, resolution_bits=None, interface=None,
)

LM567_TEXT = ("PLL tone decoder, center frequency 0.01Hz-500kHz set by external RC, "
              "bandwidth adjustable 0-14%, output sinks 100mA, 7mA typ quiescent, "
              "4.75-9V, 0 to +70°C")
LM567_KW = ["567", "tone decoder", "PLL", "phase-locked loop", "DTMF", "FSK",
            "frequency detector", "LM567C", "NE567"]

PARTS = [
    dict(unique_id="Texas_Instruments-LM567CN/NOPB", mpn="LM567CN/NOPB",
         manufacturer="Texas Instruments", value="LM567C", package="PDIP-8",
         part_locator="tone-decoder-567-bipolar-pdip8",
         description=f"Texas Instruments LM567C {LM567_TEXT}, PDIP-8",
         datasheet=DS + "ti/lm567c.pdf", manufacturer_link="https://www.ti.com/product/LM567C",
         kicad_symbol="Timer:NE567", kicad_footprint="Package_DIP:DIP-8_W7.62mm",
         lifecycle_status="Active", rohs="Yes", pin_count="8",
         keywords=",".join(LM567_KW + ["LM567CN/NOPB"]),
         temp_operating_min=0.0, temp_operating_max=70.0, function_type="tone-decoder",
         supply_voltage_min=4.75, supply_voltage_max=9.0),
    dict(unique_id="Texas_Instruments-LM567CM/NOPB", mpn="LM567CM/NOPB",
         manufacturer="Texas Instruments", value="LM567C", package="SOIC-8",
         part_locator="tone-decoder-567-bipolar-soic8",
         description=f"Texas Instruments LM567C {LM567_TEXT}, SOIC-8",
         datasheet=DS + "ti/lm567c.pdf", manufacturer_link="https://www.ti.com/product/LM567C",
         kicad_symbol="Timer:NE567", kicad_footprint="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
         lifecycle_status="Active", rohs="Yes", pin_count="8",
         keywords=",".join(LM567_KW + ["LM567CM/NOPB"]),
         temp_operating_min=0.0, temp_operating_max=70.0, function_type="tone-decoder",
         supply_voltage_min=4.75, supply_voltage_max=9.0),
    dict(unique_id="Signetics-NE565N", mpn="NE565N", manufacturer="Signetics",
         value="NE565", package="PDIP-14", part_locator="pll-565-bipolar-pdip14",
         description=("Signetics NE565 phase-locked loop, VCO + phase comparator + "
                      "amplifier, 0.001Hz-500kHz, linear FM/FSK demodulator output, "
                      "TTL/DTL-compatible square-wave and triangle VCO outputs, 8mA typ "
                      "supply, ±6V to ±12V (12-24V total), 0 to +70°C, PDIP-14 "
                      "(N package pinout)"),
         datasheet=DS + "signetics/ne565-phase-locked-loop.pdf",
         manufacturer_link="https://www.nxp.com/support/sample-and-buy/obsolete-products:WTOBUY_OBSOL",
         kicad_symbol="terra_symbols_ic_analog:NE565",
         kicad_footprint="Package_DIP:DIP-14_W7.62mm", lifecycle_status="Obsolete",
         rohs="No", pin_count="14",
         keywords=",".join(["565", "PLL", "phase-locked loop", "FM demodulator",
                            "FSK demodulator", "tone decoder", "VCO", "NE565",
                            "NE565N", "Signetics", "Philips", "vintage"]),
         temp_operating_min=0.0, temp_operating_max=70.0, function_type="pll",
         supply_voltage_min=12.0, supply_voltage_max=24.0),
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    root = Path(__file__).resolve().parents[3]
    recs = [dict(DEFAULTS, **p) for p in PARTS]
    seen = set()
    for r in recs:
        if r["unique_id"] in seen:
            raise SystemExit(f"duplicate unique_id: {r['unique_id']}")
        seen.add(r["unique_id"])
        path = root / r["datasheet"].replace("${TERRA_EDA_LIB}/", "")
        if not path.is_file():
            raise SystemExit(f"missing datasheet {r['datasheet']}")
    lines = [
        "-- Terra EDA Library - ic_analog PLL tone decoders (TI LM567C, Signetics NE565)",
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
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} rows")


if __name__ == "__main__":
    main()
