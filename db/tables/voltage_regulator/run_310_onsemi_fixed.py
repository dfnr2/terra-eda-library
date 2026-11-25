#!/usr/bin/env python3
"""onsemi fixed three-terminal linear regulators, through-hole (TO-220 / TO-92).

Families: MC7800 (1 A +), MC7900 (1 A -), MC78L00A (100 mA +), MC79L00A (100 mA -),
MC78M00 (500 mA +), MC79M00 (500 mA -). One row per voltage, taking the commercial
C/AC grade (0 to 125 degC) in its bulk/rail through-hole orderable code. Only voltages
the datasheet's ordering table lists *and* onsemi's product page shows Active
(2026-11-25) are emitted; see plans/voltage-regulator-th-classics.md for the drops.

Specs are transcribed from the grade's electrical-characteristics table: line/load
regulation are the 25 degC limits over the widest input range the table gives;
input_voltage_min is the low end of the input range the full-load output-voltage
limit is specified over; input_voltage_max is the absolute-maximum input. Negative
regulators carry signed voltages (input_voltage_min is the most negative input).

Symbols are stock Regulator_Linear parts whose pin map _vreg.check_pinouts verifies
against each family's datasheet pinout (78xx IN-GND-OUT, 79xx GND-IN-OUT,
78Lxx TO-92 OUT-GND-IN, 79Lxx TO-92 GND-IN-OUT).
"""
from pathlib import Path

from _vreg import TO220, TO92, tol, write

OUTPUT_FILE = Path(__file__).with_name("voltage_regulator_generated_310_onsemi_fixed.sql")
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets/onsemi/"
LINK = "https://www.onsemi.com/products/standard-products/ldo-voltage-regulators/"

FEATURES = "current-limit,thermal-shutdown,safe-area-protection"

# family -> shared attributes
FAMILY = {
    "MC7800": dict(datasheet=DS + "mc7800-d.pdf", link=LINK + "mc7800", current="1A",
                   pkg="TO-220", fp=TO220, polarity="positive", pinout="IN-GND-OUT",
                   noise_unit="µV/V of VO", dropout="2.0V typ (1A)"),
    "MC7900": dict(datasheet=DS + "mc7900-d.pdf", link=LINK + "mc7900", current="1A",
                   pkg="TO-220", fp=TO220, polarity="negative", pinout="GND-IN-OUT",
                   noise_unit="µV", dropout="1.3V typ (1A)"),
    "MC78L00A": dict(datasheet=DS + "mc78l00a-d.pdf", link=LINK + "mc78l", current="100mA",
                     pkg="TO-92", fp=TO92, polarity="positive", pinout="OUT-GND-IN",
                     noise_unit="µV", dropout="1.7V typ"),
    "MC79L00A": dict(datasheet=DS + "mc79l00-d.pdf", link=LINK + "mc79l", current="100mA",
                     pkg="TO-92", fp=TO92, polarity="negative", pinout="GND-IN-OUT",
                     noise_unit="µV", dropout="1.7V typ (40mA)"),
    "MC78M00": dict(datasheet=DS + "mc78m00-d.pdf", link=LINK + "mc78m", current="500mA",
                    pkg="TO-220", fp=TO220, polarity="positive", pinout="IN-GND-OUT",
                    noise_unit="µV", dropout="2.0V typ"),
    "MC79M00": dict(datasheet=DS + "mc79m00-d.pdf", link=LINK + "mc79m", current="500mA",
                    pkg="TO-220", fp=TO220, polarity="negative", pinout="GND-IN-OUT",
                    noise_unit="µV", dropout="1.1V typ (500mA)"),
}

# (family, mpn, value, nominal V, VO min/max at 25 degC, Vin min, Vin max, line reg,
#  load reg, quiescent, ripple rejection, noise (10 Hz-100 kHz), grade temp range, symbol)
PARTS = [
    # MC7800 C grade (TJ 0..125). Datasheet lists no TO-220 06/10 V; 7806 TO-220 is obsolete.
    ("MC7800", "MC7805CTG", "MC7805", 5, 4.8, 5.2, 7.0, 35.0,
     "0.5mV typ, 20mV max (7.5-20V, 1A)", "1.3mV typ, 25mV max (5mA-1A)",
     "3.2mA typ, 6.5mA max", "83dB typ, 62dB min (120Hz)", 10, (0, 125), "LM7805_TO220"),
    ("MC7800", "MC7808CTG", "MC7808", 8, 7.7, 8.3, 10.5, 35.0,
     "6.0mV typ, 32mV max (10.5-25V)", "1.4mV typ, 35mV max (5mA-1.5A)",
     "3.3mA typ, 8.0mA max", "62dB typ, 56dB min (120Hz)", 10, (0, 125), "LM7808_TO220"),
    ("MC7800", "MC7809CTG", "MC7809", 9, 8.65, 9.35, 11.5, 35.0,
     "6.2mV typ, 32mV max (11-26V)", "1.5mV typ, 35mV max (5mA-1.5A)",
     "3.4mA typ, 8.0mA max", "61dB typ, 56dB min (120Hz)", 10, (0, 125), "LM7809_TO220"),
    ("MC7800", "MC7812CTG", "MC7812", 12, 11.5, 12.5, 14.5, 35.0,
     "3.8mV typ, 24mV max (14.5-30V)", "8.1mV typ, 60mV max (5mA-1.5A)",
     "3.4mA typ, 6.5mA max", "60dB typ, 55dB min (120Hz)", 10, (0, 125), "LM7812_TO220"),
    ("MC7800", "MC7815CTG", "MC7815", 15, 14.4, 15.6, 17.5, 35.0,
     "8.5mV typ, 30mV max (17.9-30V)", "1.8mV typ, 55mV max (5mA-1.5A)",
     "3.5mA typ, 6.5mA max", "58dB typ, 54dB min (120Hz)", 10, (0, 125), "LM7815_TO220"),
    ("MC7800", "MC7818CTG", "MC7818", 18, 17.3, 18.7, 21.0, 35.0,
     "9.5mV typ, 50mV max (21-33V)", "2.0mV typ, 55mV max (5mA-1.5A)",
     "3.5mA typ, 6.5mA max", "57dB typ, 53dB min (120Hz)", 10, (0, 125), "LM7818_TO220"),
    ("MC7800", "MC7824CTG", "MC7824", 24, 23.0, 25.0, 27.0, 40.0,
     "2.7mV typ, 60mV max (27-38V)", "4.4mV typ, 65mV max (5mA-1.5A)",
     "3.6mA typ, 6.5mA max", "54dB typ, 50dB min (120Hz)", 10, (0, 125), "LM7824_TO220"),

    # MC7900 C grade (TJ 0..125). MC7908CTG / MC7924CTG are obsolete.
    ("MC7900", "MC7905CTG", "MC7905", -5, -4.8, -5.2, -35.0, -7.0,
     "35mV typ, 100mV max (-7 to -25V, 500mA)", "11mV typ, 100mV max (5mA-1.5A)",
     "4.3mA typ, 8.0mA max", "70dB typ (120Hz, 20mA)", 40, (0, 125), "MC7905"),
    ("MC7900", "MC7906CTG", "MC7906", -6, -5.75, -6.25, -35.0, -8.0,
     "43mV typ, 120mV max (-8 to -25V, 500mA)", "13mV typ, 120mV max (5mA-1.5A)",
     "4.3mA typ, 8.0mA max", "65dB typ (120Hz, 20mA)", 45, (0, 125), "MC7906"),
    ("MC7900", "MC7912CTG", "MC7912", -12, -11.5, -12.5, -35.0, -14.5,
     "55mV typ, 240mV max (-14.5 to -30V, 500mA)", "46mV typ, 240mV max (5mA-1.5A)",
     "4.4mA typ, 8.0mA max", "61dB typ (120Hz, 20mA)", 75, (0, 125), "MC7912"),
    ("MC7900", "MC7915CTG", "MC7915", -15, -14.4, -15.6, -35.0, -17.5,
     "57mV typ, 300mV max (-17.5 to -30V, 500mA)", "68mV typ, 300mV max (5mA-1.5A)",
     "4.4mA typ, 8.0mA max", "60dB typ (120Hz, 20mA)", 90, (0, 125), "MC7915"),
    ("MC7900", "MC7918CTG", "MC7918", -18, -17.3, -18.7, -35.0, -21.0,
     "90mV typ, 360mV max (-21 to -33V, 500mA)", "110mV typ, 360mV max (5mA-1.5A)",
     "4.5mA typ, 8.0mA max", "59dB typ (120Hz, 20mA)", 110, (0, 125), "MC7918"),

    # MC78L00A AC grade (TJ 0..125), bulk TO-92 ("P" = TO-92, no tape suffix).
    ("MC78L00A", "MC78L05ACPG", "MC78L05", 5, 4.8, 5.2, 7.0, 30.0,
     "55mV typ, 150mV max (7-20V)", "11mV typ, 60mV max (1-100mA)",
     "3.8mA typ, 6.0mA max", "49dB typ, 41dB min (120Hz)", 40, (0, 125), "MC78L05_TO92"),
    ("MC78L00A", "MC78L08ACPG", "MC78L08", 8, 7.7, 8.3, 10.5, 30.0,
     "20mV typ, 175mV max (10.5-23V)", "15mV typ, 80mV max (1-100mA)",
     "3.0mA typ, 6.0mA max", "57dB typ, 37dB min (120Hz)", 60, (0, 125), "MC78L08_TO92"),
    ("MC78L00A", "MC78L09ACPG", "MC78L09", 9, 8.6, 9.4, 11.5, 30.0,
     "20mV typ, 175mV max (11.5-24V)", "15mV typ, 90mV max (1-100mA)",
     "3.0mA typ, 6.0mA max", "57dB typ, 37dB min (120Hz)", 60, (0, 125), "L78L09_TO92"),
    ("MC78L00A", "MC78L12ACPG", "MC78L12", 12, 11.5, 12.5, 14.5, 35.0,
     "120mV typ, 250mV max (14.5-27V)", "20mV typ, 100mV max (1-100mA)",
     "4.2mA typ, 6.5mA max", "42dB typ, 37dB min (120Hz)", 80, (0, 125), "MC78L12_TO92"),
    ("MC78L00A", "MC78L15ACPG", "MC78L15", 15, 14.4, 15.6, 17.5, 35.0,
     "130mV typ, 300mV max (17.5-30V)", "25mV typ, 150mV max (1-100mA)",
     "4.4mA typ, 6.5mA max", "39dB typ, 34dB min (120Hz)", 90, (0, 125), "MC78L15_TO92"),
    ("MC78L00A", "MC78L18ACPG", "MC78L18", 18, 17.3, 18.7, 20.7, 35.0,
     "45mV typ, 325mV max (20.7-33V)", "30mV typ, 170mV max (1-100mA)",
     "3.1mA typ, 6.5mA max", "48dB typ, 33dB min (120Hz)", 150, (0, 125), "MC78L18_TO92"),
    ("MC78L00A", "MC78L24ACPG", "MC78L24", 24, 23.0, 25.0, 27.0, 40.0,
     "60mV typ, 350mV max (27-38V)", "40mV typ, 200mV max (1-100mA)",
     "3.1mA typ, 6.5mA max", "45dB typ, 31dB min (120Hz)", 200, (0, 125), "MC78L24_TO92"),

    # MC79L00A AC grade (TJ 0..125), bulk TO-92. The datasheet gives max limits only.
    # No stock MC79L18/24 TO-92 symbol: the 79L05 base symbol has the identical pinout.
    ("MC79L00A", "MC79L05ACPG", "MC79L05", -5, -4.8, -5.2, -30.0, -7.0,
     "150mV max (-7 to -20V)", "60mV max (1-100mA)",
     "6.0mA max", "49dB typ, 41dB min (120Hz)", 40, (0, 125), "LM79L05_TO92"),
    ("MC79L00A", "MC79L12ACPG", "MC79L12", -12, -11.5, -12.5, -35.0, -14.5,
     "250mV max (-14.5 to -27V)", "100mV max (1-100mA)",
     "6.5mA max", "42dB typ, 37dB min (120Hz)", 80, (0, 125), "LM79L12_TO92"),
    ("MC79L00A", "MC79L15ACPG", "MC79L15", -15, -14.4, -15.6, -35.0, -17.5,
     "300mV max (-17.5 to -30V)", "150mV max (1-100mA)",
     "6.5mA max", "39dB typ, 34dB min (120Hz)", 90, (0, 125), "LM79L15_TO92"),
    ("MC79L00A", "MC79L18ACPG", "MC79L18", -18, -17.3, -18.7, -35.0, -20.7,
     "325mV max (-20.7 to -33V)", "170mV max (1-100mA)",
     "6.5mA max", "48dB typ, 33dB min (120Hz)", 150, (0, 125), "LM79L05_TO92"),
    ("MC79L00A", "MC79L24ACPG", "MC79L24", -24, -23.0, -25.0, -40.0, -27.0,
     "350mV max (-27 to -38V)", "200mV max (1-100mA)",
     "6.5mA max", "47dB typ, 31dB min (120Hz)", 200, (0, 125), "LM79L05_TO92"),

    # MC78M00 C grade (TJ 0..125). TO-220 06/08/09/18/20/24 are obsolete.
    # Only a 78M05 stock symbol exists; it is the IN-GND-OUT TO-220 base for all three.
    ("MC78M00", "MC78M05CTG", "MC78M05", 5, 4.8, 5.2, 7.0, 35.0,
     "3.0mV typ, 50mV max (7-25V, 200mA)", "20mV typ, 100mV max (5-500mA)",
     "3.2mA typ, 6.0mA max", "80dB typ, 62dB min (120Hz, 300mA)", 40, (0, 125), "LM78M05_TO220"),
    ("MC78M00", "MC78M12CTG", "MC78M12", 12, 11.5, 12.5, 14.5, 35.0,
     "8.0mV typ, 50mV max (14.5-30V, 200mA)", "25mV typ, 240mV max (5-500mA)",
     "3.2mA typ, 6.0mA max", "80dB typ, 55dB min (120Hz, 300mA)", 75, (0, 125), "LM78M05_TO220"),
    ("MC78M00", "MC78M15CTG", "MC78M15", 15, 14.4, 15.6, 17.5, 35.0,
     "10mV typ, 50mV max (17.5-30V, 200mA)", "25mV typ, 300mV max (5-500mA)",
     "3.2mA typ, 6.0mA max", "70dB typ, 54dB min (120Hz, 300mA)", 90, (0, 125), "LM78M05_TO220"),

    # MC79M00: 05/08 TO-220 and MC79M12CTG are obsolete; MC79M12 survives only as the
    # B grade (TJ -40..125), MC79M15 as both (C grade taken).
    ("MC79M00", "MC79M12BTG", "MC79M12", -12, -11.5, -12.5, -35.0, -14.5,
     "5.0mV typ, 80mV max (-14.5 to -30V)", "30mV typ, 240mV max (5-500mA)",
     "4.4mA typ, 8.0mA max", "60dB typ, 54dB min (120Hz)", 75, (-40, 125), "MC79M12_TO220"),
    ("MC79M00", "MC79M15CTG", "MC79M15", -15, -14.4, -15.6, -35.0, -17.5,
     "5.0mV typ, 80mV max (-17.5 to -30V)", "30mV typ, 240mV max (5-500mA)",
     "4.4mA typ, 8.0mA max", "60dB typ, 54dB min (120Hz)", 90, (0, 125), "MC79M15_TO220"),
]


def row(family, mpn, value, nom, lo, hi, vin_min, vin_max, line, load, iq, rr, noise,
        temps, symbol):
    f = FAMILY[family]
    neg = f["polarity"] == "negative"
    vtok = f"neg{abs(nom)}v" if neg else f"{nom}v"
    pkgtok = f["pkg"].lower().replace("-", "")
    return {
        "unique_id": f"onsemi-{mpn}", "mpn": mpn, "manufacturer": "onsemi",
        "part_locator": f"reg-linear-{vtok}-{f['current'].lower()}-{pkgtok}",
        "package": f["pkg"], "value": value,
        "description": (f"onsemi {value} {nom}V {f['current']} fixed {f['polarity']} "
                        f"three-terminal linear regulator, {tol(lo, hi, nom).split(' (')[0]}, "
                        f"{temps[0]} to {temps[1]}°C, {f['pkg']}"),
        "datasheet": f["datasheet"], "manufacturer_link": f["link"],
        "kicad_symbol": f"Regulator_Linear:{symbol}", "kicad_footprint": f["fp"],
        "pinout": f["pinout"], "pin_count": "3",
        "keywords": ",".join(["linear-regulator", "fixed", f["polarity"], f"{nom}v".replace("-", "neg"),
                              f["current"].lower(), "three-terminal", value[2:].lower(),
                              value.lower(), f["pkg"].lower()]),
        "temp_operating_min": float(temps[0]), "temp_operating_max": float(temps[1]),
        "regulator_type": "linear", "output_voltage": f"{nom}V",
        "output_current": f["current"],
        "input_voltage_min": vin_min, "input_voltage_max": vin_max,
        "dropout_voltage": f["dropout"], "quiescent_current": iq,
        "output_noise": f"{noise}{f['noise_unit']} (10Hz-100kHz)", "psrr": rr,
        "line_regulation": line, "load_regulation": load,
        "accuracy": tol(lo, hi, nom), "adjustable": "no", "features": FEATURES,
    }


def main():
    write(OUTPUT_FILE, "onsemi fixed linear regulators (TO-220 / TO-92)", CREATED_BY,
          [row(*p) for p in PARTS])


if __name__ == "__main__":
    main()
