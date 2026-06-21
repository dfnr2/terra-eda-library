#!/usr/bin/env python3
"""Emit the mosfet catalog harvested from terra_sym.kicad_sym as native rows.

These three parts were recovered from the terra_sym.kicad_sym source. They are
scripted here so a schema change reapplies by rebuild and one parameter set lives
per part. This is a faithful port: every field -- URLs and the `terra_sym:`-prefixed
kicad_symbol/kicad_footprint references -- is carried verbatim with no corrections.

Deferred curation: DMP3099L `rohs_document_link` is still the placeholder 'RoHs
Link'; the IRLM2502TRPBF row likely should be IRLML2502TRPBF (its value says
'IRLML2502') and its description ("N Channel MOSFET, 30V 3.8A") looks copy-pasted
from DMP3099L while its real specs are v_ce_ds_max 20V / i_c_d_max 4.2A; BTS5030
has NULL transistor_type/sim_device (it is a smart high-side PROFET switch, not a
plain MOSFET); the deep tail (rds_on, vgs_th, power_dissipation) needs a datasheet
harvest.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("mosfet_generated_300_terra_sym_harvest.sql")

IHS_INFN = "https://4donline.ihs.com/images/VipMasterIC/IC/INFN/INFN-E-A0005477335/INFN-E-A0005477335-1.pdf?hkey=6D0214268300F1406B835FE51CB13195"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution",
    "tracking", "standards_version", "source", "dump_priority", "tier",
    "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "v_ce_ds_max", "i_c_d_max", "sim_device",
]

PARTS = [
    {
        "unique_id": "Infineon-BTS5030-1EJA",
        "part_locator": "IC_SSR Infineon BTS5030-1EJA MOSFET high-side switch 30 mOhm 5A 28V DSO-8",
        "mpn": "BTS5030-1EJA", "manufacturer": "Infineon", "package": "DSO-8-EP",
        "value": "BTS5030",
        "description": "Smart High-Side Power Switch, PROFET, Single, 30mOhm, 5A, 28V, DSO-8",
        "datasheet": "https://www.infineon.com/dgdl/Infineon-BTS5030-1EJA-DS-v02_20-EN.pdf?fileId=5546d46259d9a4bf015a84f3e686758a",
        "manufacturer_link": "https://www.infineon.com/cms/en/product/power/smart-power-switches/high-side-switches/profet-plus-12v-automotive-smart-high-side-switch/bts5030-1eja/",
        "kicad_symbol": "terra_sym:IC_SSR Infineon BTS5030-1EJA MOSFET high-side switch 30 mOhm 5A 28V DSO-8",
        "kicad_footprint": "Package_SO:Infineon_PG-DSO-8-43",
        "rohs": "Yes", "rohs_document_link": IHS_INFN,
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "9",
        "temp_operating_min": -40, "temp_operating_max": 150,
        "temp_storage_min": -55, "temp_storage_max": 150,
        "v_ce_ds_max": "28V", "i_c_d_max": "5A", "sim_device": None,
    },
    {
        "unique_id": "Diodes, Inc.-DMP3099L",
        "part_locator": "MOSFET DMP3099L P-channel 30V 3.8A", "mpn": "DMP3099L",
        "manufacturer": "Diodes, Inc.", "package": "SOT-23", "value": "DMP3099L-7",
        "description": "P Channel MOSFET, 30V 3.8A SOT-23",
        "datasheet": "https://www.diodes.com/assets/Datasheets/DMP3099L.pdf",
        "manufacturer_link": "https://www.diodes.com/part/view/DMP3099L",
        "kicad_symbol": "terra_sym:MOSFET DMP3099L P-channel 30V 3.8A",
        "kicad_footprint": "Package_TO_SOT_SMD:SOT-23",
        "rohs": "Yes", "rohs_document_link": "RoHs Link",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "3",
        "temp_operating_min": -55, "temp_operating_max": 150,
        "temp_storage_min": -55, "temp_storage_max": 150,
        "v_ce_ds_max": "30V", "i_c_d_max": "3.8A", "sim_device": "PMOS",
    },
    {
        "unique_id": "Infineon-IRLM2502TRPBF",
        "part_locator": "MOSFET Infineon IRLM2502 N-channel 4.2A 20V",
        "mpn": "IRLM2502TRPBF", "manufacturer": "Infineon", "package": "SOT-23",
        "value": "IRLML2502",
        "description": "N Channel MOSFET, 30V 3.8A SOT-23",
        "datasheet": "https://www.infineon.com/dgdl/Infineon-IRLML2502-DataSheet-v01_01-EN.pdf?fileId=5546d462533600a401535668048e2606",
        "manufacturer_link": "https://www.infineon.com/cms/en/product/power/mosfet/n-channel/irlml2502/",
        "kicad_symbol": "terra_sym:MOSFET Infineon IRLM2502 N-channel 4.2A 20V",
        "kicad_footprint": "Package_TO_SOT_SMD:SOT-23",
        "rohs": "Yes", "rohs_document_link": IHS_INFN,
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "3",
        "temp_operating_min": -55, "temp_operating_max": 150,
        "temp_storage_min": -55, "temp_storage_max": 150,
        "v_ce_ds_max": "20V", "i_c_d_max": "4.2A", "sim_device": "NMOS",
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
        "-- Terra EDA Library - mosfet harvested from terra_sym.kicad_sym",
        f"-- Native terra rows scripted from the terra_sym source. Generated by {Path(__file__).name}.",
        "-- dump_priority=0: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO mosfet ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
