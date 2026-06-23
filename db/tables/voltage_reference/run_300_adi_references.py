#!/usr/bin/env python3
"""Harvest Analog Devices / Linear Technology precision voltage references.

Datasheet-driven; same BASE-specs x VARIANTS-packages shape as the ic_opamp
generators. Datasheets live in the central store at datasheets/analog-devices/.

These three series references have no dedicated KiCad symbol, and series-
reference pinouts vary enough that borrowing a stand-in would risk wrong nets --
so each row carries its (verified) footprint and full specs with a NULL symbol,
flagged REVIEW. The generator prints those on every run; a curated symbol can be
assigned per part later.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import re
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("voltage_reference_generated_300_adi_references.sql")
CREATED_BY = Path(__file__).name

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "variant", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "rohs", "allow_substitution", "tracking", "source", "dump_priority", "tier",
    "keywords", "pin_count", "reference_type", "output_voltage", "output_voltage_options",
    "initial_accuracy", "temperature_coefficient", "output_noise", "output_current",
    "input_voltage_min", "input_voltage_max", "dropout_voltage", "line_regulation",
    "load_regulation", "long_term_drift", "adjustable",
]

DEFAULTS = {
    "manufacturer": "Analog Devices",
    "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
    "source": None, "dump_priority": 0, "tier": 2,
}

DIP8 = "Package_DIP:DIP-8_W7.62mm"
SOIC8 = "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm"
MSOP8 = "Package_SO:MSOP-8_3x3mm_P0.65mm"
RV = "REVIEW: no KiCad symbol; series-reference pinout -- assign in KiCad"

# Curated DIP-8 symbol covering every LT1021 N8 grade/voltage; lives in the
# per-table library kicad_symbols/terra-voltage-reference.kicad_sym.
LT1021SYM = "terra-voltage-reference:LT1021-xN8"
LT1021_COMMON = dict(
    datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1021.pdf",
    manufacturer_link="https://www.analog.com/en/products/lt1021.html",
    keywords="voltage-reference,precision,series,buried-zener,low-drift,low-noise,lt1021",
    reference_type="series", output_voltage_options="5V,7V,10V",
    output_noise="4µVp-p (0.1-10Hz)", output_current="10mA",
    input_voltage_max=40.0, dropout_voltage="1V", line_regulation="0.5ppm/V",
    load_regulation="12ppm/mA", long_term_drift="7ppm/1000hr", adjustable="no")
# B grade = ultralow drift; D grade = standard drift. Both share initial tolerance
# (voltage-dependent: ±0.05V absolute). The tight-tolerance C grade is not stocked here.
TC_B = "5ppm/°C max (2ppm typ)"
TC_D = "20ppm/°C max (3ppm typ)"


def lt1021(voltage, accuracy, vin_min):
    return {**LT1021_COMMON, "output_voltage": f"{voltage}V", "initial_accuracy": accuracy,
            "input_voltage_min": vin_min,
            "description": f"Analog Devices LT1021 precision buried-zener voltage reference, series, {voltage}V"}


BASE = {
    "LT1021-5": lt1021(5, "±1%", 6.5),
    "LT1021-7": lt1021(7, "±0.7%", 8.5),
    "LT1021-10": lt1021(10, "±0.5%", 11.5),
    "LT1027": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/lt1027.pdf",
        description="Analog Devices LT1027 precision low-drift series voltage reference, 2ppm/°C, ±0.05%, 5V",
        manufacturer_link="https://www.analog.com/en/products/lt1027.html",
        keywords="voltage-reference,precision,series,5v,low-drift,low-noise,adc-reference,lt1027",
        reference_type="series", output_voltage="5V", output_voltage_options="5V",
        initial_accuracy="±0.05%", temperature_coefficient="2ppm/°C",
        output_noise="3µVp-p (0.1-10Hz)", output_current="15mA source / 10mA sink",
        input_voltage_min=8.0, input_voltage_max=40.0, dropout_voltage="3V",
        line_regulation="3ppm/V", load_regulation="-3ppm/mA",
        long_term_drift="20ppm/month", adjustable="no"),
    "LTC6655-5": dict(
        datasheet="${TERRA_EDA_LIB}/datasheets/analog-devices/ltc6655.pdf",
        description="Analog Devices LTC6655 precision low-noise buried-zener series voltage reference, ±0.025%, 2ppm/°C, 0.25ppm p-p, 5V",
        manufacturer_link="https://www.analog.com/en/products/ltc6655.html",
        keywords="voltage-reference,precision,low-noise,series,buried-zener,low-drift,5v,ltc6655",
        reference_type="series", output_voltage="5V",
        output_voltage_options="1.25V,2.048V,2.5V,3V,3.3V,4.096V,5V",
        initial_accuracy="±0.025%", temperature_coefficient="2ppm/°C",
        output_noise="0.25ppm p-p (0.1-10Hz); 0.12ppm LN grade", output_current="±5mA",
        input_voltage_min=5.2, input_voltage_max=13.2, dropout_voltage="500mV",
        line_regulation="5ppm/V", load_regulation="3ppm/mA source, 10ppm/mA sink",
        long_term_drift="60ppm/√khr", adjustable="no"),
}

# (package, mpn, pin_count, kicad_symbol, kicad_footprint, note[, overrides])
# LT1021 DIP-8 (N8) rows use the curated terra-voltage-reference:LT1021-xN8 symbol; the B and D
# grades share a package/voltage but differ in temperature coefficient.
VARIANTS = {
    "LT1021-5": [("PDIP-8", "LT1021BCN8-5", "8", LT1021SYM, DIP8, "through-hole", {"variant": "B grade", "temperature_coefficient": TC_B}),
                 ("PDIP-8", "LT1021DCN8-5", "8", LT1021SYM, DIP8, "through-hole", {"variant": "D grade", "temperature_coefficient": TC_D})],
    "LT1021-7": [("PDIP-8", "LT1021BCN8-7", "8", LT1021SYM, DIP8, "through-hole", {"variant": "B grade", "temperature_coefficient": TC_B}),
                 ("PDIP-8", "LT1021DCN8-7", "8", LT1021SYM, DIP8, "through-hole", {"variant": "D grade", "temperature_coefficient": TC_D})],
    "LT1021-10": [("PDIP-8", "LT1021BCN8-10", "8", LT1021SYM, DIP8, "through-hole", {"variant": "B grade", "temperature_coefficient": TC_B}),
                  ("PDIP-8", "LT1021DCN8-10", "8", LT1021SYM, DIP8, "through-hole", {"variant": "D grade", "temperature_coefficient": TC_D})],
    "LT1027": [("PDIP-8", "LT1027CN8", "8", None, DIP8, "through-hole; " + RV),
               ("SOIC-8", "LT1027CS8", "8", None, SOIC8, RV)],
    "LTC6655-5": [("MSOP-8", "LTC6655BHMS8-5", "8", None, MSOP8, RV)],
}


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lines = ["-- Terra EDA Library - ADI/LT precision voltage references",
             f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL.", "",
             "BEGIN TRANSACTION;", ""]
    seen, needs_work = set(), []
    for value, base in BASE.items():
        for v in VARIANTS[value]:
            package, mpn, pin_count, ksym, kfp, note = v[:6]
            extra = v[6] if len(v) > 6 else {}
            uid = f"Analog_Devices-{mpn}"
            if uid in seen:
                raise SystemExit(f"duplicate unique_id: {uid}")
            seen.add(uid)
            pkgtoken = re.sub(r"[^a-z0-9]+", "-", package.lower()).strip("-")
            row = {**DEFAULTS, **base, "unique_id": uid,
                   "part_locator": f"voltage-reference-{value.lower()}-{pkgtoken}",
                   "mpn": mpn, "variant": package, "package": package, "value": value,
                   "description": f"{base['description']}, {package}",
                   "kicad_symbol": ksym, "kicad_footprint": kfp, "pin_count": pin_count,
                   **extra}
            if ksym is None or kfp is None:
                needs_work.append(f"{value} {package}: {note}")
            vals = ", ".join(sql(row.get(c)) for c in COLS)
            lines.append(f"INSERT INTO voltage_reference ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(seen)} rows across {len(BASE)} parts")
    if needs_work:
        print(f"  {len(needs_work)} row(s) need work (NULL symbol):")
        for w in needs_work:
            print(f"    - {w}")


if __name__ == "__main__":
    main()
