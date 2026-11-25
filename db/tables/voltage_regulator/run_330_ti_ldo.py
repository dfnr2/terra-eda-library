#!/usr/bin/env python3
"""TI through-hole low-dropout regulators: LM2940 / LM2940C (TO-220), LM1117 (TO-220),
LP2950 (TO-92).

One row per fixed voltage (plus LM1117-ADJ) in the bulk/tube TO-220 or TO-92 orderable
that ti.com lists ACTIVE (2026-11-25). LM2940-N (LM2940T, -40..125 degC, 60 V
transient) and LM2940C (LM2940CT, 0..125 degC, 45 V transient) share one datasheet
but are distinct grades with different voltage menus, so both are emitted. LP2950 uses
the LP2950-N datasheet's C grade (LP2950CZ, +-1% at 25 degC).

Specs are the datasheet's 25 degC limits. input_voltage_min is the low end of the
input range the output/line regulation is specified over; input_voltage_max is the
recommended maximum input (26 V LM2940, 15 V LM1117, 30 V LP2950).

Symbols (pin maps checked by _vreg.check_pinouts): LM2940 TO-220 is IN-GND-OUT
(tab = GND), the same map as the stock LM2937xT LDO symbol; LM1117T fixed is
GND-OUT-IN and ADJ is ADJ-OUT-IN (stock LM1117T-x); LP2950 TO-92 is OUT-GND-IN
(stock LP2950-x_TO92). The LM1117T-x stock symbols default to a horizontal footprint;
rows use the vertical TO-220-3 like every other TO-220 row.
"""
from pathlib import Path

from _vreg import TO220, TO92, tol, write

OUTPUT_FILE = Path(__file__).with_name("voltage_regulator_generated_330_ti_ldo.sql")
CREATED_BY = Path(__file__).name
TI_DS = "${TERRA_EDA_LIB}/datasheets/ti/"

LM2940_IQ = "10mA typ, 15mA max (IOUT=5mA); 30mA typ, 45mA max (IOUT=1A)"
LM2940_DROPOUT = "0.5V typ, 0.8V max (1A); 110mV typ, 150mV max (100mA)"

# LM2940 per-voltage 25 degC data (VO min/max, Vin min, line, load, noise uVrms, RR typ/min)
LM2940_V = {
    5:  (4.85, 5.15, 6.25, "20mV typ, 50mV max (VO+2V to 26V, 5mA)", "35mV typ, 50mV max (50mA-1A)", 150, "72dB typ, 60dB min"),
    8:  (7.76, 8.24, 9.4, "20mV typ, 80mV max (VO+2V to 26V, 5mA)", "55mV typ, 80mV max (50mA-1A)", 240, "66dB typ, 54dB min"),
    9:  (8.73, 9.27, 10.5, "20mV typ, 90mV max (VO+2V to 26V, 5mA)", "60mV typ, 90mV max (50mA-1A)", 270, "64dB typ, 52dB min"),
    10: (9.7, 10.3, 11.5, "20mV typ, 100mV max (VO+2V to 26V, 5mA)", "65mV typ, 100mV max (50mA-1A)", 300, "63dB typ, 51dB min"),
    12: (11.64, 12.36, 13.6, "20mV typ, 120mV max (VO+2V to 26V, 5mA)", "55mV typ, 120mV max (50mA-1A)", 360, "66dB typ, 54dB min"),
    15: (14.55, 15.45, 16.75, "20mV typ, 150mV max (VO+2V to 26V, 5mA)", "70mV typ, 150mV max (50mA-1A)", 450, "64dB typ, 52dB min"),
}
LM2940_PARTS = [  # (mpn, nominal V, grade)
    ("LM2940T-5.0/NOPB", 5, "N"), ("LM2940T-8.0/NOPB", 8, "N"), ("LM2940T-9.0/NOPB", 9, "N"),
    ("LM2940T-10.0/NOPB", 10, "N"), ("LM2940T-12.0/NOPB", 12, "N"),
    ("LM2940CT-5.0/NOPB", 5, "C"), ("LM2940CT-9.0/NOPB", 9, "C"),
    ("LM2940CT-12/NOPB", 12, "C"), ("LM2940CT-15/NOPB", 15, "C"),
]

# LM1117 fixed: (mpn, suffix, VO min/max at 25 degC, Vin min, line max, load max)
LM1117_FIXED = [
    ("LM1117T-2.5/NOPB", "2.5", 2.475, 2.525, 3.9, "1mV typ, 6mV max (3.9-10V, IOUT=0)", "1mV typ, 10mV max (0-800mA)"),
    ("LM1117T-3.3/NOPB", "3.3", 3.267, 3.333, 4.75, "1mV typ, 6mV max (4.75-15V, IOUT=0)", "1mV typ, 10mV max (0-800mA)"),
    ("LM1117T-5.0/NOPB", "5.0", 4.95, 5.05, 6.5, "1mV typ, 10mV max (6.5-15V, IOUT=0)", "1mV typ, 15mV max (0-800mA)"),
]

# LP2950C (CZ): (mpn, suffix, VO min/max at 25 degC, noise)
LP2950_PARTS = [
    ("LP2950CZ-3.0/NOPB", "3.0", 2.970, 3.030, "160µVrms with CL=200µF (10Hz-100kHz)"),
    ("LP2950CZ-3.3/NOPB", "3.3", 3.267, 3.333, "160µVrms with CL=200µF (10Hz-100kHz)"),
    ("LP2950CZ-5.0/NOPB", "5.0", 4.95, 5.05, "430µVrms with CL=1µF; 160µVrms with CL=200µF (10Hz-100kHz)"),
]


def lm2940(mpn, nom, grade):
    lo, hi, vin_min, line, load, noise, rr = LM2940_V[nom]
    c = grade == "C"
    value = f"LM2940{'C' if c else ''}-{nom}" if nom >= 12 and c else f"LM2940{'C' if c else ''}-{nom:.1f}"
    return {
        "unique_id": f"Texas_Instruments-{mpn}", "mpn": mpn, "manufacturer": "Texas Instruments",
        "value": value, "part_locator": f"reg-ldo-{nom}v-1a-to220", "package": "TO-220",
        "description": (f"Texas Instruments {value} {nom}V 1A low-dropout regulator, 0.5V typ dropout, "
                        f"reverse-battery protected, {'0' if c else '-40'} to 125°C, TO-220"),
        "datasheet": TI_DS + "lm2940-n.pdf",
        "manufacturer_link": f"https://www.ti.com/product/{'LM2940C' if c else 'LM2940-N'}",
        "kicad_symbol": "Regulator_Linear:LM2937xT", "kicad_footprint": TO220,
        "pinout": "IN-GND-OUT", "pin_count": "3",
        "temp_operating_min": 0.0 if c else -40.0, "temp_operating_max": 125.0,
        "output_voltage": f"{nom}V", "output_current": "1A",
        "input_voltage_min": vin_min, "input_voltage_max": 26.0,
        "dropout_voltage": LM2940_DROPOUT, "quiescent_current": LM2940_IQ,
        "output_noise": f"{noise}µVrms (10Hz-100kHz)", "psrr": f"{rr} (120Hz, 100mA)",
        "line_regulation": line, "load_regulation": load, "accuracy": tol(lo, hi, nom),
        "adjustable": "no",
        "features": ("current-limit,thermal-shutdown,reverse-battery-protection,"
                     "mirror-image-insertion-protection,"
                     + ("45v-transient" if c else "60v-transient")),
        "keywords": f"ldo,low-dropout,linear-regulator,fixed,positive,{nom}v,1a,lm2940,"
                    f"{value.lower()},automotive,to-220",
    }


def lm1117_common(mpn, value):
    return {
        "unique_id": f"Texas_Instruments-{mpn}", "mpn": mpn, "manufacturer": "Texas Instruments",
        "value": value, "package": "TO-220", "datasheet": TI_DS + "lm1117.pdf",
        "manufacturer_link": "https://www.ti.com/product/LM1117", "kicad_footprint": TO220,
        "pin_count": "3", "temp_operating_min": 0.0, "temp_operating_max": 125.0,
        "output_current": "800mA", "input_voltage_max": 15.0,
        "dropout_voltage": "1.2V typ, 1.3V max (800mA); 1.1V typ (100mA)",
        "output_noise": "0.003% of VO rms (10Hz-10kHz)",
        "psrr": "75dB typ, 60dB min (120Hz, VIN-VOUT=3V)",
        "features": "current-limit,thermal-shutdown",
    }


def lm1117_rows():
    rows = []
    for mpn, sfx, lo, hi, vin_min, line, load in LM1117_FIXED:
        nom = float(sfx)
        value = f"LM1117-{sfx}"
        rows.append({**lm1117_common(mpn, value),
                     "part_locator": f"reg-ldo-{nom:g}v-800ma-to220",
                     "description": f"Texas Instruments {value} {sfx}V 800mA low-dropout regulator, "
                                    f"1.2V typ dropout, ±1%, 0 to 125°C, TO-220",
                     "kicad_symbol": f"Regulator_Linear:LM1117T-{sfx}", "pinout": "GND-OUT-IN",
                     "output_voltage": f"{nom:g}V", "input_voltage_min": vin_min,
                     "quiescent_current": "5mA typ, 10mA max", "line_regulation": line,
                     "load_regulation": load, "accuracy": tol(lo, hi, nom), "adjustable": "no",
                     "keywords": f"ldo,low-dropout,linear-regulator,fixed,positive,{nom:g}v,800ma,"
                                 f"lm1117,{value.lower()},to-220"})
    rows.append({**lm1117_common("LM1117T-ADJ/NOPB", "LM1117-ADJ"),
                 "part_locator": "reg-ldo-adj-1.25-13.8v-800ma-to220",
                 "description": "Texas Instruments LM1117-ADJ 800mA adjustable low-dropout regulator, "
                                "1.25-13.8V out, 1.2V typ dropout, 0 to 125°C, TO-220",
                 "kicad_symbol": "Regulator_Linear:LM1117T-ADJ", "pinout": "ADJ-OUT-IN",
                 "output_voltage": "adjustable", "output_voltage_min": 1.25, "output_voltage_max": 13.8,
                 "quiescent_current": "ADJ pin 60µA typ, 120µA max; min load 1.7mA typ, 5mA max",
                 "line_regulation": "0.035% typ, 0.2% max (VIN-VOUT 1.5-13.75V, 10mA)",
                 "load_regulation": "0.2% typ, 0.4% max (10-800mA, VIN-VOUT=3V)",
                 "accuracy": "VREF 1.238-1.262V (1.25V typ) at 25°C", "adjustable": "yes",
                 "keywords": "ldo,low-dropout,linear-regulator,adjustable,positive,800ma,lm1117,"
                             "lm1117-adj,to-220"})
    return rows


def lp2950_rows():
    rows = []
    for mpn, sfx, lo, hi, noise in LP2950_PARTS:
        nom = float(sfx)
        value = f"LP2950-{sfx}"
        rows.append({
            "unique_id": f"Texas_Instruments-{mpn}", "mpn": mpn, "manufacturer": "Texas Instruments",
            "value": value, "part_locator": f"reg-ldo-{nom:g}v-100ma-to92", "package": "TO-92",
            "description": f"Texas Instruments {value} {sfx}V 100mA micropower low-dropout regulator, "
                          f"75µA quiescent, 380mV typ dropout, ±1%, -40 to 125°C, TO-92",
            "datasheet": TI_DS + "lp2950-n.pdf", "manufacturer_link": "https://www.ti.com/product/LP2950-N",
            "kicad_symbol": f"Regulator_Linear:LP2950-{sfx}_TO92", "kicad_footprint": TO92,
            "pinout": "OUT-GND-IN", "pin_count": "3",
            "temp_operating_min": -40.0, "temp_operating_max": 125.0,
            "output_voltage": f"{nom:g}V", "output_current": "100mA",
            "input_voltage_min": round(nom + 1.0, 2), "input_voltage_max": 30.0,
            "dropout_voltage": "380mV typ, 450mV max (100mA); 50mV typ, 80mV max (100µA)",
            "quiescent_current": "75µA typ, 120µA max (IL=100µA); 8mA typ, 12mA max (IL=100mA)",
            "output_noise": noise,
            "line_regulation": "0.04% typ, 0.2% max (VO+1V to 30V)",
            "load_regulation": "0.1% typ, 0.2% max (100µA-100mA)",
            "accuracy": tol(lo, hi, nom), "adjustable": "no",
            "features": "current-limit,thermal-shutdown,micropower",
            "keywords": f"ldo,low-dropout,linear-regulator,fixed,positive,{nom:g}v,100ma,micropower,"
                        f"lp2950,{value.lower()},to-92",
        })
    return rows


def main():
    rows = [lm2940(*p) for p in LM2940_PARTS] + lm1117_rows() + lp2950_rows()
    for r in rows:
        r["regulator_type"] = "LDO"
    write(OUTPUT_FILE, "TI low-dropout regulators (TO-220 / TO-92)", CREATED_BY, rows)


if __name__ == "__main__":
    main()
