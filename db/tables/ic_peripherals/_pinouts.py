"""Pin tables for the custom ic_peripherals symbols.

One symbol per distinct pinout, named after the first chip that uses it. Chips whose
pinout matches a stock KiCad symbol pin for pin, active-low bars included, use the
stock symbol instead (see each generator). Pinouts are transcribed from each chip's
data sheet, named in the generator docstring. Write the symbols with

    python3 tools/make_dip_symbol.py db/tables/ic_peripherals/_pinouts.py \\
        kicad_symbols/terra_symbols_ic_peripherals.kicad_sym

Layout: CPU side on the left (data bus D0 first, then register selects, chip selects,
strobes, reset and interrupt), device side on the right (ports, serial lines, timer
pins) in pin order unless listed; supplies top and bottom.
Pin types: see tools/make_dip_symbol.py.
"""
import re

DIP24 = "Package_DIP:DIP-24_W15.24mm"
DIP28 = "Package_DIP:DIP-28_W15.24mm"
DIP40 = "Package_DIP:DIP-40_W15.24mm"
DIP48 = "Package_DIP:DIP-48_W15.24mm"
DIP16N = "Package_DIP:DIP-16_W7.62mm"
DIP18N = "Package_DIP:DIP-18_W7.62mm"
DIP20N = "Package_DIP:DIP-20_W7.62mm"
DIP24N = "Package_DIP:DIP-24_W7.62mm"

PWR = {"pwr"}


def _a(first, names, ptype="bidi"):
    """Consecutive pins first, first+1, ... named in order."""
    return {first + i: (n, ptype) for i, n in enumerate(names)}


def _bus(prefix, lo, hi):
    return [f"{prefix}{i}" for i in range(lo, hi + 1)]


def _per(pins, left, footprint, description, keywords, right=None, data="D",
         width=20.32):
    """Build a pinout entry.

    left: CPU-side names after the data bus (None = gap). right: device-side names;
    default is every remaining signal pin in pin order. Supplies go top (VCC/VDD) and
    bottom (VSS/GND), stacked by name.
    """
    names = [n for n, t in pins.values() if t not in PWR and t != "nc"]
    hits = [(int(m.group(1)), n) for n in names
            if (m := re.match(rf"{data}(\d+)(/|$)", n))]
    dbus = [n for _, n in sorted(hits)]
    lhs = dbus + ([None] if dbus and left else []) + left
    if right is None:
        used = set(lhs)
        right = [n for _, (n, t) in sorted(pins.items())
                 if t not in PWR and t != "nc" and n not in used]
    pwr = list(dict.fromkeys(n for n, t in pins.values() if t in PWR))
    top = [n for n in pwr if not n.startswith(("VSS", "GND"))]
    bottom = [n for n in pwr if n.startswith(("VSS", "GND"))]
    return dict(pins=pins, left=lhs, right=right, top=top, bottom=bottom, width=width,
                footprint=footprint, description=description, keywords=keywords)


# --- MOS Technology 6500 family (1982-83 MOS/Commodore Data Catalog) ---------------
# Names as printed by MOS (PHI2, ~{RES}); the WDC CMOS parts are pin-for-pin the same
# but carry WDC's B-suffix names, so they get their own symbols.

_PORTS_6520 = {**_a(2, _bus("PA", 0, 7)), **_a(10, _bus("PB", 0, 7)),
               18: ("CB1", "in"), 19: ("CB2", "bidi"), 39: ("CA2", "bidi"),
               40: ("CA1", "in")}
_DATA_6520 = _a(26, [f"D{i}" for i in range(7, -1, -1)])

# 6520 PIA, book 2-46.
M6520 = {
    1: ("VSS", "pwr"), **_PORTS_6520, 20: ("VCC", "pwr"), 21: ("R/~{W}", "in"),
    22: ("CS0", "in"), 23: ("~{CS2}", "in"), 24: ("CS1", "in"), 25: ("PHI2", "in"),
    **_DATA_6520, 34: ("~{RES}", "in"), 35: ("RS1", "in"), 36: ("RS0", "in"),
    37: ("~{IRQB}", "oc"), 38: ("~{IRQA}", "oc"),
}

# 6522 VIA, book 2-50.
M6522 = {
    1: ("VSS", "pwr"), **_PORTS_6520, 20: ("VCC", "pwr"), 21: ("~{IRQ}", "oc"),
    22: ("R/~{W}", "in"), 23: ("~{CS2}", "in"), 24: ("CS1", "in"), 25: ("PHI2", "in"),
    **_DATA_6520, 34: ("~{RES}", "in"), 35: ("RS3", "in"), 36: ("RS2", "in"),
    37: ("RS1", "in"), 38: ("RS0", "in"),
}

# 6530 RRIOT, book 2-106 (PA0 on pin 2, PA1-PA7 on pins 40 down to 34).
M6530 = {
    1: ("VSS", "pwr"), 2: ("PA0", "bidi"), 3: ("PHI2", "in"), 4: ("RS0", "in"),
    **_a(5, ["A9", "A8", "A7", "A6"], "in"), 9: ("R/~{W}", "in"),
    **_a(10, ["A5", "A4", "A3", "A2", "A1", "A0"], "in"), 16: ("~{RES}", "in"),
    17: ("~{IRQ}/PB7", "bidi"), 18: ("CS1/PB6", "bidi"), 19: ("CS2/PB5", "bidi"),
    20: ("VCC", "pwr"), **_a(21, ["PB4", "PB3", "PB2", "PB1", "PB0"]),
    **_a(26, [f"DB{i}" for i in range(7, -1, -1)]),
    **_a(34, [f"PA{i}" for i in range(7, 0, -1)]),
}

# 6532 RIOT, book 2-107 (pin 20 printed VDD, the +5V rail).
M6532 = {
    1: ("VSS", "pwr"), **_a(2, ["A5", "A4", "A3", "A2", "A1", "A0"], "in"),
    **_a(8, _bus("PA", 0, 7)), **_a(16, ["PB7", "PB6", "PB5", "PB4"]), 20: ("VDD", "pwr"),
    **_a(21, ["PB3", "PB2", "PB1", "PB0"]), 25: ("~{IRQ}", "oc"),
    **_a(26, [f"DB{i}" for i in range(7, -1, -1)]), 34: ("~{RES}", "in"),
    35: ("R/~{W}", "in"), 36: ("~{RS}", "in"), 37: ("~{CS2}", "in"), 38: ("CS1", "in"),
    39: ("PHI2", "in"), 40: ("A6", "in"),
}

# 6551 ACIA, book 2-129.
M6551 = {
    1: ("GND", "pwr"), 2: ("CS0", "in"), 3: ("~{CS1}", "in"), 4: ("~{RES}", "in"),
    5: ("RxC", "bidi"), 6: ("XTAL1", "in"), 7: ("XTAL2", "out"), 8: ("~{RTS}", "out"),
    9: ("~{CTS}", "in"), 10: ("TxD", "out"), 11: ("~{DTR}", "out"), 12: ("RxD", "in"),
    13: ("RS0", "in"), 14: ("RS1", "in"), 15: ("VCC", "pwr"), 16: ("~{DCD}", "in"),
    17: ("~{DSR}", "in"), **_a(18, _bus("DB", 0, 7)), 26: ("~{IRQ}", "oc"),
    27: ("PHI2", "in"), 28: ("R/~{W}", "in"),
}


def _wdc(pins, renames, irq_type=None):
    """A MOS pinout with WDC's printed names (and IRQ output type) substituted."""
    out = {}
    for n, (name, t) in pins.items():
        name = renames.get(name, name)
        if irq_type and name.startswith("IRQ"):
            t = irq_type
        out[n] = (name, t)
    return out


_WDC = {"VCC": "VDD", "GND": "VSS", "R/~{W}": "RWB", "~{CS2}": "CS2B", "~{RES}": "RESB",
        "~{IRQ}": "IRQB", "~{IRQA}": "IRQAB", "~{IRQB}": "IRQBB"}
W65C21 = _wdc(M6520, _WDC)  # IRQAB/IRQBB open drain on N and S (datasheet p. 15)
W65C22N = _wdc(M6522, _WDC, "oc")  # N: open-drain IRQB
W65C22S = _wdc(M6522, _WDC, "out")  # S: totem-pole IRQB
W65C51N = _wdc(M6551, {**_WDC, "~{CS1}": "CS1B", "XTAL1": "XTLI", "XTAL2": "XTLO",
                       "~{RTS}": "RTSB", "~{CTS}": "CTSB", "~{DTR}": "DTRB",
                       "~{DCD}": "DCDB", "~{DSR}": "DSRB",
                       **{f"DB{i}": f"D{i}" for i in range(8)}})

_L6520 = ["RS0", "RS1", "CS0", "CS1", "~{CS2}", "R/~{W}", "PHI2", "~{RES}", None,
          "~{IRQA}", "~{IRQB}"]
_L6522 = ["RS0", "RS1", "RS2", "RS3", "CS1", "~{CS2}", "R/~{W}", "PHI2", "~{RES}",
          "~{IRQ}"]
_R6520 = _bus("PA", 0, 7) + ["CA1", "CA2", None] + _bus("PB", 0, 7) + ["CB1", "CB2"]
_L6551 = ["RS0", "RS1", "CS0", "~{CS1}", "R/~{W}", "PHI2", "~{RES}", "~{IRQ}"]
_R6551 = ["TxD", "RxD", "RxC", None, "XTAL1", "XTAL2", None, "~{RTS}", "~{CTS}",
          "~{DTR}", "~{DSR}", "~{DCD}"]


def _ren(names, renames):
    return [None if n is None else renames.get(n, n) for n in names]


# --- Motorola 6800 family (1983 8-Bit Microprocessor & Peripheral Data) -------------

# MC6840 PTM, book 3-397. The stock Interface:MC6840 types D0-D7 as inputs.
MC6840 = {
    1: ("VSS", "pwr"), 2: ("~{G2}", "in"), 3: ("O2", "out"), 4: ("~{C2}", "in"),
    5: ("~{G3}", "in"), 6: ("O3", "out"), 7: ("~{C3}", "in"), 8: ("~{RESET}", "in"),
    9: ("~{IRQ}", "oc"), 10: ("RS0", "in"), 11: ("RS1", "in"), 12: ("RS2", "in"),
    13: ("R/~{W}", "in"), 14: ("VCC", "pwr"), 15: ("~{CS0}", "in"), 16: ("CS1", "in"),
    17: ("E", "in"), **_a(18, [f"D{i}" for i in range(7, -1, -1)]),
    26: ("~{G1}", "in"), 27: ("O1", "out"), 28: ("~{C1}", "in"),
}

# MC6847/MC6847Y VDG, book 3-469. Not a bus peripheral: DA/DD go to display RAM.
MC6847 = {
    1: ("VSS", "pwr"), 2: ("DD6", "in"), **_a(3, _bus("DD", 0, 5), "in"),
    9: ("CHB", "out"), 10: ("ϕB", "out"), 11: ("ϕA", "out"), 12: ("~{MS}", "in"),
    **_a(13, _bus("DA", 5, 8), "tri"), 17: ("VCC", "pwr"),
    **_a(18, _bus("DA", 9, 12), "tri"), **_a(22, _bus("DA", 0, 4), "tri"),
    27: ("GM2", "in"), 28: ("Y", "out"), 29: ("GM1", "in"), 30: ("GM0", "in"),
    31: ("~{INT}/EXT", "in"), 32: ("INV", "in"), 33: ("CLK", "in"), 34: ("~{A}/S", "in"),
    35: ("~{A}/G", "in"), 36: ("~{RP}", "out"), 37: ("~{FS}", "out"), 38: ("~{HS}", "out"),
    39: ("CSS", "in"), 40: ("DD7", "in"),
}

# MC6850 ACIA, book 3-494 (the stock Interface_UART:MC6850 drops the bar on ~{CS2})
# and MC6852 SSDA, book 3-506: same bus pins, different serial/control pins.
_ACIA_BUS = {
    1: ("VSS", "pwr"), 2: ("Rx Data", "in"), 3: ("Rx CLK", "in"), 4: ("Tx CLK", "in"),
    6: ("Tx Data", "out"), 7: ("~{IRQ}", "oc"), 11: ("RS", "in"), 12: ("VCC", "pwr"),
    13: ("R/~{W}", "in"), 14: ("E", "in"), **_a(15, [f"D{i}" for i in range(7, -1, -1)]),
    23: ("~{DCD}", "in"), 24: ("~{CTS}", "in"),
}
MC6850 = {**_ACIA_BUS, 5: ("~{RTS}", "out"), 8: ("CS0", "in"), 9: ("~{CS2}", "in"),
          10: ("CS1", "in")}
MC6852 = {**_ACIA_BUS, 5: ("SM/~{DTR}", "out"), 8: ("TUF", "out"),
          9: ("~{RESET}", "in"), 10: ("~{CS}", "in")}

# MC6854 ADLC, book 3-524 (pin 1 unlabelled in the drawing; VSS per the block diagram).
MC6854 = {
    1: ("VSS", "pwr"), 2: ("~{RTS}", "out"), 3: ("RxD", "in"), 4: ("RxC", "in"),
    5: ("TxC", "in"), 6: ("TxD", "out"), 7: ("~{IRQ}", "oc"), 8: ("~{RESET}", "in"),
    9: ("~{CS}", "in"), 10: ("RS0", "in"), 11: ("RS1", "in"), 12: ("R/~{W}", "in"),
    13: ("E", "in"), 14: ("VCC", "pwr"), **_a(15, [f"D{i}" for i in range(7, -1, -1)]),
    23: ("RDSR", "out"), 24: ("TDSR", "out"), 25: ("~{FLAG DET}", "out"),
    26: ("~{LOC/DTR}", "out"), 27: ("~{DCD}", "in"), 28: ("~{CTS}", "in"),
}

# --- Motorola 68000 family -----------------------------------------------------------
# The stock Interface:68230 and Interface:68681 drop every active-low bar.

# MC68230 PI/T, 1981 Microprocessors Data Manual, book 4-783.
MC68230 = {
    1: ("D5", "bidi"), 2: ("D6", "bidi"), 3: ("D7", "bidi"),
    **_a(4, _bus("PA", 0, 7)), 12: ("VCC", "pwr"), 13: ("H1", "in"), 14: ("H2", "bidi"),
    15: ("H3", "in"), 16: ("H4", "bidi"), **_a(17, _bus("PB", 0, 7)),
    25: ("RS5", "in"), 26: ("RS4", "in"), 27: ("RS3", "in"), 28: ("RS2", "in"),
    29: ("RS1", "in"), 30: ("PC0", "bidi"), 31: ("PC1", "bidi"), 32: ("PC2/TIN", "bidi"),
    33: ("PC3/TOUT", "bidi"), 34: ("PC4/~{DMAREQ}", "bidi"), 35: ("PC5/~{PIRQ}", "bidi"),
    36: ("PC6/~{PIACK}", "bidi"), 37: ("PC7/~{TIACK}", "bidi"), 38: ("VSS", "pwr"),
    39: ("~{RESET}", "in"), 40: ("CLK", "in"), 41: ("~{CS}", "in"),
    42: ("~{DTACK}", "tri"), 43: ("R/~{W}", "in"), **_a(44, _bus("D", 0, 4)),
}

# MC68901 MFP, January 1984 manual, p. 8-1.
MC68901 = {
    1: ("R/~{W}", "in"), **_a(2, _bus("RS", 1, 5), "in"), 7: ("TC", "in"),
    8: ("SO", "out"), 9: ("SI", "in"), 10: ("RC", "in"), 11: ("VCC", "pwr"),
    12: ("NC", "nc"), 13: ("TAO", "out"), 14: ("TBO", "out"), 15: ("TCO", "out"),
    16: ("TDO", "out"), 17: ("XTAL1", "in"), 18: ("XTAL2", "in"), 19: ("TAI", "in"),
    20: ("TBI", "in"), 21: ("~{RESET}", "in"), **_a(22, _bus("I", 0, 7)),
    30: ("~{TR}", "out"), 31: ("~{RR}", "out"), 32: ("~{IRQ}", "oc"),
    33: ("~{IEO}", "out"), 34: ("~{IEI}", "in"), 35: ("CLK", "in"), 36: ("GND", "pwr"),
    **_a(37, _bus("D", 0, 7)), 45: ("~{IACK}", "in"), 46: ("~{DTACK}", "tri"),
    47: ("~{DS}", "in"), 48: ("~{CS}", "in"),
}

# MC68681 DUART, September 1985 manual, p. 6-1.
MC68681 = {
    1: ("RS1", "in"), 2: ("IP3", "in"), 3: ("RS2", "in"), 4: ("IP1", "in"),
    5: ("RS3", "in"), 6: ("RS4", "in"), 7: ("IP0", "in"), 8: ("R/~{W}", "in"),
    9: ("~{DTACK}", "oc"), 10: ("RxDB", "in"), 11: ("TxDB", "out"), 12: ("OP1", "out"),
    13: ("OP3", "out"), 14: ("OP5", "out"), 15: ("OP7", "out"), 16: ("D1", "bidi"),
    17: ("D3", "bidi"), 18: ("D5", "bidi"), 19: ("D7", "bidi"), 20: ("GND", "pwr"),
    21: ("~{IRQ}", "oc"), 22: ("D6", "bidi"), 23: ("D4", "bidi"), 24: ("D2", "bidi"),
    25: ("D0", "bidi"), 26: ("OP6", "out"), 27: ("OP4", "out"), 28: ("OP2", "out"),
    29: ("OP0", "out"), 30: ("TxDA", "out"), 31: ("RxDA", "in"), 32: ("X1/CLK", "in"),
    33: ("X2", "in"), 34: ("~{RESET}", "in"), 35: ("~{CS}", "in"), 36: ("IP2", "in"),
    37: ("~{IACK}", "in"), 38: ("IP5", "in"), 39: ("IP4", "in"), 40: ("VCC", "pwr"),
}

# --- Zilog Z80 family (1989 Z80 Family Data Book; NMOS and CMOS DIPs identical) -----
# The PIO uses the stock Interface:Z8420.

# Z8430/Z84C30 CTC, book 97.
Z8430 = {
    **_a(1, _bus("D", 4, 7)), 5: ("GND", "pwr"), 6: ("~{RD}", "in"),
    7: ("ZC/TO0", "out"), 8: ("ZC/TO1", "out"), 9: ("ZC/TO2", "out"),
    10: ("~{IORQ}", "in"), 11: ("IEO", "out"), 12: ("~{INT}", "oc"), 13: ("IEI", "in"),
    14: ("~{M1}", "in"), 15: ("CLK", "in"), 16: ("~{CE}", "in"), 17: ("~{RESET}", "in"),
    18: ("CS0", "in"), 19: ("CS1", "in"), 20: ("CLK/TRG3", "in"), 21: ("CLK/TRG2", "in"),
    22: ("CLK/TRG1", "in"), 23: ("CLK/TRG0", "in"), 24: ("+5V", "pwr"),
    **_a(25, _bus("D", 0, 3)),
}

# Z8440/1/2 SIO/0, SIO/1, SIO/2 and Z8470 DART, book 113 and 137. Pins 25-29 carry
# the bonding option; pin 11 (and 29) are SYNC on the SIO, RI on the DART.
_SIO = {
    1: ("D1", "bidi"), 2: ("D3", "bidi"), 3: ("D5", "bidi"), 4: ("D7", "bidi"),
    5: ("~{INT}", "oc"), 6: ("IEI", "in"), 7: ("IEO", "out"), 8: ("~{M1}", "in"),
    9: ("+5V", "pwr"), 10: ("~{W/RDYA}", "out"), 11: ("~{SYNCA}", "bidi"),
    12: ("RxDA", "in"), 13: ("~{RxCA}", "in"), 14: ("~{TxCA}", "in"), 15: ("TxDA", "out"),
    16: ("~{DTRA}", "out"), 17: ("~{RTSA}", "out"), 18: ("~{CTSA}", "in"),
    19: ("~{DCDA}", "in"), 20: ("CLK", "in"), 21: ("~{RESET}", "in"),
    22: ("~{DCDB}", "in"), 23: ("~{CTSB}", "in"), 24: ("~{RTSB}", "out"),
    30: ("~{W/RDYB}", "out"), 31: ("GND", "pwr"), 32: ("~{RD}", "in"),
    33: ("C/~{D}", "in"), 34: ("B/~{A}", "in"), 35: ("~{CE}", "in"), 36: ("~{IORQ}", "in"),
    37: ("D6", "bidi"), 38: ("D4", "bidi"), 39: ("D2", "bidi"), 40: ("D0", "bidi"),
}
Z8442 = {**_SIO, 25: ("~{DTRB}", "out"), 26: ("TxDB", "out"), 27: ("~{TxCB}", "in"),
         28: ("~{RxCB}", "in"), 29: ("RxDB", "in")}  # SIO/2: no ~{SYNCB}
Z8441 = {**_SIO, 25: ("TxDB", "out"), 26: ("~{TxCB}", "in"), 27: ("~{RxCB}", "in"),
         28: ("RxDB", "in"), 29: ("~{SYNCB}", "bidi")}  # SIO/1: no ~{DTRB}
Z8440 = {**_SIO, 25: ("~{DTRB}", "out"), 26: ("TxDB", "out"), 27: ("~{RxTxCB}", "in"),
         28: ("RxDB", "in"), 29: ("~{SYNCB}", "bidi")}  # SIO/0: TxCB+RxCB bonded
Z8470 = {**Z8440, 11: ("~{RIA}", "in"), 29: ("~{RIB}", "in")}

# Z8410/Z84C10 DMA, book 57.
Z8410 = {
    **_a(1, ["A5", "A4", "A3", "A2", "A1", "A0"], "tri"), 7: ("CLK", "in"),
    8: ("~{WR}", "bidi"), 9: ("~{RD}", "bidi"), 10: ("~{IORQ}", "bidi"),
    11: ("+5V", "pwr"), 12: ("~{MREQ}", "tri"), 13: ("~{BAO}", "out"),
    14: ("~{BAI}", "in"), 15: ("~{BUSREQ}", "bidi"), 16: ("~{CE}/~{WAIT}", "in"),
    **_a(17, [f"A{i}" for i in range(15, 7, -1)], "tri"), 25: ("RDY", "in"),
    26: ("~{M1}", "in"), 27: ("D7", "bidi"), 28: ("D6", "bidi"), 29: ("D5", "bidi"),
    30: ("GND", "pwr"), **_a(31, ["D4", "D3", "D2", "D1", "D0"]), 36: ("IEO", "out"),
    37: ("~{INT}/~{PULSE}", "oc"), 38: ("IEI", "in"), 39: ("A7", "tri"),
    40: ("A6", "tri"),
}

_LZ = ["~{CE}", "C/~{D}", "B/~{A}", "~{RD}", "~{IORQ}", "~{M1}", "CLK", "~{RESET}", None,
       "~{INT}", "IEI", "IEO"]
_RSIO_A = ["TxDA", "RxDA", "~{TxCA}", "~{RxCA}", "~{SYNCA}", "~{W/RDYA}", "~{RTSA}",
           "~{CTSA}", "~{DTRA}", "~{DCDA}", None]


def _sio_right(pins):
    """Channel A then channel B, keeping only the signals this bonding option has."""
    names = {n for n, _ in pins.values()}
    a = [n.replace("SYNCA", "RIA") if n and "~{RIA}" in names and "SYNCA" in n else n
         for n in _RSIO_A]
    b = ["TxDB", "RxDB", "~{TxCB}", "~{RxCB}", "~{RxTxCB}", "~{SYNCB}", "~{RIB}",
         "~{W/RDYB}", "~{RTSB}", "~{CTSB}", "~{DTRB}", "~{DCDB}"]
    return [n for n in a if n is None or n in names] + [n for n in b if n in names]


# --- RCA CDP1800 family (1982 RCA CMOS LSI Products) --------------------------------

# CDP1852/CDP1852C byte-wide I/O port, book 203 (pins 1 and 23 polarity set by MODE).
CDP1852 = {
    1: ("CS1/~{CS1}", "in"), 2: ("MODE", "in"), 3: ("DI0", "in"), 4: ("DO0", "tri"),
    5: ("DI1", "in"), 6: ("DO1", "tri"), 7: ("DI2", "in"), 8: ("DO2", "tri"),
    9: ("DI3", "in"), 10: ("DO3", "tri"), 11: ("CLOCK", "in"), 12: ("VSS", "pwr"),
    13: ("CS2", "in"), 14: ("~{CLEAR}", "in"), 15: ("DO4", "tri"), 16: ("DI4", "in"),
    17: ("DO5", "tri"), 18: ("DI5", "in"), 19: ("DO6", "tri"), 20: ("DI6", "in"),
    21: ("DO7", "tri"), 22: ("DI7", "in"), 23: ("~{SR}/SR", "out"), 24: ("VDD", "pwr"),
}

# CDP1853/CDP1853C 1-of-8 decoder, book 210.
CDP1853 = {
    1: ("CLOCK A", "in"), 2: ("N0", "in"), 3: ("N1", "in"),
    **_a(4, ["OUT 0", "OUT 1", "OUT 2", "OUT 3"], "out"), 8: ("VSS", "pwr"),
    **_a(9, ["OUT 7", "OUT 6", "OUT 5", "OUT 4"], "out"), 13: ("CE", "in"),
    14: ("N2", "in"), 15: ("CLOCK B", "in"), 16: ("VDD", "pwr"),
}

# CDP1854A/CDP1854AC UART, book 214, mode 1 (CDP1800 bus) names.
CDP1854 = {
    1: ("VDD", "pwr"), 2: ("MODE", "in"), 3: ("VSS", "pwr"), 4: ("~{CS2}", "in"),
    **_a(5, [f"R BUS {i}" for i in range(7, -1, -1)], "tri"), 13: ("~{INT}", "out"),
    14: ("FE", "out"), 15: ("PE/OE", "out"), 16: ("RSEL", "in"), 17: ("R CLOCK", "in"),
    18: ("TPB", "in"), 19: ("~{DA}", "out"), 20: ("SDI", "in"), 21: ("~{CLEAR}", "in"),
    22: ("~{THRE}", "out"), 23: ("CS1", "in"), 24: ("~{RTS}", "out"), 25: ("SDO", "out"),
    **_a(26, [f"T BUS {i}" for i in range(8)], "in"), 34: ("RD/~{WR}", "in"),
    35: ("CS3", "in"), 36: ("NC", "nc"), 37: ("~{PSI}", "in"), 38: ("~{ES}", "in"),
    39: ("~{CTS}", "in"), 40: ("T CLOCK", "in"),
}

# CDP1861C video display controller ("Pixie"), book 258.
CDP1861 = {
    1: ("~{CLK}", "in"), 2: ("~{DMAO}", "oc"), 3: ("~{INT}", "oc"), 4: ("TPA", "in"),
    5: ("TPB", "in"), 6: ("~{COMP SYNC}", "out"), 7: ("VIDEO", "out"),
    8: ("~{RESET}", "in"), 9: ("~{EFX}", "out"), 10: ("DISP ON", "in"),
    11: ("DISP OFF", "in"), 12: ("VSS", "pwr"), **_a(13, _bus("DI", 0, 7), "in"),
    21: ("SC0", "in"), 22: ("SC1", "in"), 23: ("~{CLEAR}", "out"), 24: ("VDD", "pwr"),
}

# --- TI 9900 family (1978 9900 Family Systems Design and Data Book) -----------------

# TMS9901 programmable systems interface, book 8-148.
TMS9901 = {
    1: ("~{RST1}", "in"), 2: ("CRUOUT", "in"), 3: ("CRUCLK", "in"), 4: ("CRUIN", "tri"),
    5: ("~{CE}", "in"), **_a(6, ["~{INT6}", "~{INT5}", "~{INT4}", "~{INT3}"], "in"),
    10: ("~{φ}", "in"), 11: ("~{INTREQ}", "out"),
    **_a(12, ["IC3", "IC2", "IC1", "IC0"], "out"), 16: ("VSS", "pwr"),
    17: ("~{INT1}", "in"), 18: ("~{INT2}", "in"), **_a(19, ["P6", "P5", "P4", "P3"]),
    23: ("~{INT15}/P7", "bidi"), 24: ("S4", "in"), 25: ("S3", "in"), 26: ("P2", "bidi"),
    **_a(27, [f"~{{INT{14 - i}}}/P{8 + i}" for i in range(8)]),
    35: ("S2", "in"), 36: ("S1", "in"), 37: ("P1", "bidi"), 38: ("P0", "bidi"),
    39: ("S0", "in"), 40: ("VCC", "pwr"),
}

# TMS9902 asynchronous communications controller, book 8-181.
TMS9902 = {
    1: ("~{INT}", "out"), 2: ("XOUT", "out"), 3: ("RIN", "in"), 4: ("CRUIN", "tri"),
    5: ("~{RTS}", "out"), 6: ("~{CTS}", "in"), 7: ("~{DSR}", "in"), 8: ("CRUOUT", "in"),
    9: ("VSS", "pwr"), **_a(10, ["S4", "S3", "S2", "S1", "S0"], "in"),
    15: ("CRUCLK", "in"), 16: ("~{φ}", "in"), 17: ("~{CE}", "in"), 18: ("VCC", "pwr"),
}

# TIM9904 (SN74LS362) four-phase clock generator, book 8-258. Two ground pins.
TIM9904 = {
    1: ("TANK 1", "in"), 2: ("TANK 2", "in"), 3: ("GND", "pwr"), 4: ("FFQ", "out"),
    5: ("FFD", "in"), 6: ("~{φ4} TTL", "out"), 7: ("~{φ3} TTL", "out"), 8: ("φ3", "out"),
    9: ("φ4", "out"), 10: ("GND", "pwr"), 11: ("φ2", "out"), 12: ("φ1", "out"),
    13: ("VDD", "pwr"), 14: ("~{φ1} TTL", "out"), 15: ("~{φ2} TTL", "out"),
    16: ("OSCOUT", "out"), 17: ("OSCIN", "in"), 18: ("XTAL 1", "in"),
    19: ("XTAL 2", "in"), 20: ("VCC", "pwr"),
}

# --- Intel 8080/8085 support (1981 Intel Component Data Catalog) -------------------

# 8212 8-bit I/O port, book 6-58.
I8212 = {
    1: ("~{DS1}", "in"), 2: ("MD", "in"), 3: ("DI1", "in"), 4: ("DO1", "tri"),
    5: ("DI2", "in"), 6: ("DO2", "tri"), 7: ("DI3", "in"), 8: ("DO3", "tri"),
    9: ("DI4", "in"), 10: ("DO4", "tri"), 11: ("STB", "in"), 12: ("GND", "pwr"),
    13: ("DS2", "in"), 14: ("~{CLR}", "in"), 15: ("DO5", "tri"), 16: ("DI5", "in"),
    17: ("DO6", "tri"), 18: ("DI6", "in"), 19: ("DO7", "tri"), 20: ("DI7", "in"),
    21: ("DO8", "tri"), 22: ("DI8", "in"), 23: ("~{INT}", "out"), 24: ("VCC", "pwr"),
}

# 8216/8226 4-bit bidirectional bus drivers, book 6-66 (identical pinouts).
I8216 = {
    1: ("~{CS}", "in"), 2: ("DO0", "tri"), 3: ("DB0", "bidi"), 4: ("DI0", "in"),
    5: ("DO1", "tri"), 6: ("DB1", "bidi"), 7: ("DI1", "in"), 8: ("GND", "pwr"),
    9: ("DI2", "in"), 10: ("DB2", "bidi"), 11: ("DO2", "tri"), 12: ("DI3", "in"),
    13: ("DB3", "bidi"), 14: ("DO3", "tri"), 15: ("~{DIEN}", "in"), 16: ("VCC", "pwr"),
}

# 8224 clock generator for the 8080A, book 6-82.
I8224 = {
    1: ("RESET", "out"), 2: ("~{RESIN}", "in"), 3: ("RDYIN", "in"), 4: ("READY", "out"),
    5: ("SYNC", "in"), 6: ("PHI2(TTL)", "out"), 7: ("~{STSTB}", "out"), 8: ("GND", "pwr"),
    9: ("VDD", "pwr"), 10: ("PHI2", "out"), 11: ("PHI1", "out"), 12: ("OSC", "out"),
    13: ("TANK", "in"), 14: ("XTAL2", "in"), 15: ("XTAL1", "in"), 16: ("VCC", "pwr"),
}

# 8228/8238 system controller and bus driver, book 6-87 (identical pinouts).
I8228 = {
    1: ("~{STSTB}", "in"), 2: ("HLDA", "in"), 3: ("~{WR}", "in"), 4: ("DBIN", "in"),
    5: ("DB4", "bidi"), 6: ("D4", "bidi"), 7: ("DB7", "bidi"), 8: ("D7", "bidi"),
    9: ("DB3", "bidi"), 10: ("D3", "bidi"), 11: ("DB2", "bidi"), 12: ("D2", "bidi"),
    13: ("DB0", "bidi"), 14: ("GND", "pwr"), 15: ("D0", "bidi"), 16: ("DB1", "bidi"),
    17: ("D1", "bidi"), 18: ("DB5", "bidi"), 19: ("D5", "bidi"), 20: ("DB6", "bidi"),
    21: ("D6", "bidi"), 22: ("~{BUSEN}", "in"), 23: ("~{INTA}", "tri"),
    24: ("~{MEMR}", "tri"), 25: ("~{I/OR}", "tri"), 26: ("~{MEMW}", "tri"),
    27: ("~{I/OW}", "tri"), 28: ("VCC", "pwr"),
}

# 8251A USART, book 8-43.
I8251A = {
    1: ("D2", "bidi"), 2: ("D3", "bidi"), 3: ("RxD", "in"), 4: ("GND", "pwr"),
    5: ("D4", "bidi"), 6: ("D5", "bidi"), 7: ("D6", "bidi"), 8: ("D7", "bidi"),
    9: ("~{TxC}", "in"), 10: ("~{WR}", "in"), 11: ("~{CS}", "in"), 12: ("C/~{D}", "in"),
    13: ("~{RD}", "in"), 14: ("RxRDY", "out"), 15: ("TxRDY", "out"),
    16: ("SYNDET/BD", "bidi"), 17: ("~{CTS}", "in"), 18: ("TxEMPTY", "out"),
    19: ("TxD", "out"), 20: ("CLK", "in"), 21: ("RESET", "in"), 22: ("~{DSR}", "in"),
    23: ("~{RTS}", "out"), 24: ("~{DTR}", "out"), 25: ("~{RxC}", "in"), 26: ("VCC", "pwr"),
    27: ("D0", "bidi"), 28: ("D1", "bidi"),
}

# 8257 DMA controller, book 6-106.
I8257 = {
    1: ("~{I/OR}", "bidi"), 2: ("~{I/OW}", "bidi"), 3: ("~{MEMR}", "tri"),
    4: ("~{MEMW}", "tri"), 5: ("MARK", "out"), 6: ("READY", "in"), 7: ("HLDA", "in"),
    8: ("ADSTB", "out"), 9: ("AEN", "out"), 10: ("HRQ", "out"), 11: ("~{CS}", "in"),
    12: ("CLK", "in"), 13: ("RESET", "in"), 14: ("~{DACK2}", "out"),
    15: ("~{DACK3}", "out"), 16: ("DRQ3", "in"), 17: ("DRQ2", "in"), 18: ("DRQ1", "in"),
    19: ("DRQ0", "in"), 20: ("GND", "pwr"), 21: ("D7", "bidi"), 22: ("D6", "bidi"),
    23: ("D5", "bidi"), 24: ("~{DACK1}", "out"), 25: ("~{DACK0}", "out"),
    26: ("D4", "bidi"), 27: ("D3", "bidi"), 28: ("D2", "bidi"), 29: ("D1", "bidi"),
    30: ("D0", "bidi"), 31: ("VCC", "pwr"), **_a(32, _bus("A", 0, 3)), 36: ("TC", "out"),
    **_a(37, _bus("A", 4, 7), "tri"),
}

# 8279 keyboard/display controller, book 8-264.
I8279 = {
    1: ("RL2", "in"), 2: ("RL3", "in"), 3: ("CLK", "in"), 4: ("IRQ", "out"),
    **_a(5, _bus("RL", 4, 7), "in"), 9: ("RESET", "in"), 10: ("~{RD}", "in"),
    11: ("~{WR}", "in"), **_a(12, _bus("DB", 0, 7)), 20: ("VSS", "pwr"), 21: ("A0", "in"),
    22: ("~{CS}", "in"), 23: ("~{BD}", "out"),
    **_a(24, ["OUT A3", "OUT A2", "OUT A1", "OUT A0", "OUT B3", "OUT B2", "OUT B1",
              "OUT B0"], "out"),
    **_a(32, _bus("SL", 0, 3), "out"), 36: ("SHIFT", "in"), 37: ("CNTL/STB", "in"),
    38: ("RL0", "in"), 39: ("RL1", "in"), 40: ("VCC", "pwr"),
}

_W51 = {**_WDC, "~{CS1}": "CS1B", "XTAL1": "XTLI", "XTAL2": "XTLO", "~{RTS}": "RTSB",
        "~{CTS}": "CTSB", "~{DTR}": "DTRB", "~{DCD}": "DCDB", "~{DSR}": "DSRB"}

PINOUTS = {
    "MPS6520": _per(M6520, _L6520, DIP40, "MOS 6520 peripheral interface adapter "
                    "(PIA), two 8-bit ports with handshake",
                    "6520 MPS6520 PIA MOS 6502 NMOS parallel", right=_R6520),
    "MPS6522": _per(M6522, _L6522, DIP40, "MOS 6522 versatile interface adapter (VIA): "
                    "two 8-bit ports, two 16-bit timers, shift register",
                    "6522 MPS6522 VIA MOS 6502 NMOS parallel timer", right=_R6520),
    "MPS6530": _per(M6530, [], DIP40, "MOS 6530 ROM-RAM-I/O-timer (RRIOT): 1Kx8 mask "
                    "ROM, 64x8 RAM, 16 I/O, timer", "6530 MPS6530 RRIOT MOS 6502 NMOS "
                    "ROM RAM timer", data="DB",
                    right=_bus("PA", 0, 7) + [None, "PB0", "PB1", "PB2", "PB3", "PB4",
                                              "CS2/PB5", "CS1/PB6", "~{IRQ}/PB7"]) | {
        "left": _bus("DB", 0, 7) + [None] + _bus("A", 0, 9)
        + [None, "RS0", "R/~{W}", "PHI2", "~{RES}"]},
    "MPS6532": _per(M6532, [], DIP40, "MOS 6532 RAM-I/O-timer (RIOT): 128x8 RAM, 16 "
                    "I/O, interval timer", "6532 MPS6532 RIOT MOS 6502 NMOS RAM timer",
                    data="DB", right=_bus("PA", 0, 7) + [None] + _bus("PB", 0, 7)) | {
        "left": _bus("DB", 0, 7) + [None] + _bus("A", 0, 6)
        + [None, "~{RS}", "CS1", "~{CS2}", "R/~{W}", "PHI2", "~{RES}", "~{IRQ}"]},
    "MPS6551": _per(M6551, _L6551, DIP28, "MOS 6551 asynchronous communications "
                    "interface adapter (ACIA), on-chip baud-rate generator",
                    "6551 MPS6551 ACIA UART serial MOS 6502 NMOS", data="DB",
                    right=_R6551),
    "W65C21": _per(W65C21, _ren(_L6520, _WDC), DIP40, "WDC W65C21 CMOS peripheral "
                   "interface adapter (PIA), 6520/6821 replacement, 14MHz",
                   "W65C21 65C21 6521 6520 PIA WDC CMOS parallel", right=_R6520),
    "W65C22N": _per(W65C22N, _ren(_L6522, _WDC), DIP40, "WDC W65C22N CMOS versatile "
                    "interface adapter (VIA), NMOS-compatible, open-drain IRQB, 14MHz",
                    "W65C22 W65C22N 65C22 6522 VIA WDC CMOS timer", right=_R6520),
    "W65C22S": _per(W65C22S, _ren(_L6522, _WDC), DIP40, "WDC W65C22S CMOS versatile "
                    "interface adapter (VIA), totem-pole IRQB, 1.8-5V, 14MHz",
                    "W65C22 W65C22S 65C22 6522 VIA WDC CMOS timer", right=_R6520),
    "W65C51N": _per(W65C51N, _ren(_L6551, _W51), DIP28, "WDC W65C51N CMOS "
                    "asynchronous communications interface adapter (ACIA), 14MHz",
                    "W65C51 W65C51N 65C51 6551 ACIA UART serial WDC CMOS",
                    right=_ren(_R6551, _W51)),
    "Z8430": _per(Z8430, [n for n in _LZ if n not in ("C/~{D}", "B/~{A}")]
                  + ["CS0", "CS1"], DIP28,
                  "Zilog Z80 CTC counter/timer circuit, four channels",
                  "Z8430 Z84C30 Z80 CTC counter timer Zilog",
                  right=["CLK/TRG0", "ZC/TO0", None, "CLK/TRG1", "ZC/TO1", None,
                         "CLK/TRG2", "ZC/TO2", None, "CLK/TRG3"]),
    "Z8440": _per(Z8440, _LZ, DIP40, "Zilog Z80 SIO/0 serial input/output controller "
                  "(TxCB and RxCB bonded together)", "Z8440 Z84C40 Z80 SIO SIO/0 USART "
                  "serial Zilog", right=_sio_right(Z8440), width=25.4),
    "Z8441": _per(Z8441, _LZ, DIP40, "Zilog Z80 SIO/1 serial input/output controller "
                  "(no DTRB)", "Z8441 Z84C41 Z80 SIO SIO/1 USART serial Zilog",
                  right=_sio_right(Z8441), width=25.4),
    "Z8442": _per(Z8442, _LZ, DIP40, "Zilog Z80 SIO/2 serial input/output controller "
                  "(no SYNCB)", "Z8442 Z84C42 Z80 SIO SIO/2 USART serial Zilog",
                  right=_sio_right(Z8442), width=25.4),
    "Z8470": _per(Z8470, _LZ, DIP40, "Zilog Z80 DART dual asynchronous "
                  "receiver/transmitter", "Z8470 Z80 DART UART serial Zilog",
                  right=_sio_right(Z8470), width=25.4),
    "Z8410": _per(Z8410, ["~{CE}/~{WAIT}", "~{RD}", "~{WR}", "~{IORQ}", "~{MREQ}",
                          "~{M1}", "CLK", "RDY", None, "~{INT}/~{PULSE}", "IEI", "IEO",
                          None, "~{BUSREQ}", "~{BAI}", "~{BAO}"], DIP40,
                  "Zilog Z80 DMA direct memory access controller",
                  "Z8410 Z84C10 Z80 DMA Zilog", right=_bus("A", 0, 15), width=25.4),
    "CDP1852": _per(CDP1852, [], DIP24, "RCA CDP1852 CMOS byte-wide input/output "
                    "port, latch with 3-state outputs and service request",
                    "1852 CDP1852 RCA COSMAC 1802 CMOS I/O port latch", data="DI",
                    right=_bus("DO", 0, 7)) | {
        "left": _bus("DI", 0, 7) + [None, "MODE", "CS1/~{CS1}", "CS2", "CLOCK",
                                    "~{CLEAR}", "~{SR}/SR"]},
    "CDP1853": _per(CDP1853, ["N0", "N1", "N2", None, "CE", "CLOCK A", "CLOCK B"],
                    DIP16N, "RCA CDP1853 CMOS N-bit 1-of-8 decoder for 1802 I/O "
                    "selection", "1853 CDP1853 RCA COSMAC 1802 CMOS decoder",
                    right=[f"OUT {i}" for i in range(8)], width=15.24),
    "CDP1854": _per(CDP1854, [], DIP40, "RCA CDP1854A CMOS UART, CDP1800 bus (mode 1) "
                    "or TR1602A compatible (mode 0)", "1854 CDP1854 CDP1854A RCA COSMAC "
                    "1802 CMOS UART serial",
                    right=["SDO", "SDI", "T CLOCK", "R CLOCK", None, "~{RTS}", "~{CTS}",
                           "~{PSI}", "~{ES}"], width=25.4) | {
        "left": [f"R BUS {i}" for i in range(8)] + [None]
        + [f"T BUS {i}" for i in range(8)]
        + [None, "MODE", "CS1", "~{CS2}", "CS3", "RSEL", "RD/~{WR}", "TPB", "~{CLEAR}",
           None, "~{INT}", "~{DA}", "~{THRE}", "FE", "PE/OE"]},
    "CDP1861": _per(CDP1861, [], DIP24, "RCA CDP1861C CMOS video display controller "
                    "(Pixie), 64x128 bit-mapped via 1802 DMA",
                    "1861 CDP1861 CDP1861C Pixie RCA COSMAC 1802 CMOS video", data="DI",
                    right=["VIDEO", "~{COMP SYNC}", None, "~{CLEAR}", "~{EFX}"]) | {
        "left": _bus("DI", 0, 7) + [None, "SC0", "SC1", "TPA", "TPB", "~{CLK}",
                                    "~{RESET}", "DISP ON", "DISP OFF", None, "~{DMAO}",
                                    "~{INT}"]},
    "TMS9901": _per(TMS9901, ["S0", "S1", "S2", "S3", "S4", "~{CE}", "CRUIN", "CRUOUT",
                              "CRUCLK", "~{φ}", "~{RST1}", None, "~{INTREQ}", "IC0",
                              "IC1", "IC2", "IC3"], DIP40,
                    "TI TMS9901 programmable systems interface: interrupt controller, "
                    "16 I/O, interval timer, CRU interface",
                    "9901 TMS9901 TI 9900 NMOS CRU interrupt timer",
                    right=[f"~{{INT{i}}}" for i in range(1, 7)] + [None]
                    + [f"P{i}" for i in range(7)] + [None]
                    + ["~{INT15}/P7"] + [f"~{{INT{14 - i}}}/P{8 + i}" for i in range(8)],
                    width=25.4),
    "TMS9902": _per(TMS9902, ["S0", "S1", "S2", "S3", "S4", "~{CE}", "CRUIN", "CRUOUT",
                              "CRUCLK", "~{φ}", "~{INT}"], DIP18N,
                    "TI TMS9902 asynchronous communications controller (UART), CRU "
                    "interface", "9902 TMS9902 TI 9900 NMOS CRU UART serial",
                    right=["XOUT", "RIN", None, "~{RTS}", "~{CTS}", "~{DSR}"]),
    "TIM9904": _per(TIM9904, ["XTAL 1", "XTAL 2", "TANK 1", "TANK 2", "OSCIN", None,
                              "FFD"], DIP20N,
                    "TI TIM9904 (SN74LS362) four-phase 12V clock generator/driver for "
                    "the TMS9900", "9904 TIM9904 SN74LS362 74LS362 TI 9900 clock "
                    "generator bipolar",
                    right=["φ1", "φ2", "φ3", "φ4", None, "~{φ1} TTL", "~{φ2} TTL",
                           "~{φ3} TTL", "~{φ4} TTL", None, "OSCOUT", "FFQ"]),
    "8212": _per(I8212, [], DIP24, "Intel 8212 8-bit input/output port, latch with "
                 "3-state outputs and service-request flip-flop",
                 "8212 Intel I/O port latch bipolar 8080", data="DI",
                 right=_bus("DO", 1, 8)) | {
        "left": _bus("DI", 1, 8) + [None, "~{DS1}", "DS2", "MD", "STB", "~{CLR}",
                                    "~{INT}"]},
    "8216": _per(I8216, [], DIP16N, "Intel 8216/8226 4-bit bidirectional bus driver, "
                 "3-state", "8216 8226 Intel bus driver transceiver bipolar 8080",
                 data="DI", width=15.24) | {
        "left": _bus("DI", 0, 3) + [None] + _bus("DO", 0, 3) + [None, "~{CS}",
                                                                 "~{DIEN}"],
        "right": _bus("DB", 0, 3)},
    "8224": _per(I8224, [], DIP16N, "Intel 8224 clock generator and driver for the "
                 "8080A, 12V phi1/phi2, reset and ready sync",
                 "8224 Intel clock generator 8080 bipolar",
                 right=["PHI1", "PHI2", "PHI2(TTL)", "OSC", None, "RESET", "READY",
                        "~{STSTB}"], width=15.24) | {
        "left": ["XTAL1", "XTAL2", "TANK", None, "~{RESIN}", "RDYIN", "SYNC"]},
    "8228": _per(I8228, ["~{STSTB}", "DBIN", "~{WR}", "HLDA", "~{BUSEN}"], DIP28,
                 "Intel 8228/8238 system controller and bus driver for the 8080A",
                 "8228 8238 Intel system controller bus driver 8080 bipolar",
                 right=_bus("DB", 0, 7) + [None, "~{MEMR}", "~{MEMW}", "~{I/OR}",
                                           "~{I/OW}", "~{INTA}"]),
    "8251A": _per(I8251A, ["C/~{D}", "~{CS}", "~{RD}", "~{WR}", "CLK", "RESET", None,
                           "TxRDY", "RxRDY", "TxEMPTY", "SYNDET/BD"], DIP28,
                  "Intel 8251A programmable communication interface (USART), sync "
                  "and async", "8251 8251A Intel USART UART serial NMOS",
                  right=["TxD", "RxD", "~{TxC}", "~{RxC}", None, "~{RTS}", "~{CTS}",
                         "~{DTR}", "~{DSR}"]),
    "8257": _per(I8257, ["~{CS}", "~{I/OR}", "~{I/OW}", "CLK", "RESET", "READY",
                         None, "HRQ", "HLDA", "AEN", "ADSTB", "~{MEMR}", "~{MEMW}",
                         "MARK", "TC"], DIP40,
                 "Intel 8257 programmable DMA controller, four channels",
                 "8257 Intel DMA controller NMOS 8080 8085",
                 right=_bus("A", 0, 7) + [None] + _bus("DRQ", 0, 3) + [None]
                 + [f"~{{DACK{i}}}" for i in range(4)], width=25.4),
    "8279": _per(I8279, ["A0", "~{CS}", "~{RD}", "~{WR}", "CLK", "RESET", "IRQ"],
                 DIP40, "Intel 8279 programmable keyboard/display interface",
                 "8279 Intel keyboard display controller NMOS 8085", data="DB",
                 right=_bus("RL", 0, 7) + ["SHIFT", "CNTL/STB", None]
                 + _bus("SL", 0, 3) + [None, "OUT A0", "OUT A1", "OUT A2", "OUT A3",
                                       "OUT B0", "OUT B1", "OUT B2", "OUT B3",
                                       "~{BD}"], width=25.4),

    "MC6840": _per(MC6840, ["RS0", "RS1", "RS2", "~{CS0}", "CS1", "R/~{W}", "E",
                            "~{RESET}", "~{IRQ}"], DIP28,
                   "Motorola MC6840 programmable timer module (PTM), three 16-bit timers",
                   "6840 MC6840 PTM timer Motorola 6800 NMOS",
                   right=["~{C1}", "~{G1}", "O1", None, "~{C2}", "~{G2}", "O2", None,
                          "~{C3}", "~{G3}", "O3"]),
    "MC6847": _per(MC6847, [], DIP40,
                   "Motorola MC6847 video display generator (VDG), 3.58MHz, NTSC "
                   "Y/phiA/phiB/CHB outputs", "6847 MC6847 MC6847Y VDG video Motorola NMOS",
                   data="DD",
                   right=["Y", "ϕA", "ϕB", "CHB", None, "~{HS}", "~{FS}", "~{RP}", None,
                          "CLK"],
                   width=25.4) | {"left": _bus("DD", 0, 7) + [None] + _bus("DA", 0, 12)
                                  + [None, "~{MS}", "~{A}/G", "~{A}/S", "~{INT}/EXT",
                                     "GM0", "GM1", "GM2", "CSS", "INV"]},
    "MC6850": _per(MC6850, ["RS", "CS0", "CS1", "~{CS2}", "R/~{W}", "E", "~{IRQ}"],
                   DIP24, "Motorola MC6850 asynchronous communications interface "
                   "adapter (ACIA)", "6850 MC6850 ACIA UART serial Motorola 6800 NMOS",
                   right=["Tx Data", "Rx Data", "Tx CLK", "Rx CLK", None, "~{RTS}",
                          "~{CTS}", "~{DCD}"]),
    "MC6852": _per(MC6852, ["RS", "~{CS}", "R/~{W}", "E", "~{RESET}", "~{IRQ}"],
                   DIP24, "Motorola MC6852 synchronous serial data adapter (SSDA)",
                   "6852 MC6852 SSDA synchronous serial Motorola 6800 NMOS",
                   right=["Tx Data", "Rx Data", "Tx CLK", "Rx CLK", None, "SM/~{DTR}",
                          "~{CTS}", "~{DCD}", "TUF"]),
    "MC6854": _per(MC6854, ["RS0", "RS1", "~{CS}", "R/~{W}", "E", "~{RESET}",
                            "~{IRQ}"], DIP28,
                   "Motorola MC6854 advanced data-link controller (ADLC), HDLC/SDLC",
                   "6854 MC6854 ADLC HDLC SDLC serial Motorola 6800 NMOS",
                   right=["TxD", "RxD", "TxC", "RxC", None, "~{RTS}", "~{CTS}", "~{DCD}",
                          "~{LOC/DTR}", "~{FLAG DET}", None, "RDSR", "TDSR"]),
    "MC68230": _per(MC68230, ["RS1", "RS2", "RS3", "RS4", "RS5", "~{CS}", "R/~{W}",
                              "~{DTACK}", "CLK", "~{RESET}"], DIP48,
                    "Motorola MC68230 parallel interface/timer (PI/T), ports A/B/C, "
                    "24-bit timer", "68230 MC68230 PIT PI/T parallel timer Motorola "
                    "68000 HMOS",
                    right=_bus("PA", 0, 7) + [None] + _bus("PB", 0, 7) + [None]
                    + ["H1", "H2", "H3", "H4", None, "PC0", "PC1", "PC2/TIN",
                       "PC3/TOUT", "PC4/~{DMAREQ}", "PC5/~{PIRQ}", "PC6/~{PIACK}",
                       "PC7/~{TIACK}"], width=25.4),
    "MC68901": _per(MC68901, ["RS1", "RS2", "RS3", "RS4", "RS5", "~{CS}", "~{DS}",
                              "R/~{W}", "~{DTACK}", "CLK", "~{RESET}", None, "~{IRQ}",
                              "~{IACK}", "~{IEI}", "~{IEO}"], DIP48,
                    "Motorola MC68901 multi-function peripheral (MFP): USART, four "
                    "timers, 8 I/O, 16-source interrupt controller",
                    "68901 MC68901 MFP USART timer Motorola 68000",
                    right=_bus("I", 0, 7) + [None, "TAI", "TBI", "TAO", "TBO", "TCO",
                                             "TDO", "XTAL1", "XTAL2", None, "SI",
                                             "SO", "RC", "TC", "~{RR}", "~{TR}"],
                    width=25.4),
    "MC68681": _per(MC68681, ["RS1", "RS2", "RS3", "RS4", "~{CS}", "R/~{W}",
                              "~{DTACK}", "~{RESET}", "~{IRQ}", "~{IACK}"], DIP40,
                    "Motorola MC68681 dual asynchronous receiver/transmitter (DUART), "
                    "counter/timer", "68681 MC68681 DUART UART serial Motorola 68000",
                    right=["RxDA", "TxDA", "RxDB", "TxDB", None, "X1/CLK", "X2", None]
                    + _bus("IP", 0, 5) + [None] + _bus("OP", 0, 7), width=25.4),
}
