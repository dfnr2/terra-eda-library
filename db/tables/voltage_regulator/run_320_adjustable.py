#!/usr/bin/env python3
"""Classic adjustable ("programmable") linear regulators, through-hole.

LM317 (TO-220), LM317L (TO-92), LM317HV, LM337, LM338, LM350 (TO-220) and the
uA723 precision regulator (DIP-14). Each part is the single Active through-hole
orderable chosen in plans/voltage-regulator-th-classics.md:

- LM317 TO-220 comes from onsemi (LM317TG): TI's only TO-220 LM317 (LM317KCS /
  LM317KCSE3) is NOT RECOMMENDED FOR NEW DESIGNS on ti.com.
- LM723 DIP-14 is TI's uA723CN: the LM723 product folder now orders only the
  TO-100 can, while uA723 (same 14-pin pinout) is Active in PDIP.

The three-terminal parts are floating regulators: they are specified by input-output
differential, not absolute input voltage, so input_voltage_min/max stay NULL and the
differential range is in the description. Specs are the datasheet's 25 degC limits.

Symbols: stock Regulator_Linear where the pin map matches (checked by
_vreg.check_pinouts). TI's LM317L LP (TO-92) package is pinned IN-OUT-ADJ, the
reverse of the stock LM317L_TO92 (ADJ-OUT-IN, the National/onsemi Z-package order),
so it uses terra_symbols_voltage_regulator:LM317LxLP. LM338 has no stock symbol and
reuses LM350_TO220 (identical ADJ-OUT-IN TO-220 pin map).
"""
from pathlib import Path

from _vreg import DIP14, TO220, TO92, write

OUTPUT_FILE = Path(__file__).with_name("voltage_regulator_generated_320_adjustable.sql")
CREATED_BY = Path(__file__).name
TI_DS = "${TERRA_EDA_LIB}/datasheets/ti/"
ON_DS = "${TERRA_EDA_LIB}/datasheets/onsemi/"

ROWS = [
    dict(unique_id="onsemi-LM317TG", mpn="LM317TG", manufacturer="onsemi", value="LM317",
         part_locator="reg-adj-1.2-37v-1.5a-to220", package="TO-220",
         description="onsemi LM317 1.5A adjustable positive three-terminal linear regulator, "
                     "1.2-37V out, VI-VO 3-40V, 0 to 125°C, TO-220",
         datasheet=ON_DS + "lm317-d.pdf",
         manufacturer_link="https://www.onsemi.com/products/standard-products/ldo-voltage-regulators/lm317",
         kicad_symbol="Regulator_Linear:LM317_TO-220", kicad_footprint=TO220,
         pinout="ADJ-OUT-IN", pin_count="3",
         temp_operating_min=0.0, temp_operating_max=125.0,
         output_voltage_min=1.2, output_voltage_max=37.0, output_current="1.5A",
         quiescent_current="ADJ pin 50µA typ, 100µA max; min load 3.5mA typ, 10mA max (VI-VO=40V)",
         output_noise="0.003% of VO rms (10Hz-10kHz)",
         psrr="65dB typ; 80dB typ, 66dB min with 10µF CADJ (120Hz)",
         line_regulation="0.01%/V typ, 0.04%/V max (VI-VO 3-40V, 25°C)",
         load_regulation="5mV typ, 25mV max (VO<=5V); 0.1% typ, 0.5% max (VO>=5V); 10mA-1.5A, 25°C",
         accuracy="VREF 1.2-1.3V (1.25V typ)",
         features="current-limit,thermal-shutdown,safe-area-protection,floating"),
    dict(unique_id="Texas_Instruments-LM317LCLP", mpn="LM317LCLP", manufacturer="Texas Instruments",
         value="LM317L", part_locator="reg-adj-1.25-37v-100ma-to92", package="TO-92",
         description="Texas Instruments LM317L 100mA adjustable positive three-terminal linear "
                     "regulator, 1.25-37V out (32V on CSO:SHE die), VI-VO 2.5-37V, 0 to 125°C, "
                     "TO-92 (LP: 1=IN 2=OUT 3=ADJ)",
         datasheet=TI_DS + "lm317l.pdf", manufacturer_link="https://www.ti.com/product/LM317L",
         kicad_symbol="terra_symbols_voltage_regulator:LM317LxLP", kicad_footprint=TO92,
         pinout="IN-OUT-ADJ", pin_count="3",
         temp_operating_min=0.0, temp_operating_max=125.0,
         output_voltage_min=1.25, output_voltage_max=37.0, output_current="100mA",
         quiescent_current="ADJ pin 50µA typ, 100µA max; min load 3.5mA typ, 5mA max (VI-VO=35V)",
         output_noise="10µV/V of VO (10Hz-10kHz)",
         psrr="55dB typ; 80dB typ, 66dB min with 10µF CADJ (120Hz)",
         line_regulation="0.01%/V typ, 0.02%/V max (VI-VO 5-35V, 25°C)",
         load_regulation="25mV typ (VO<=5V); 5mV/V typ (VO>=5V); 2.5-100mA, 25°C",
         accuracy="VREF 1.2-1.3V (1.25V typ)",
         features="current-limit,thermal-shutdown,floating"),
    dict(unique_id="Texas_Instruments-LM317HVT/NOPB", mpn="LM317HVT/NOPB", manufacturer="Texas Instruments",
         value="LM317HV", part_locator="reg-adj-1.25-57v-1.5a-to220", package="TO-220",
         description="Texas Instruments LM317HV 1.5A high-voltage adjustable positive three-terminal "
                     "linear regulator, 1.25-57V out, VI-VO 3-60V, 0 to 125°C, TO-220",
         datasheet=TI_DS + "lm317hv.pdf", manufacturer_link="https://www.ti.com/product/LM317HV",
         kicad_symbol="Regulator_Linear:LM317_TO-220", kicad_footprint=TO220,
         pinout="ADJ-OUT-IN", pin_count="3",
         temp_operating_min=0.0, temp_operating_max=125.0,
         output_voltage_min=1.25, output_voltage_max=57.0, output_current="1.5A",
         quiescent_current="ADJ pin 50µA typ, 100µA max; min load 3.5mA typ, 12mA max (VI-VO=60V)",
         output_noise="0.003% of VO rms (10Hz-10kHz)",
         psrr="65dB typ; 80dB typ, 66dB min with 10µF CADJ (120Hz)",
         line_regulation="0.01%/V typ, 0.04%/V max (VI-VO 3-60V, 25°C)",
         load_regulation="0.1% typ, 0.5% max (10mA-1.5A, 25°C)",
         accuracy="VREF 1.2-1.3V (1.25V typ)",
         features="current-limit,thermal-shutdown,floating,high-voltage"),
    dict(unique_id="Texas_Instruments-LM337KCSE3", mpn="LM337KCSE3", manufacturer="Texas Instruments",
         value="LM337", part_locator="reg-adj-neg1.2-37v-1.5a-to220", package="TO-220",
         description="Texas Instruments LM337 1.5A adjustable negative three-terminal linear "
                     "regulator, -1.2 to -37V out, VI-VO -3 to -40V, 0 to 125°C, TO-220",
         datasheet=TI_DS + "lm337.pdf", manufacturer_link="https://www.ti.com/product/LM337",
         kicad_symbol="Regulator_Linear:LM337_TO220", kicad_footprint=TO220,
         pinout="ADJ-IN-OUT", pin_count="3",
         temp_operating_min=0.0, temp_operating_max=125.0,
         output_voltage_min=-37.0, output_voltage_max=-1.2, output_current="1.5A",
         quiescent_current="ADJ pin 65µA typ, 100µA max; min load 2.5mA typ, 10mA max (|VI-VO|<=40V)",
         output_noise="0.003% of VO rms (10Hz-10kHz)",
         psrr="60dB typ; 77dB typ, 66dB min with 10µF CADJ (120Hz)",
         line_regulation="0.01%/V typ, 0.04%/V max (VI-VO -3 to -40V, 25°C)",
         load_regulation="50mV max (|VO|<=5V); 0.3% typ, 1% max (|VO|>=5V); 10mA-1.5A, 25°C",
         accuracy="VREF -1.213 to -1.287V (-1.25V typ) at 25°C",
         features="current-limit,thermal-shutdown,safe-area-protection,floating"),
    dict(unique_id="Texas_Instruments-LM338T/NOPB", mpn="LM338T/NOPB", manufacturer="Texas Instruments",
         value="LM338", part_locator="reg-adj-1.2-32v-5a-to220", package="TO-220",
         description="Texas Instruments LM338 5A adjustable positive three-terminal linear "
                     "regulator, 1.2-32V out, VI-VO 3-40V, 0 to 125°C, TO-220",
         datasheet=TI_DS + "lm338.pdf", manufacturer_link="https://www.ti.com/product/LM338",
         kicad_symbol="Regulator_Linear:LM350_TO220", kicad_footprint=TO220,
         pinout="ADJ-OUT-IN", pin_count="3",
         temp_operating_min=0.0, temp_operating_max=125.0,
         output_voltage_min=1.2, output_voltage_max=32.0, output_current="5A",
         quiescent_current="ADJ pin 45µA typ, 100µA max; min load 3.5mA typ, 10mA max (VI-VO=35V)",
         output_noise="0.003% of VO rms (10Hz-10kHz)",
         psrr="60dB typ; 75dB typ, 60dB min with 10µF CADJ (120Hz)",
         line_regulation="0.005%/V typ, 0.03%/V max (VI-VO 3-35V, 25°C)",
         load_regulation="0.1% typ, 0.5% max (10mA-5A, 25°C)",
         accuracy="VREF 1.19-1.29V (1.24V typ)",
         features="current-limit,time-dependent-current-limit,thermal-shutdown,safe-area-protection,floating"),
    dict(unique_id="Texas_Instruments-LM350T/NOPB", mpn="LM350T/NOPB", manufacturer="Texas Instruments",
         value="LM350", part_locator="reg-adj-1.2-33v-3a-to220", package="TO-220",
         description="Texas Instruments LM350 3A adjustable positive three-terminal linear "
                     "regulator, 1.2-33V out, VI-VO 3-35V, 0 to 125°C, TO-220",
         datasheet=TI_DS + "lm350-n.pdf", manufacturer_link="https://www.ti.com/product/LM350-N",
         kicad_symbol="Regulator_Linear:LM350_TO220", kicad_footprint=TO220,
         pinout="ADJ-OUT-IN", pin_count="3",
         temp_operating_min=0.0, temp_operating_max=125.0,
         output_voltage_min=1.2, output_voltage_max=33.0, output_current="3A",
         quiescent_current="ADJ pin 50µA typ, 100µA max; min load 3.5mA typ, 10mA max (VI-VO=35V)",
         output_noise="0.001% of VO rms (10Hz-10kHz)",
         psrr="65dB typ; 86dB typ, 66dB min with 10µF CADJ (120Hz)",
         line_regulation="0.005%/V typ, 0.03%/V max (VI-VO 3-35V, 25°C)",
         load_regulation="0.1% typ, 0.5% max (10mA-3A, 25°C)",
         accuracy="VREF 1.20-1.30V (1.25V typ)",
         features="current-limit,thermal-shutdown,safe-area-protection,floating"),
    dict(unique_id="Texas_Instruments-UA723CN", mpn="UA723CN", manufacturer="Texas Instruments",
         value="uA723", part_locator="reg-adj-2-37v-150ma-dip14", package="DIP-14",
         description="Texas Instruments uA723 precision adjustable voltage regulator (723), "
                     "2-37V out, 150mA without external pass transistor, VI 9.5-40V, "
                     "VC-VO 3-38V, 0 to 70°C, DIP-14",
         datasheet=TI_DS + "ua723.pdf", manufacturer_link="https://www.ti.com/product/UA723",
         kicad_symbol="Regulator_Linear:LM723_DIP14", kicad_footprint=DIP14,
         pin_count="14",
         temp_operating_min=0.0, temp_operating_max=70.0,
         output_voltage_min=2.0, output_voltage_max=37.0, output_current="150mA",
         input_voltage_min=9.5, input_voltage_max=40.0,
         quiescent_current="standby 2.3mA typ, 4mA max (VI=30V, IO=0)",
         output_noise="20µV (100Hz-10kHz, Cref=0); 2.5µV with Cref=5µF",
         psrr="74dB typ; 86dB typ with Cref=5µF (50Hz-10kHz)",
         line_regulation="1mV/V typ, 5mV/V max (VI 12-40V, 25°C)",
         load_regulation="-0.3mV/V typ, -2mV/V max (25°C)",
         accuracy="VREF 6.8-7.5V (7.15V typ)",
         features="adjustable-current-limit,external-pass-transistor,positive-or-negative,"
                  "series-shunt-switching-floating"),
]

COMMON_KEYWORDS = "linear-regulator,adjustable,programmable"


def main():
    rows = []
    for r in ROWS:
        neg = r["output_voltage_max"] < 0
        three_pin = r["pin_count"] == "3"
        kw = [COMMON_KEYWORDS, "negative" if neg else "positive",
              "three-terminal" if three_pin else "precision-reference",
              r["output_current"].lower(), r["value"].lower(), r["package"].lower()]
        rows.append({**r, "regulator_type": "linear", "output_voltage": "adjustable",
                     "adjustable": "yes", "keywords": ",".join(kw)})
    write(OUTPUT_FILE, "adjustable linear regulators (TO-220 / TO-92 / DIP-14)", CREATED_BY, rows)


if __name__ == "__main__":
    main()
