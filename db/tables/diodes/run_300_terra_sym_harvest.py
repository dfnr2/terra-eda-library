#!/usr/bin/env python3
"""Emit the diodes catalog harvested from terra_sym.kicad_sym as native rows.

These eight 2-terminal diodes were recovered from the terra_sym source. They are
scripted here so a schema change reapplies by rebuild. The recovered rows carried
dump_priority=100 and no tier; both are overridden here to the native convention
(dump_priority=0, tier=2). Field values are otherwise ported faithfully -- URLs,
symbol/footprint strings (including any `terra_sym:` prefix, double spaces, and
trailing spaces) are preserved verbatim.

Deferred curation:
  - ROHM RFN10TB4SNZC9: its datasheet field is a bare MPN 'RFN10TB4SNZC9' (broken,
    needs a real URL); its description says "Vf 430V" which is actually Vr, not Vf.
    (Its `value` was a leftover template string and has been replaced with the MPN.)
  - The `terra_sym:`-prefixed footprints (PNE20020ER's "terra_sym:Nexperia SOD-123W",
    VSSAF510 and VSSAF512's "terra_sym:Vishay_SlimSMA_D_DO-221AC") point at a symbol
    library and need real footprints.
  - Deep tail params (diode_type / forward_voltage / forward_current) are sparse and
    need a datasheet harvest.
  - A ninth recovered row, 'Unknown-UNKNOWN', is a mis-identified Nexperia
    PESD3V3L4UW ESD array (not a 2-terminal diode); it is excluded here and should be
    re-homed to diodes_tvs as Nexperia PESD3V3L4UW.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("diodes_generated_300_terra_sym_harvest.sql")

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution",
    "tracking", "standards_version", "source", "dump_priority", "tier",
    "pin_count", "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "diode_type", "voltage_rating", "forward_voltage",
    "forward_current", "current_rating", "power_rating",
]

PARTS = [
    {
        "unique_id": "Diodes, Inc.-MMBD914-7-F",
        "part_locator": "DIODE MMBD914 small signal switching diode SMT SOT23",
        "mpn": "MMBD914-7-F", "manufacturer": "Diodes, Inc.", "package": "SOT23",
        "value": "MMBD914",
        "description": "DIODE SMT/TH 1n914/mmbd914 generic switching",
        "datasheet": "https://www.diodes.com/assets/Datasheets/BAS16_MMBD4148_MMBD914.pdf",
        "manufacturer_link": "https://www.diodes.com/part/view/MMBD914",
        "kicad_symbol": "terra_sym:DIODE MMBD914 small signal switching diode SMT SOT23",
        "kicad_footprint": "Package_TO_SOT_SMD:SOT-23",
        "rohs": "Yes",
        "rohs_document_link": "https://www.diodes.com/assets/Quality-Reliability-Docs/Master_CofC.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "3",
        "temp_operating_min": -65, "temp_operating_max": 150,
        "power_rating": "350 mW / 200 mA",
    },
    {
        "unique_id": "Nexperia-PNE20020ER",
        "part_locator": "DIODE Nexperia PNE20020ERX 200V 2.8A Fast Recovery SOD123",
        "mpn": "PNE20020ER", "manufacturer": "Nexperia", "package": "SOD123W",
        "value": "200V 2A",
        "description": "200V hyperfast recovery rectifier, Vf 0.98V @ 2A, Iav 2A, trr 25ns",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/nexperia/pne20020er.pdf",
        "manufacturer_link": "https://www.nexperia.com/products/diodes/recovery-rectifiers/PNE20020ER.html",
        "kicad_symbol": "terra_sym:DIODE Nexperia PNE20020ERX 200V 2.8A Fast Recovery SOD123",
        "kicad_footprint": "terra_sym:Nexperia SOD-123W",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/RECT/RECT-E-A0007327236/RECT-E-A0007327236-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "2",
        "temp_operating_min": -55, "temp_operating_max": 175,
        "temp_storage_min": -65, "temp_storage_max": 175,
        "current_rating": "2A", "diode_type": "rectifier", "voltage_rating": "200V",
        "forward_voltage": "0.98V", "forward_current": "2.8A",
    },
    {
        "unique_id": "OnSemi-MBR0530T1G",
        "part_locator": "DIODE OnSemi Schottky 30V 0.5A SOD-123 MBR0530",
        "mpn": "MBR0530T1G", "manufacturer": "OnSemi", "package": "SOD-123",
        "value": "DIODE OnSemi Schottky 30V 0.5A SOD-123 MBR0530",
        "description": "30V 0.5A Schottky Power Rectifier Diode",
        "datasheet": "https://www.onsemi.com/pdf/datasheet/mbr0530t1-d.pdf",
        "manufacturer_link": "https://www.onsemi.com/products/discrete-power-modules/schottky-diodes-schottky-rectifiers/mbr0530",
        "kicad_symbol": "terra_sym:DIODE OnSemi Schottky 30V 0.5A SOD-123 MBR0530",
        "kicad_footprint": "Diode_SMD:D_SOD-123",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/On_Semiconductor_5121_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "temp_operating_min": -65, "temp_operating_max": 125,
        "temp_storage_min": -65, "temp_storage_max": 150, "diode_type": "schottky",
    },
    {
        # EDIT: `value` was a leftover template
        # '_TEMPLATE MANUF [VALUE] [PARAMS] [PKG] [MPN]' -> replaced with the MPN.
        "unique_id": "ROHM-RFN10TB4SNZC9",
        "part_locator": "DIODE ROHM RFN10TB4SNZC9 430V 10A",
        "mpn": "RFN10TB4SNZC9", "manufacturer": "ROHM", "package": "TO-220FN-2",
        "value": "RFN10TB4SNZC9",
        "description": "General-purpose fast-recovery rectifier, Vr 430V, Vf 1.55V @ 10A, Iav 10A, trr 30ns",
        "datasheet": "${TERRA_EDA_LIB}/datasheets/rohm/rfn10tb4snz.pdf",
        "manufacturer_link": "https://www.rohm.com/products/diodes/fast-recovery-diodes/standard/rfn10tb4snz-product",
        "kicad_symbol": "terra_sym:DIODE ROHM RFN10TB4SNZC9 430V 10A",
        "kicad_footprint": "Package_TO_SOT_THT:TO-220-2_Vertical",
        "rohs": "Yes",
        "rohs_document_link": "https://fscdn.rohm.com/en/techdata_basic/diode/rohs-elv/ROHS_ELV_Diode-e.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "2",
        "temp_operating_max": 150, "temp_storage_min": -55, "temp_storage_max": 150,
        "diode_type": "rectifier", "voltage_rating": "430V", "forward_voltage": "1.55V",
        "forward_current": "10A", "current_rating": "10A",
    },
    {
        "unique_id": "Rectron-FR204-B",
        "part_locator": "DIODE Rectron  FR204-B 400V 2A Fast Recovery",
        "mpn": "FR204-B", "manufacturer": "Rectron", "package": "DO-15",
        "value": "400V 2A",
        "description": "General Purpose DIode, fast recovery, Vf 400V, Iav 2A",
        "datasheet": "https://www.rectron.com/public/product_datasheets/fr201-fr207.pdf",
        "manufacturer_link": "https://www.rectron.com/category/4/50",
        "kicad_symbol": "terra_sym:DIODE Rectron  FR204-B 400V 2A Fast Recovery",
        "kicad_footprint": "Diode_THT:D_DO-15_P10.16mm_Horizontal",
        "rohs": "Yes",
        "rohs_document_link": "https://4donline.ihs.com/images/VipMasterIC/IC/RECT/RECT-E-A0007327236/RECT-E-A0007327236-1.pdf?hkey=6D0214268300F1406B835FE51CB13195",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2, "pin_count": "2",
        "temp_operating_min": -55, "temp_operating_max": 150,
        "temp_storage_min": -55, "temp_storage_max": 150, "current_rating": "2A",
        "diode_type": "fast-recovery", "voltage_rating": "400V",
        "forward_voltage": "1.3V", "forward_current": "2A",
    },
    {
        "unique_id": "Vishay-VSSAF510-M3/H",
        "part_locator": "DIODE Vishay VSSAF510  Schottky 5A",
        "mpn": "VSSAF510-M3/H", "manufacturer": "Vishay", "package": "SMA (DO-214AC)",
        "value": "VSSAF510",
        "description": "100V 5A Schottky Power Rectifier Diode",
        "datasheet": "https://www.vishay.com/docs/87610/vssaf510.pdf",
        "manufacturer_link": "https://www.vishay.com/en/product/87610/",
        "kicad_symbol": "terra_sym:DIODE Vishay VSSAF510  Schottky 5A",
        "kicad_footprint": "terra_sym:Vishay_SlimSMA_D_DO-221AC",
        "rohs": "Yes",
        "rohs_document_link": "https://www.vishay.com/en/how/leadfree/#summary",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "temp_operating_min": -65, "temp_operating_max": 150,
        "temp_storage_min": -65, "temp_storage_max": 150, "diode_type": "schottky",
        "voltage_rating": "100V", "forward_voltage": "0.75V",
        "forward_current": "5A", "current_rating": "5A",
    },
    {
        "unique_id": "Vishay-VSSAF512",
        "part_locator": "DIODE Vishay VSSAF512  Schottky 5A",
        "mpn": "VSSAF512", "manufacturer": "Vishay", "package": "SMA (DO-214AC)",
        "value": "VSSAF512",
        "description": "120V 5A Schottky Power Rectifier Diode",
        "datasheet": "https://www.vishay.com/docs/87611/vssaf512.pdf",
        "manufacturer_link": "https://www.vishay.com/en/product/87611/",
        "kicad_symbol": "terra_sym:DIODE Vishay VSSAF512  Schottky 5A",
        "kicad_footprint": "terra_sym:Vishay_SlimSMA_D_DO-221AC",
        "rohs": "Yes",
        "rohs_document_link": "https://www.vishay.com/en/how/leadfree/#summary",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "temp_operating_min": -65, "temp_operating_max": 150,
        "temp_storage_min": -65, "temp_storage_max": 150, "diode_type": "schottky",
        "voltage_rating": "120V", "forward_voltage": "0.88V",
        "forward_current": "5A", "current_rating": "5A",
    },
    {
        "unique_id": "Vishay-VSSB410S",
        "part_locator": "DIODE Vishay VSSB410S Schottky 4A",
        "mpn": "VSSB410S", "manufacturer": "Vishay", "package": "SMB (DO-214AA)",
        "value": "VSSB410S",
        "description": "100V 4A Schottky Power Rectifier Diode",
        "datasheet": "https://www.vishay.com/docs/89140/vssb410s-e3.pdf",
        "manufacturer_link": "https://www.vishay.com/en/product/89140/",
        "kicad_symbol": "terra_sym:DIODE Vishay VSSB410S Schottky 4A",
        "kicad_footprint": "Diode_SMD:D_SMB",
        "rohs": "Yes",
        "rohs_document_link": "https://www.vishay.com/en/how/leadfree/#summary",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "temp_operating_min": -65, "temp_operating_max": 150,
        "temp_storage_min": -65, "temp_storage_max": 150, "diode_type": "schottky",
        "voltage_rating": "100V", "forward_voltage": "0.77V", "forward_current": "4A",
        "current_rating": "4A",
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
        "-- Terra EDA Library - diodes harvested from terra_sym.kicad_sym",
        f"-- Native terra rows scripted from the terra_sym source. Generated by {Path(__file__).name}.",
        "-- dump_priority=0: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO diodes ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
