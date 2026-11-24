"""Pin tables for the custom ic_drivers symbols (MC1488/MC1489 RS-232 line drivers).

KiCad has no symbol for either chip. Pinouts are from TI's data sheets, SLLS094C
(MC1488, SN75188) and SLLS095D (MC1489/A, SN75189/A), and are the same in every
14-pin package. Write the symbols with

    python3 tools/make_dip_symbol.py db/tables/ic_drivers/_pinouts.py \\
        kicad_symbols/terra_symbols_ic_drivers.kicad_sym

Layout: logic or line inputs on the left, outputs on the right, each output beside
its gate's last input; VCC+ on top, GND and VCC- at the bottom. The receivers'
response-control (CONT) pins are passive: they take an optional capacitor or
threshold-shift resistor and are usually left open.
"""

DIP14N = "Package_DIP:DIP-14_W7.62mm"

MC1488 = {
    1: ("VCC-", "pwr"), 2: ("1A", "in"), 3: ("1Y", "out"), 4: ("2A", "in"),
    5: ("2B", "in"), 6: ("2Y", "out"), 7: ("GND", "pwr"), 8: ("3Y", "out"),
    9: ("3A", "in"), 10: ("3B", "in"), 11: ("4Y", "out"), 12: ("4A", "in"),
    13: ("4B", "in"), 14: ("VCC+", "pwr"),
}

MC1489 = {
    1: ("1A", "in"), 2: ("1CONT", "pas"), 3: ("1Y", "out"), 4: ("2A", "in"),
    5: ("2CONT", "pas"), 6: ("2Y", "out"), 7: ("GND", "pwr"), 8: ("3Y", "out"),
    9: ("3CONT", "pas"), 10: ("3A", "in"), 11: ("4Y", "out"), 12: ("4CONT", "pas"),
    13: ("4A", "in"), 14: ("VCC", "pwr"),
}

PINOUTS = {
    "MC1488": dict(
        pins=MC1488,
        left=["1A", None, None, "2A", "2B", None, "3A", "3B", None, "4A", "4B"],
        right=["1Y", None, None, None, "2Y", None, None, "3Y", None, None, "4Y"],
        top=["VCC+"], bottom=["GND", "VCC-"], footprint=DIP14N,
        description="Quadruple RS-232 line driver: one inverter and three 2-input "
                    "NAND drivers, +/-7.5 to 15 V supplies",
        keywords="RS-232 EIA-232 V.28 line driver quad 1488 MC1488 SN75188"),
    "MC1489": dict(
        pins=MC1489,
        left=["1A", "1CONT", None, "2A", "2CONT", None, "3A", "3CONT", None, "4A",
              "4CONT"],
        right=["1Y", None, None, "2Y", None, None, "3Y", None, None, "4Y"],
        top=["VCC"], bottom=["GND"], footprint=DIP14N,
        description="Quadruple RS-232 line receiver with hysteresis and "
                    "response-control inputs, 5 V supply",
        keywords="RS-232 EIA-232 V.28 line receiver quad 1489 MC1489 MC1489A SN75189 "
                 "SN75189A"),
}
