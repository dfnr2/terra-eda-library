#!/usr/bin/env python3
"""Emit the indicator-LED catalog harvested from terra_sym.kicad_sym as native rows.

These six LEDs were previously the optoelectronics_led_1_migrated.sql dump (generated
from terra_sym.kicad_sym). They are scripted here from that source. The curated green
Everlight 1608 LED lives in its own run_320_cart_harvest.py alongside this.

LED `value` is the color by default: the legacy dump left `color` NULL and put a long
descriptive string (or literally "LED") in `value`. Here each part carries `color`, and
main() sets `value = color` when a row does not override it -- so an LED drops onto the
schematic showing its colour.

Typos corrected (confirmed by each part's own datasheet/other fields): the APHBM2012
manufacturer "Kingsbright" -> "Kingbright" (kingbrightusa.com), and the space-wrapped
" APG1608QBC/D " mpn -> "APG1608QBC/D".

Deferred curation: every `kicad_footprint` is `terra_sym:`-prefixed (points at a symbol
library, needs a real footprint) and the HSML-A401 even borrows the ASMT-SWB5 footprint;
the APHBM2012 has no footprint at all; deep tail (forward_voltage_v, current_max_ma,
wavelength_nm, viewing_angle) is NULL pending a datasheet harvest.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("optoelectronics_led_generated_300_terra_sym_harvest.sql")

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "rohs_document_link", "allow_substitution",
    "tracking", "standards_version", "source", "dump_priority", "tier",
    "sim_device", "sim_pins", "pin_count", "temp_operating_min",
    "temp_operating_max", "temp_storage_min", "temp_storage_max",
    "temp_soldering", "color",
]

PARTS = [
    {
        "unique_id": "Broadcom-HSML-A401-U40M1",
        "part_locator": "LED Broadcom Orange, PLCC-4  HSML-A401-U40M1",
        "mpn": "HSML-A401-U40M1", "manufacturer": "Broadcom", "package": "SMT",
        "color": "Orange", "description": "Orange SMT LED , PLCC-4 SMT",
        "datasheet": "https://docs.broadcom.com/docs/HSMx-A4xx-xxxxx-SMT-Surface-Mount-LED-Indicator-DS",
        "manufacturer_link": "https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/hsml-a401-u40m1",
        "kicad_symbol": "terra_sym:LED Broadcom Orange, PLCC-4  HSML-A401-U40M1 ",
        "kicad_footprint": "terra_sym:ASMT-SWB5-NW703",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Broadcom_Limited_6305_RoHS_Certificate.pdf",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "D", "sim_pins": "1=K 2=A",
        "temp_operating_min": -40, "temp_operating_max": 100,
        "temp_storage_min": -40, "temp_storage_max": 100, "temp_soldering": 260,
    },
    {
        "unique_id": "Broadcom-ASMT-SWB5-NW703",
        "part_locator": "LED Broadcom White, PLCC-4 ASMT-SWB5-NW703",
        "mpn": "ASMT-SWB5-NW703", "manufacturer": "Broadcom", "package": "SMT",
        "color": "White", "description": "White SMT LED , PLCC-4 SMT",
        "datasheet": "https://docs.broadcom.com/docs/ASMT-SWB5-Nxxxx-DS",
        "manufacturer_link": "https://www.broadcom.com/products/leds-and-displays/surface-mount-plcc/plcc-4-leds/flat-top/asmt-swb5-nw703",
        "kicad_symbol": "terra_sym:LED Broadcom White, PLCC-4 ASMT-SWB5-NW703",
        "kicad_footprint": "terra_sym:ASMT-SWB5-NW703",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Broadcom_6305_RoHS_Certificate.pdf",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "D", "sim_pins": "1=K 2=A",
        "temp_operating_min": -40, "temp_operating_max": 100,
        "temp_storage_min": -40, "temp_storage_max": 100, "temp_soldering": 260,
    },
    {
        # FIX: manufacturer "Kingsbright" -> "Kingbright" (datasheet is kingbrightusa.com).
        "unique_id": "Kingbright-APHBM2012CGKSYKC",
        "part_locator": "LED DUAL APHBM2012CGKSYKC ",
        "mpn": "APHBM2012CGKSYKC", "manufacturer": "Kingbright", "package": "SMD",
        "color": "Green/Yellow", "description": "Dual Green/Yellow LED, SMD",
        "datasheet": "https://www.kingbrightusa.com/images/catalog/SPEC/APHBM2012CGKSYKC.pdf",
        "manufacturer_link": "https://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APHBM2012CGKSYKC",
        "kicad_symbol": "terra_sym:LED DUAL APHBM2012CGKSYKC ",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Kingbright_6040_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "D", "sim_pins": "1=K 2=A", "pin_count": "4",
        "temp_operating_min": -40, "temp_operating_max": 85,
    },
    {
        "unique_id": "Dialight-550-0205F",
        "part_locator": "LED Dialight CBI 5mm Green TH",
        "mpn": "550-0205F", "manufacturer": "Dialight", "package": "TH CBI",
        "color": "Green", "description": "CBI 1x1 5mm green LED",
        "datasheet": "https://s3-us-west-2.amazonaws.com/catsy.557/C17264.pdf",
        "manufacturer_link": "https://www.dialightsignalsandcomponents.com/550-series-cbi-5mm-1x1-g/#resources-btn",
        "kicad_symbol": "terra_sym:LED Dialight CBI 5mm Green TH",
        "kicad_footprint": "terra_sym:Dialight-550-series",
        "rohs": "Yes",
        "rohs_document_link": "https://www.dialightsignalsandcomponents.com/550-series-cbi-5mm-1x1-g/#resources-btn",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "D", "sim_pins": "1=K 2=A",
        "temp_operating_min": -40, "temp_operating_max": 100,
        "temp_storage_min": -40, "temp_storage_max": 100, "temp_soldering": 260,
    },
    {
        "unique_id": "Dialight-550-3507F",
        "part_locator": "LED Dialight CBI 5mm Green/Red Common Cath TH",
        "mpn": "550-3507F", "manufacturer": "Dialight", "package": "TH CBI",
        "color": "Green/Red",
        "description": "CBI 1x1 5mm Green/Red Commong Cathode LED",
        "datasheet": "https://s3-us-west-2.amazonaws.com/catsy.557/C17264.pdf",
        "manufacturer_link": "https://www.dialightsignalsandcomponents.com/550-series-5-mm-cbi-r-g-3-leaded-slope-back-housing/",
        "kicad_symbol": "terra_sym:LED Dialight CBI 5mm Green/Red Common Cath TH",
        "kicad_footprint": "terra_sym:Dialight-550-3x07",
        "rohs": "Yes",
        "rohs_document_link": "https://www.dialightsignalsandcomponents.com/550-series-5-mm-cbi-r-g-3-leaded-slope-back-housing/",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "D", "sim_pins": "1=K 2=A",
        "temp_operating_min": -20, "temp_operating_max": 85,
        "temp_storage_min": -55, "temp_storage_max": 100, "temp_soldering": 260,
    },
    {
        # FIX: mpn was " APG1608QBC/D " (leading+trailing spaces); trimmed. The legacy
        # `value` was literally "LED" -> now the colour (Blue) via the value=color rule.
        "unique_id": "Kingbright-APG1608QBC/D",
        "part_locator": "LED Kingbright Blue  SMT 1608  APG1608QBC/D",
        "mpn": "APG1608QBC/D", "manufacturer": "Kingbright", "package": "1608",
        "color": "Blue", "description": "Blue LED  SMT 1608  20mA",
        "datasheet": "https://www.kingbrightusa.com/images/catalog/SPEC/APG1608QBC-D.pdf",
        "manufacturer_link": "http://www.kingbrightusa.com/product.asp?catalog_name=LED&product_id=APG1608QBC/D",
        "kicad_symbol": "terra_sym:LED Kingbright Blue  SMT 1608  APG1608QBC/D",
        "kicad_footprint": "terra_sym:LED_0603_1608Metric",
        "rohs": "Yes",
        "rohs_document_link": "https://www.mouser.com/catalog/additional/Kingbright_6040_RoHS_Certificate.pdf",
        "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.1",
        "source": "terra_sym", "dump_priority": 0, "tier": 2,
        "sim_device": "D", "sim_pins": "1=K 2=A",
        "temp_operating_min": -40, "temp_operating_max": 85,
        "temp_storage_min": -40, "temp_storage_max": 85, "temp_soldering": 260,
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
        "-- Terra EDA Library - indicator LEDs harvested from terra_sym.kicad_sym",
        f"-- Native terra rows scripted from the terra_sym source. Generated by {Path(__file__).name}.",
        "-- LED value defaults to the colour. dump_priority=0: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for p in PARTS:
        # value defaults to the part's colour unless explicitly overridden.
        p = {**p, "value": p.get("value") or p["color"]}
        vals = ", ".join(sql(p.get(c)) for c in COLS)
        lines.append(f"INSERT INTO optoelectronics_led ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
