"""Pin tables for the custom led_drivers DIP symbols (Renesas/Intersil ICM7218A-D).

KiCad ships no ICM7218 symbol. Pinouts are from the Renesas ICM7218 data sheet,
FN3159 Rev 4.00 (May 2016), "Pin Configurations" (pp.2-3). Write the symbols with

    python3 tools/make_dip_symbol.py db/tables/led_drivers/_pinouts.py \\
        kicad_symbols/terra_symbols_led_drivers.kicad_sym

There are four pinouts. A and C are common-anode (segment drivers sink, digit
drivers source); B and D are common-cathode, with the digit and segment pins on
different package pins. A/B are the sequential versions (8 data inputs ID0-ID7 plus
WRITE and MODE); C/D are random-access (4 data inputs, a decimal-point input, three
digit-address inputs and a three-level HEXA/CODE B/SHUTDOWN input on pin 9).

The data sheet's C/D pin-description table lists DA0-DA2 as "10, 6, 5" and ID0-ID3
as "14, 13, 11, 12"; the pin-configuration drawings and the A/B table (ID0-ID3 =
12, 11, 13, 14) show those lists are MSB-first. The drawings are followed here:
DA0=5, DA1=6, DA2=10, ID0=12, ID1=11, ID2=13, ID3=14.

Layout: data inputs top-left, controls below (the long three-level pin-9 name sits
opposite the gap between segment and digit outputs); segment outputs a-g, DP top-right,
digit outputs 1-8 below; VDD on top, VSS at the bottom.
"""

DIP28W = "Package_DIP:DIP-28_W15.24mm"
DS = "${TERRA_EDA_LIB}/datasheets/renesas/icm7218.pdf"

# Output pins shared by each display polarity.
_CA_OUT = {  # common anode (ICM7218A, ICM7218C)
    1: ("SEGc", "out"), 2: ("SEGe", "out"), 3: ("SEGb", "out"), 4: ("DP", "out"),
    15: ("DIGIT1", "out"), 16: ("DIGIT2", "out"), 17: ("DIGIT5", "out"),
    18: ("DIGIT8", "out"), 20: ("DIGIT4", "out"), 21: ("DIGIT7", "out"),
    22: ("DIGIT6", "out"), 23: ("DIGIT3", "out"), 24: ("SEGf", "out"),
    25: ("SEGd", "out"), 26: ("SEGg", "out"), 27: ("SEGa", "out"),
}
_CC_OUT = {  # common cathode (ICM7218B, ICM7218D)
    1: ("DIGIT4", "out"), 2: ("DIGIT6", "out"), 3: ("DIGIT3", "out"),
    4: ("DIGIT1", "out"), 15: ("DP", "out"), 16: ("SEGa", "out"),
    17: ("SEGb", "out"), 18: ("SEGd", "out"), 20: ("SEGc", "out"),
    21: ("SEGe", "out"), 22: ("SEGf", "out"), 23: ("SEGg", "out"),
    24: ("DIGIT8", "out"), 25: ("DIGIT2", "out"), 26: ("DIGIT5", "out"),
    27: ("DIGIT7", "out"),
}
_PWR = {19: ("VDD", "pwr"), 28: ("VSS", "pwr")}

# Sequential-access inputs (ICM7218A, ICM7218B). ID4-ID7 double as the control
# word when MODE is high.
_SEQ_IN = {
    5: ("ID6/HEXA/~{CODEB}", "in"), 6: ("ID5/~{DECODE}", "in"),
    7: ("ID7/DATA_COMING", "in"), 8: ("~{WRITE}", "in"), 9: ("MODE", "in"),
    10: ("ID4/~{SHDN}", "in"), 11: ("ID1", "in"), 12: ("ID0", "in"),
    13: ("ID2", "in"), 14: ("ID3", "in"),
}
# Random-access inputs (ICM7218C, ICM7218D).
_RND_IN = {
    5: ("DA0", "in"), 6: ("DA1", "in"), 7: ("ID7/DP", "in"), 8: ("~{WRITE}", "in"),
    9: ("HEXA/CODEB/~{SHDN}", "in"), 10: ("DA2", "in"), 11: ("ID1", "in"),
    12: ("ID0", "in"), 13: ("ID2", "in"), 14: ("ID3", "in"),
}

_RIGHT = ["SEGa", "SEGb", "SEGc", "SEGd", "SEGe", "SEGf", "SEGg", "DP", None,
          "DIGIT1", "DIGIT2", "DIGIT3", "DIGIT4", "DIGIT5", "DIGIT6", "DIGIT7",
          "DIGIT8"]
_SEQ_LEFT = ["ID0", "ID1", "ID2", "ID3", "ID4/~{SHDN}", "ID5/~{DECODE}",
             "ID6/HEXA/~{CODEB}", "ID7/DATA_COMING", None, "MODE", "~{WRITE}"]
_RND_LEFT = ["ID0", "ID1", "ID2", "ID3", "ID7/DP", None, "~{WRITE}", None,
             "HEXA/CODEB/~{SHDN}", None, "DA0", "DA1", "DA2"]

_KW = "LED display driver 7-segment 8-digit multiplexed hexadecimal Code B ICM7218"


def _pinout(inputs, outputs, left, polarity, access):
    return dict(
        pins={**inputs, **outputs, **_PWR},
        left=left, right=_RIGHT, top=["VDD"], bottom=["VSS"], footprint=DIP28W,
        width=25.4,
        datasheet=DS,
        description=f"8-digit multiplexed LED display decoder/driver, {polarity}, "
                    f"{access}, hexadecimal/Code B decode, 5 V, CERDIP-28",
        keywords=f"{_KW} {polarity}")


PINOUTS = {
    "ICM7218A": _pinout(_SEQ_IN, _CA_OUT, _SEQ_LEFT, "common anode",
                        "sequential access with no-decode mode"),
    "ICM7218B": _pinout(_SEQ_IN, _CC_OUT, _SEQ_LEFT, "common cathode",
                        "sequential access with no-decode mode"),
    "ICM7218C": _pinout(_RND_IN, _CA_OUT, _RND_LEFT, "common anode",
                        "random access"),
    "ICM7218D": _pinout(_RND_IN, _CC_OUT, _RND_LEFT, "common cathode",
                        "random access"),
}
