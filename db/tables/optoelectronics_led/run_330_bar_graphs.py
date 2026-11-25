#!/usr/bin/env python3
"""10-segment DIP LED bar-graph arrays: Broadcom HDSP-48xx / HLCP-J100 and the
Kingbright DC10 series.

Sources (parked under datasheets/):
  - broadcom/hdsp-48xx-hlcp-j100.pdf -- Broadcom AV02-1798EN (July 8, 2024), covering
    HDSP-4830/4840/4850/4832/4836 and HLCP-J100. The older HDSP-4820 is not in it and
    is not emitted.
  - kingbright/dc10*.pdf -- Kingbright USA per-part spec sheets (DSAD1426 etc.,
    Rev V.4A-V.10A, 2020; DC10GWA V.9A, 2013).

Pinout: every part here is ten independent LEDs, anode pins 1-10 and cathode pins
20-11 (segment n: anode n, cathode 21-n), checked against each data sheet's internal
circuit diagram. KiCad's stock LED library has per-part HDSP-48xx/HLCP-J100 symbols
(10 units, unit n = A pin n / K pin 21-n) that match, so no custom symbol is drawn:
Broadcom parts use their own stock symbol, Kingbright DC10 parts use LED:HDSP-4830
(same pinout; the symbol carries no colour).

Footprints: Broadcom parts use their stock Display:HDSP-48xx / HLCP-J100 footprints
(25.4 x 10.16 mm body, 2.54 mm pitch, 7.62 mm row spacing, with 3D models).
Kingbright DC10: same 25.4 x 10.16 mm body and 2.54 mm pitch, but the data sheet gives
7.5 mm (0.295") row spacing and recommends 1.0 mm holes. Display:HDSP-48xx (7.62 mm
rows, 0.914 mm drill) is used as the closest stock footprint -- the 0.12 mm row
difference is absorbed by lead spring; swap in an exact footprint via DC10_FOOTPRINT
if one is made.

Not emitted: the Kingbright bi-colour DC10EGWA and DC10SURKCGKWA. They are 30-pin
three-row parts (red anodes 20-11, green anodes 1-10, common cathodes 21-30) with no
stock symbol or footprint; see plans/led-display-drivers-bar-graphs.md.

Luminous intensity: typical per-segment figure at the data sheet's test current.
Kingbright sheets give two scales (legacy and CIE127-2007 traceable, marked "*");
the legacy figure is used, matching distributor listings (e.g. DC10EWA 9 mcd).

sim_device / sim_pins are set NULL: the table default ('D', '1=K 2=A') describes a
two-pin LED and would be wrong for a 20-pin array.

Lifecycle (checked 2026-11-25 at Digi-Key): HDSP-4830/4832/4836/4840/4850 and
HLCP-J100 Active; DC10CGKWA, DC10EWA, DC10GWA, DC10SURKWA, DC10SYKWA, DC10YWA Active.
(DC10SRWA is Obsolete at Digi-Key and has no current sheet; not emitted.)

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("optoelectronics_led_generated_330_bar_graphs.sql")

DC10_FOOTPRINT = "Display:HDSP-48xx"
DC10_SYMBOL = "LED:HDSP-4830"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "sim_device", "sim_pins",
    "temp_operating_min", "temp_operating_max", "temp_storage_min", "temp_storage_max",
    "color", "wavelength_nm", "luminous_intensity",
    "forward_voltage_v", "current_max_ma", "viewing_angle",
]

# Broadcom AV02-1798EN. Single-colour rows: (colour, dominant nm, Vf typ @ its test
# current (the sheet tests HLCP-J100 at 20 mA despite its 15 mA DC rating), DC If max, Iv typ @ test current, op min, op max, storage min, max).
BCM_COLOURS = {
    "HLCP-J100": ("Deep Red", "639", "2.1 V @20mA", "15 mA", "1.0 mcd @1mA", -20, 100, -55, 100),
    "HDSP-4830": ("Red", "622", "2.05 V @20mA", "30 mA", "8.4 mcd @10mA", -40, 85, -40, 85),
    "HDSP-4840": ("Yellow", "588", "2.0 V @20mA", "20 mA", "4.9 mcd @10mA", -40, 85, -40, 85),
    "HDSP-4850": ("Green", "571", "2.1 V @10mA", "30 mA", "10.2 mcd @10mA", -20, 85, -40, 85),
}
# Multicolour arrays: segment colours a..j from the data sheet table; the red,
# yellow and green elements are specified as the HDSP-4830/4840/4850.
BCM_MULTI = {
    "HDSP-4832": "a-c red, d-g yellow, h-j green",
    "HDSP-4836": "a-b red, c-d yellow, e-f green, g-h yellow, i-j red",
}
BCM_MATERIAL = {"HLCP-J100": "AlInGaP deep red", "HDSP-4830": "AlInGaP red",
                "HDSP-4840": "AlInGaP yellow", "HDSP-4850": "AlInGaP green"}

# Kingbright DC10 single-colour parts: (mpn, colour, material, dominant nm, Vf typ,
# Vf test current, DC If max, Iv typ mcd @10mA).
DC10 = [
    ("DC10EWA", "Red", "high-efficiency red GaAsP/GaP", "617", "1.9 V", "10mA", "30 mA", "9"),
    ("DC10SURKWA", "Red", "hyper red AlGaInP", "630", "1.85 V", "10mA", "30 mA", "100"),
    ("DC10YWA", "Yellow", "yellow GaAsP/GaP", "588", "1.95 V", "10mA", "30 mA", "9"),
    ("DC10SYKWA", "Yellow", "super bright yellow AlGaInP", "590", "1.95 V", "10mA", "30 mA", "65"),
    ("DC10GWA", "Green", "green GaP", "568", "2.2 V", "20mA", "25 mA", "12"),
    ("DC10CGKWA", "Green", "green AlGaInP", "570", "2.0 V", "10mA", "30 mA", "28"),
]

COMMON = {
    "package": "DIP-20 bar graph", "rohs": "Yes", "allow_substitution": "No",
    "tracking": "No", "source": None, "dump_priority": 0, "tier": 2,
    "pin_count": "20", "sim_device": None, "sim_pins": None,
    "lifecycle_status": "Active", "viewing_angle": None,
}


def broadcom():
    ds = "${TERRA_EDA_LIB}/datasheets/broadcom/hdsp-48xx-hlcp-j100.pdf"
    for mpn, (col, wl, vf, imax, iv, omin, omax, smin, smax) in BCM_COLOURS.items():
        yield {
            **COMMON,
            "unique_id": f"Broadcom-{mpn}", "mpn": mpn, "manufacturer": "Broadcom",
            "part_locator": f"led-bargraph-10seg-{col.lower().replace(' ', '-')}-dip20",
            "value": mpn,
            "description": (f"Broadcom {mpn} 10-element LED bar graph array, "
                            f"{BCM_MATERIAL[mpn]} {wl}nm, end stackable, DIP-20"),
            "datasheet": ds,
            "manufacturer_link": "https://www.broadcom.com/products/leds-and-displays/"
                                 "displays/bar-graph-arrays",
            "kicad_symbol": f"LED:{mpn}", "kicad_footprint": f"Display:{mpn}",
            "keywords": f"LED, bar graph, 10 segment, array, {col.lower()}, {mpn}",
            "temp_operating_min": omin, "temp_operating_max": omax,
            "temp_storage_min": smin, "temp_storage_max": smax,
            "color": col, "wavelength_nm": wl, "luminous_intensity": iv,
            "forward_voltage_v": vf, "current_max_ma": imax,
        }
    r, y, g = (BCM_COLOURS[m] for m in ("HDSP-4830", "HDSP-4840", "HDSP-4850"))
    for mpn, layout in BCM_MULTI.items():
        yield {
            **COMMON,
            "unique_id": f"Broadcom-{mpn}", "mpn": mpn, "manufacturer": "Broadcom",
            "part_locator": "led-bargraph-10seg-red-yellow-green-dip20",
            "value": mpn,
            "description": (f"Broadcom {mpn} 10-element multicolour LED bar graph array "
                            f"({layout}), AlInGaP, DIP-20"),
            "datasheet": ds,
            "manufacturer_link": "https://www.broadcom.com/products/leds-and-displays/"
                                 "displays/bar-graph-arrays",
            "kicad_symbol": f"LED:{mpn}", "kicad_footprint": f"Display:{mpn}",
            "keywords": f"LED, bar graph, 10 segment, array, multicolor, red, yellow, green, {mpn}",
            # Intersection of the three element ratings.
            "temp_operating_min": -20, "temp_operating_max": 85,
            "temp_storage_min": -40, "temp_storage_max": 85,
            "color": "Red/Yellow/Green", "wavelength_nm": f"{r[1]}/{y[1]}/{g[1]}",
            "luminous_intensity": "8.4/4.9/10.2 mcd @10mA",
            "forward_voltage_v": "2.05/2.0/2.1 V @20/20/10mA", "current_max_ma": "30/20/30 mA",
        }


def kingbright():
    for mpn, col, material, wl, vf, vf_at, imax, iv in DC10:
        yield {
            **COMMON,
            "unique_id": f"Kingbright-{mpn}", "mpn": mpn, "manufacturer": "Kingbright",
            "part_locator": f"led-bargraph-10seg-{col.lower()}-dip20",
            "value": mpn,
            "description": (f"Kingbright {mpn} 10-segment LED bar graph array, {material} "
                            f"{wl}nm, gray face / white segments, end stackable, DIP-20"),
            "datasheet": f"${{TERRA_EDA_LIB}}/datasheets/kingbright/{mpn.lower()}.pdf",
            "manufacturer_link": ("https://www.kingbrightusa.com/category.asp?catalog_name=LED"
                                  "&category_name=KCBar+Graph+Array&Page=1"),
            "kicad_symbol": DC10_SYMBOL, "kicad_footprint": DC10_FOOTPRINT,
            "keywords": (f"LED, bar graph, 10 segment, array, {col.lower()}, {mpn}, "
                         f"DC-10{mpn[4:]}"),
            "temp_operating_min": -40, "temp_operating_max": 85,
            "temp_storage_min": -40, "temp_storage_max": 85,
            "color": col, "wavelength_nm": wl, "luminous_intensity": f"{iv} mcd @10mA",
            "forward_voltage_v": f"{vf} @{vf_at}", "current_max_ma": imax,
        }


def records():
    yield from broadcom()
    yield from kingbright()


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
    for r in recs:  # Kingbright suffix encodes the colour: E/SURK red, Y/SYK yellow, G/CGK green
        if r["manufacturer"] == "Kingbright":
            code = r["mpn"][4:-2]
            want = {"E": "Red", "SURK": "Red", "Y": "Yellow", "SYK": "Yellow",
                    "G": "Green", "CGK": "Green"}[code]
            assert r["color"] == want, r["mpn"]
    lines = [
        "-- Terra EDA Library - optoelectronics_led 10-segment DIP bar graph arrays",
        f"-- Generated by {Path(__file__).name}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO optoelectronics_led ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} parts")


if __name__ == "__main__":
    main()
