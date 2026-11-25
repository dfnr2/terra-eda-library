#!/usr/bin/env python3
"""LED display drivers: TI LM3914/15/16 dot/bar, ADI (Maxim) MAX7219/MAX7221 and
Renesas (Intersil) ICM7218A-D 8-digit multiplexed 7-segment drivers.

Sources (all parked under datasheets/):
  - ti/lm3914.pdf -- TI SNVS761B (Mar 2013), package addendum dated 23-Dec-2025.
  - ti/lm3915.pdf -- National DS005104 (2004); TI no longer hosts an LM3915 sheet.
  - ti/lm3916.pdf -- TI SNVS762B (Mar 2013).
  - maxim/max7219-max7221.pdf -- Maxim 19-4452 Rev 6 (8/21).
  - renesas/icm7218.pdf -- Renesas FN3159 Rev 4.00 (May 2016).

Field interpretation for display drivers (the led_drivers tail was written for
switching/linear current drivers):
  - driver_topology = 'linear': all outputs are linear current sources/sinks.
  - channels = number of LEDs the part can address on its own: 10 for the LM391x
    (one output per LED), 64 for the 8-digit x 8-segment (7 + DP) multiplexed
    MAX72xx and ICM7218. The digit/segment split is in the description.
  - output_current = LED current per output. LM391x: the programmable range. MAX72xx
    and ICM7218: typical peak segment current, with the digit-driver figure after it.
  - output_voltage_max = 'Voltage on Output Drivers' abs max (LM391x only; the other
    sheets give no separate output rating).
  - switching_freq = the multiplex scan rate (typ) for the scanned parts.
  - dimming_method: LM391x 'analog' (reference current sets LED current); MAX72xx
    'pwm' (16-step digital intensity register, plus RSET); ICM7218 'none'.
  - interface: 'none' (analog input) / 'spi' / 'parallel'.

Lifecycle (checked 2026-11-25):
  - LM3914/15/16: Obsolete. TI's LM3914 product page is OBSOLETE and the 2025
    addendum lists only LM3914VX/NOPB (Obsolete); Digi-Key lists LM3914N-1 as
    Obsolete. TI has removed the LM3915/LM3916 product pages; RS/Digi-Key list
    LM3915N-1/NOPB as discontinued. Kept as obsolete classics. LM3914V (PLCC-20) is
    not emitted: only wanted if active, and it is obsolete.
  - MAX7219/MAX7221: Active (Digi-Key: all six MAX7221 codes and MAX7219EWG+ Active;
    MAX7219CNG+/CWG+/ENG+ listed and priced at Digi-Key, Production per ADI via
    Octopart/Arrow). The ERG (CERDIP) codes in the ordering table are dropped: the
    Rev 6 package section only has PDIP N24+1 and SOIC W24+1.
  - ICM7218: per renesas.com part pages, ICM7218BIJI Active; AIJI, CIJI, DIJI
    Obsolete. The R5254 ordering variants are not emitted.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("led_drivers_generated_320_display_drivers.sql")
SYMLIB = "terra_symbols_led_drivers"

DIP18 = "Package_DIP:DIP-18_W7.62mm"
DIP24 = "Package_DIP:DIP-24_W7.62mm"
SO24W = "Package_SO:SOIC-24W_7.5x15.4mm_P1.27mm"
DIP28W = "Package_DIP:DIP-28_W15.24mm"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "pin_count", "keywords",
    "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "driver_topology", "channels", "output_current",
    "supply_voltage_min", "supply_voltage_max", "output_voltage_max",
    "switching_freq", "dimming_method", "interface", "current_accuracy",
]

COMMON = {
    "allow_substitution": "No", "tracking": "No", "source": None,
    "dump_priority": 0, "tier": 2, "driver_topology": "linear",
}

# --- TI LM3914 / LM3915 / LM3916 (identical 18-pin pinout; stock Driver_LED:LM3914N
# matches the data-sheet connection diagram pin for pin) ---------------------------
# base, scale, data sheet, output current range, supply max, keywords
LM391X = [
    ("LM3914", "linear 10-step", "lm3914", "2-30mA", 20.0,
     "LED driver, dot, bar graph, linear, analog meter, LM3914"),
    ("LM3915", "logarithmic 3dB/step", "lm3915", "1-30mA", 25.0,
     "LED driver, dot, bar graph, logarithmic, dB, audio level, LM3915"),
    ("LM3916", "VU-scale", "lm3916", "1-30mA", 25.0,
     "LED driver, dot, bar graph, VU meter, audio level, LM3916"),
]


SCALE_SLUG = {"LM3914": "linear", "LM3915": "log", "LM3916": "vu"}


def lm391x():
    for base, scale, ds, iout, vmax, kw in LM391X:
        mpn = f"{base}N-1/NOPB"
        yield {
            **COMMON,
            "unique_id": f"Texas Instruments-{mpn}",
            "part_locator": f"led-driver-dot-bar-10ch-{SCALE_SLUG[base]}-dip18",
            "mpn": mpn, "manufacturer": "Texas Instruments", "package": "PDIP-18",
            "value": f"{base}N-1",
            "description": (
                f"TI {base} dot/bar display driver, {scale}, 10 current-regulated "
                f"open-collector LED outputs ({iout}), internal reference, "
                f"3-{vmax:g}V, PDIP-18"),
            "datasheet": f"${{TERRA_EDA_LIB}}/datasheets/ti/{ds}.pdf",
            "manufacturer_link": f"https://www.ti.com/product/{base}",
            "kicad_symbol": "Driver_LED:LM3914N", "kicad_footprint": DIP18,
            "lifecycle_status": "Obsolete", "rohs": "Yes", "pin_count": "18",
            "keywords": kw,
            "temp_operating_min": 0, "temp_operating_max": 70,
            "temp_storage_min": -55, "temp_storage_max": 150,
            "channels": 10, "output_current": iout,
            "supply_voltage_min": 3.0, "supply_voltage_max": vmax,
            "output_voltage_max": "25V", "switching_freq": None,
            "dimming_method": "analog", "interface": "none",
            "current_accuracy": None,
        }


# --- ADI (Maxim) MAX7219 / MAX7221 ----------------------------------------------
# Ordering codes from the Rev 6 ordering table, "+" = lead-free. Stock symbols:
# Driver_LED:MAX7219 (DIP/SO, LOAD pin 12) and MAX7221xNG / MAX7221xWG (~CS pin 12,
# open-collector digit / open-emitter segment pins); all checked against the
# data-sheet pin configuration.
MAX72XX = [
    # mpn, temp grade, package, footprint, symbol
    ("MAX7219CNG+", "C", "PDIP-24", DIP24, "Driver_LED:MAX7219"),
    ("MAX7219CWG+", "C", "SOIC-24W", SO24W, "Driver_LED:MAX7219"),
    ("MAX7219ENG+", "E", "PDIP-24", DIP24, "Driver_LED:MAX7219"),
    ("MAX7219EWG+", "E", "SOIC-24W", SO24W, "Driver_LED:MAX7219"),
    ("MAX7221CNG+", "C", "PDIP-24", DIP24, "Driver_LED:MAX7221xNG"),
    ("MAX7221CWG+", "C", "SOIC-24W", SO24W, "Driver_LED:MAX7221xWG"),
    ("MAX7221ENG+", "E", "PDIP-24", DIP24, "Driver_LED:MAX7221xNG"),
    ("MAX7221EWG+", "E", "SOIC-24W", SO24W, "Driver_LED:MAX7221xWG"),
]
TEMP = {"C": (0, 70), "E": (-40, 85)}


def max72xx():
    for mpn, grade, pkg, fp, sym in MAX72XX:
        base = mpn[:7]
        lo, hi = TEMP[grade]
        is21 = base == "MAX7221"
        iface = ("SPI/QSPI/MICROWIRE, slew-limited segments" if is21
                 else "4-wire serial (LOAD latch)")
        yield {
            **COMMON,
            "unique_id": f"Analog Devices-{mpn}",
            "part_locator": f"led-driver-7seg-8digit-serial-{pkg.lower()}",
            "mpn": mpn, "manufacturer": "Analog Devices", "package": pkg,
            "value": base,
            "description": (
                f"Maxim {base} serially interfaced 8-digit common-cathode LED display "
                f"driver, 8 digits x 8 segments (64 LEDs), {iface}, Code-B decode, "
                f"40mA segments, 4.0-5.5V, {lo}..{hi}C, {pkg}"),
            "datasheet": "${TERRA_EDA_LIB}/datasheets/maxim/max7219-max7221.pdf",
            "manufacturer_link": f"https://www.analog.com/en/products/{base.lower()}.html",
            "kicad_symbol": sym, "kicad_footprint": fp,
            "lifecycle_status": "Active", "rohs": "Yes", "pin_count": "24",
            "keywords": ("LED display driver, 7-segment, 8-digit, matrix, bar graph, "
                         f"multiplexed, serial, SPI, common cathode, {base}"),
            "temp_operating_min": lo, "temp_operating_max": hi,
            "temp_storage_min": -65, "temp_storage_max": 160,
            "channels": 64, "output_current": "40mA seg / 320mA digit sink",
            "supply_voltage_min": 4.0, "supply_voltage_max": 5.5,
            "output_voltage_max": None, "switching_freq": "800Hz",
            "dimming_method": "pwm", "interface": "spi",
            "current_accuracy": "3%",
        }


# --- Renesas (Intersil) ICM7218A-D ----------------------------------------------
# Custom symbols drawn from db/tables/led_drivers/_pinouts.py. Peak segment / digit
# drive currents are the typ figures from the Electrical Specifications table (the
# second "Common Anode" ISEG row is the common-cathode source figure).
ICM7218 = [
    # mpn, symbol, polarity, access, lifecycle, segment / digit current
    ("ICM7218AIJI", "ICM7218A", "common anode", "sequential, hex/Code B/no-decode",
     "Obsolete", "40mA seg sink / 200mA digit"),
    ("ICM7218BIJI", "ICM7218B", "common cathode", "sequential, hex/Code B/no-decode",
     "Active", "20mA seg / 100mA digit sink"),
    ("ICM7218CIJI", "ICM7218C", "common anode", "random access, hex/Code B",
     "Obsolete", "40mA seg sink / 200mA digit"),
    ("ICM7218DIJI", "ICM7218D", "common cathode", "random access, hex/Code B",
     "Obsolete", "20mA seg / 100mA digit sink"),
]


def icm7218():
    for mpn, sym, pol, access, life, iout in ICM7218:
        yield {
            **COMMON,
            "unique_id": f"Renesas-{mpn}",
            "part_locator": f"led-driver-7seg-8digit-parallel-{pol.split()[1]}-cerdip28",
            "mpn": mpn, "manufacturer": "Renesas", "package": "CERDIP-28",
            "value": sym,
            "description": (
                f"Intersil {sym} 8-digit multiplexed LED display decoder/driver, {pol}, "
                f"8 digits x 8 segments (64 LEDs), {access}, 8-byte display RAM, "
                f"parallel uP interface, 4-6V, CERDIP-28"),
            "datasheet": "${TERRA_EDA_LIB}/datasheets/renesas/icm7218.pdf",
            "manufacturer_link": "https://www.renesas.com/en/products/icm7218",
            "kicad_symbol": f"{SYMLIB}:{sym}", "kicad_footprint": DIP28W,
            # Only the R5254 ordering codes are marked Pb-free (e3) in the sheet.
            "lifecycle_status": life, "rohs": None, "pin_count": "28",
            "keywords": ("LED display driver, 7-segment, 8-digit, multiplexed, "
                         f"hexadecimal, Code B, parallel, {pol}, ICM7218, {sym}"),
            "temp_operating_min": -40, "temp_operating_max": 85,
            "temp_storage_min": -65, "temp_storage_max": 150,
            "channels": 64, "output_current": iout,
            "supply_voltage_min": 4.0, "supply_voltage_max": 6.0,
            "output_voltage_max": None, "switching_freq": "250Hz",
            "dimming_method": "none", "interface": "parallel",
            "current_accuracy": None,
        }


def records():
    yield from lm391x()
    yield from max72xx()
    yield from icm7218()


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
    for r in recs:  # MPN encodes the temperature grade for the MAX72xx codes
        if r["mpn"].startswith("MAX72"):
            assert TEMP[r["mpn"][7]] == (r["temp_operating_min"], r["temp_operating_max"]), r["mpn"]
            assert (r["mpn"][8] == "N") == (r["package"] == "PDIP-24"), r["mpn"]
    lines = [
        "-- Terra EDA Library - led_drivers display drivers (LM391x, MAX72xx, ICM7218)",
        f"-- Generated by {Path(__file__).name}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO led_drivers ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} parts")


if __name__ == "__main__":
    main()
