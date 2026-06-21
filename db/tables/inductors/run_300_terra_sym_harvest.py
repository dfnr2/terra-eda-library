#!/usr/bin/env python3
"""Emit the inductors catalog harvested from terra_sym.kicad_sym as native rows.

These three power inductors were recovered from the terra_sym.kicad_sym source.
They are scripted here so a schema change reapplies by rebuild rather than a hand
edit of a static dump.

Only a typo contradicted by a part's own other fields is corrected here: the
Bourns SRR6603 mpn carried a junk " q q" suffix ("SRR6603-100ML q q") which is
trimmed to "SRR6603-100ML"; unique_id follows. Its kicad_symbol never had the
" q q" suffix and is preserved verbatim.

Deferred curation (judgement calls intentionally left as-is for a later pass):
  - All three kicad_footprint values are terra_sym:-prefixed, so they point at a
    symbol library rather than a real footprint. Two (SRR6603, MSS7341) even name
    a "Coilcraft MSS7341 Shileded" [sic] footprint that is mismatched to the part
    (the SRR6603 is a Bourns part).
  - The descriptions read "mH" where the parts are actually uH -- the value,
    part_locator and MPN all confirm uH.
  - The SRR6603 tolerance is recorded as '30%' while its description says 20%.
  - The deep tail (inductance, saturation_current, dc_resistance, self_res_freq)
    is still NULL pending a datasheet harvest.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("inductors_generated_300_terra_sym_harvest.sql")

BOURNS_ROHS = "https://www.bourns.com/docs/rohs-cofc/cofc_srr.pdf?sfvrsn=7557d913_18"
BOURNS_MFR_LINK = "https://www.bourns.com/resources/rohs/magnetics/power-inductors-smd-shielded"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution",
    "tracking", "standards_version", "source", "dump_priority", "tier",
    "sim_device", "sim_pins", "pin_count", "temp_operating_min",
    "temp_operating_max", "temp_storage_min", "temp_storage_max", "tolerance",
    "current_rating",
]

PARTS = [
    {
        # FIX: mpn carried a junk " q q" suffix ("SRR6603-100ML q q") -> trimmed;
        # unique_id follows. The kicad_symbol never had the suffix; left verbatim.
        "unique_id": "Bourns-SRR6603-100ML",
        "part_locator": "IND Bourns 10uH 1.1A rms SRR6603-100ML",
        "mpn": "SRR6603-100ML", "manufacturer": "Bourns", "package": "SMT",
        "value": "IND Bourns 10uH 1.1A rms SRR6603-100ML",
        "description": "Power inductor, 10 mH, 75 mOhm, 1A rms,  20% SMT 6.8x4.4mm",
        "datasheet": "https://www.bourns.com/pdfs/SRR6603.pdf",
        "manufacturer_link": BOURNS_MFR_LINK,
        "kicad_symbol": "terra_sym:IND Bourns 10uH 1.1A rms SRR6603-100ML",
        "kicad_footprint": "terra_sym:Coilcraft MSS7341 Shileded power inductor",
        "rohs": "Yes", "rohs_document_link": BOURNS_ROHS,
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "L", "sim_pins": "1=+ 2=-", "pin_count": "2",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -40, "temp_storage_max": 125, "tolerance": "30%",
        "current_rating": "1.1A rms, 40C rise, 1.5ADC, 10% drop",
    },
    {
        "unique_id": "Bourns-SRR1210-680M",
        "part_locator": "IND Bourns 68uH 3A rms  SRR1210-680M ",
        "mpn": "SRR1210-680M", "manufacturer": "Bourns", "package": "SMT",
        "value": "IND Bourns 68uH 3A rms  SRR1210-680M",
        "description": "Power inductor, 68 mH, 102 mOhm, 3A rms,  20% SMT 12mm x 12mm",
        "datasheet": "https://www.bourns.com/docs/Product-Datasheets/SRR1210.pdf",
        "manufacturer_link": BOURNS_MFR_LINK,
        "kicad_symbol": "terra_sym:IND Bourns 68uH 3A rms  SRR1210-680M ",
        "kicad_footprint": "terra_sym:Bourns SRR1210",
        "rohs": "Yes", "rohs_document_link": BOURNS_ROHS,
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "L", "sim_pins": "1=+ 2=-", "pin_count": "2",
        "temp_operating_min": -40, "temp_operating_max": 125,
        "temp_storage_min": -40, "temp_storage_max": 125, "tolerance": "20%",
        "current_rating": "3A rms, 40C rise, 10% drop",
    },
    {
        "unique_id": "CoilCraft-MSS7341-103ML",
        "part_locator": "IND CoilCraft 10uH 2.8A MSS7341-103ML",
        "mpn": "MSS7341-103ML", "manufacturer": "CoilCraft", "package": "SMT",
        "value": "IND CoilCraft 10uH 2.8A MSS7341-103ML",
        "description": "Power inductor, 10 mH, 38 mOhm, 2.8A, 20% SMT 7.1x7.1 mm",
        "datasheet": "https://www.coilcraft.com/getmedia/7b464459-a4d6-47b0-83ca-9d96d4410863/MSS7341.pdf",
        "manufacturer_link": "https://www.coilcraft.com/en-us/products/power/shielded-inductors/ferrite-drum/mss-mos/mss7341/mss7341-103/",
        "kicad_symbol": "terra_sym:IND CoilCraft 10uH 2.8A MSS7341-103ML",
        "kicad_footprint": "terra_sym:Coilcraft MSS7341 Shileded power inductor",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/COLC/COLC-E-A0007342590/COLC-E-A0007342584-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "L", "sim_pins": "1=+ 2=-", "pin_count": "2",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -40, "temp_storage_max": 125, "tolerance": "30%",
        "current_rating": "2.8A rms, 20C rise, 1.64ADC, 10% ind. drop",
    },
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lines = [
        "-- Terra EDA Library - inductors harvested from terra_sym.kicad_sym",
        f"-- Native terra rows scripted from the terra_sym source. Generated by {Path(__file__).name}.",
        "-- dump_priority=0: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO inductors ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
