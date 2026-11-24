"""Pin tables for the custom ic_microprocessors symbols.

One symbol per distinct pinout, named after the first chip that uses it. Chips whose
pinout matches a stock KiCad symbol pin for pin (MC6800/6802/6809/6809E, MC68000/
68008/68010, Z80, 8080A, 8086/8088, CDP1802) use the stock symbol instead; see the
generator. Pinouts are transcribed from each chip's data sheet (named in the
generator docstring). Write the symbols with

    python3 tools/make_dip_symbol.py db/tables/ic_microprocessors/_pinouts.py \\
        kicad_symbols/terra_symbols_ic_microprocessors.kicad_sym

Layout: address bus top-left (A0 first), then control inputs; data bus top-right
(D0 first), then control and clock outputs; supplies top and bottom.
Pin types: see tools/make_dip_symbol.py.
"""
import re


def _a(first, names, ptype="out"):
    """Consecutive pins first, first+1, ... named in order."""
    return {first + i: (n, ptype) for i, n in enumerate(names)}


def _bus(prefix, lo, hi):
    return [f"{prefix}{i}" for i in range(lo, hi + 1)]


def _cpu(pins, left_extra, right_extra, top, bottom, footprint, description, keywords,
         addr="A", data="D", width=20.32):
    """Build a pinout: address/data buses sorted by bit number, extras below a gap."""
    names = {n for n, _ in pins.values()}

    def bus(prefix):
        """Names like A3 or D3/BA3 for this prefix, in bit order."""
        hits = [(int(m.group(1)), n) for n in names
                if (m := re.match(rf"{prefix}(\d+)(/|$)", n))]
        return [n for _, n in sorted(hits)]

    return dict(pins=pins, left=bus(addr) + [None] + left_extra,
                right=bus(data) + [None] + right_extra, top=top, bottom=bottom,
                width=width, footprint=footprint, description=description,
                keywords=keywords)


DIP28 = "Package_DIP:DIP-28_W15.24mm"
DIP40 = "Package_DIP:DIP-40_W15.24mm"
DIP64W = "Package_DIP:DIP-64_W22.86mm"

# --- MOS Technology 6500 family (1982 MOS Technology Data Catalog, book 2-22/2-23) --

_DATA_6502 = _a(26, [f"D{i}" for i in range(7, -1, -1)], "bidi")  # pins 26-33 = D7..D0

M6502 = {
    1: ("VSS", "pwr"), 2: ("RDY", "in"), 3: ("PHI1(OUT)", "out"), 4: ("~{IRQ}", "in"),
    5: ("NC", "nc"), 6: ("~{NMI}", "in"), 7: ("SYNC", "out"), 8: ("VCC", "pwr"),
    **_a(9, _bus("A", 0, 11)), 21: ("VSS", "pwr"), **_a(22, _bus("A", 12, 15)),
    **_DATA_6502, 34: ("R/~{W}", "out"), 35: ("NC", "nc"), 36: ("NC", "nc"),
    37: ("PHI0(IN)", "in"), 38: ("S.O.", "in"), 39: ("PHI2(OUT)", "out"),
    40: ("~{RES}", "in"),
}


def _m28(head, addr_hi):
    """28-pin 6503-6507: pins 1..k are `head`, then A0..A<addr_hi>, D7..D0, R/W, clocks."""
    pins = {i + 1: p for i, p in enumerate(head)}
    first = len(head) + 1
    pins.update(_a(first, _bus("A", 0, addr_hi)))
    pins.update(_a(18, [f"D{i}" for i in range(7, -1, -1)], "bidi"))
    pins.update({26: ("R/~{W}", "out"), 27: ("PHI0(IN)", "in"), 28: ("PHI2(OUT)", "out")})
    assert sorted(pins) == list(range(1, 29)), head
    return pins


RES, VSS, VCC = ("~{RES}", "in"), ("VSS", "pwr"), ("VCC", "pwr")
IRQ, NMI, RDY = ("~{IRQ}", "in"), ("~{NMI}", "in"), ("RDY", "in")
M6503 = _m28([RES, VSS, IRQ, NMI, VCC], 11)
M6504 = _m28([RES, VSS, IRQ, VCC], 12)
M6505 = _m28([RES, VSS, RDY, IRQ, VCC], 11)
M6506 = _m28([RES, VSS, ("PHI1(OUT)", "out"), IRQ, VCC], 11)
M6507 = _m28([RES, VSS, RDY, VCC], 12)


# 6512-6515 (book 2-23/2-24): the external two-phase-clock versions. No clock
# generator: PHI1(IN) and PHI2(IN) replace PHI0(IN) and the clock outputs (the 40-pin
# 6512 still buffers PHI2(OUT)). The 6512 adds DBE (data bus enable) on pin 36 and a
# third VSS on pin 5.
M6512 = {
    1: ("VSS", "pwr"), 2: ("RDY", "in"), 3: ("PHI1(IN)", "in"), 4: ("~{IRQ}", "in"),
    5: ("VSS", "pwr"), 6: ("~{NMI}", "in"), 7: ("SYNC", "out"), 8: ("VCC", "pwr"),
    **_a(9, _bus("A", 0, 11)), 21: ("VSS", "pwr"), **_a(22, _bus("A", 12, 15)),
    **_DATA_6502, 34: ("R/~{W}", "out"), 35: ("NC", "nc"), 36: ("DBE", "in"),
    37: ("PHI2(IN)", "in"), 38: ("S.O.", "in"), 39: ("PHI2(OUT)", "out"),
    40: ("~{RES}", "in"),
}


def _m28x(head, addr_hi):
    """28-pin 6513-6515: `head` from pin 1, then A0..A<addr_hi>, D7..D0 on 18-25,
    R/W on 26, PHI2(IN) on 27 and RES on 28."""
    pins = {i + 1: p for i, p in enumerate(head)}
    pins.update(_a(len(head) + 1, _bus("A", 0, addr_hi)))
    pins.update(_a(18, [f"D{i}" for i in range(7, -1, -1)], "bidi"))
    pins.update({26: ("R/~{W}", "out"), 27: ("PHI2(IN)", "in"), 28: RES})
    assert sorted(pins) == list(range(1, 29)), head
    return pins


PHI1_IN = ("PHI1(IN)", "in")
M6513 = _m28x([VSS, PHI1_IN, IRQ, NMI, VCC], 11)
M6514 = _m28x([VSS, PHI1_IN, IRQ, VCC], 12)
M6515 = _m28x([VSS, RDY, PHI1_IN, IRQ, VCC], 11)

# Commodore Semiconductor Group "6510 Microprocessor with I/O" (HMOS), p. 1, the base
# 6510 column (the C64 CPU; the 6510-1 and 6510-2 pinouts differ and are not drawn).
# AEC (address enable control) floats the address bus and R/W for DMA, so those pins
# are tri-state. P0-P5 are the on-chip I/O port (DDR at 0000, data at 0001).
M6510 = {
    1: ("PHI1(IN)", "in"), 2: ("RDY", "in"), 3: ("~{IRQ}", "in"), 4: ("~{NMI}", "in"),
    5: ("AEC", "in"), 6: ("VCC", "pwr"), **_a(7, _bus("A", 0, 13), "tri"),
    21: ("VSS", "pwr"), 22: ("A14", "tri"), 23: ("A15", "tri"),
    **_a(24, [f"P{i}" for i in range(5, -1, -1)], "bidi"),
    **_a(30, [f"DB{i}" for i in range(7, -1, -1)], "bidi"),
    38: ("R/~{W}", "tri"), 39: ("PHI2(OUT)", "out"), 40: ("~{RES}", "in"),
}


def _mos(pins, pkg_pins, desc, extra_in, extra_out):
    return _cpu(pins, ["PHI0(IN)", "~{RES}"] + extra_in, ["R/~{W}"] + extra_out,
                ["VCC"], ["VSS"], DIP40 if pkg_pins == 40 else DIP28, desc,
                "6502 65xx MOS NMOS CPU microprocessor 8-bit")


# --- WDC W65C02S / W65C816S (current WDC data sheets, figure 3-1 / 2-2) ---------------
# WDC marks active-low signals with a trailing B (RESB, IRQB) instead of an overbar.

W65C02S = {
    1: ("VPB", "out"), 2: ("RDY", "bidi"), 3: ("PHI1O", "out"), 4: ("IRQB", "in"),
    5: ("MLB", "out"), 6: ("NMIB", "in"), 7: ("SYNC", "out"), 8: ("VDD", "pwr"),
    **_a(9, _bus("A", 0, 11), "tri"), 21: ("VSS", "pwr"), **_a(22, _bus("A", 12, 15), "tri"),
    **_DATA_6502, 34: ("RWB", "tri"), 35: ("NC", "nc"), 36: ("BE", "in"),
    37: ("PHI2", "in"), 38: ("SOB", "in"), 39: ("PHI2O", "out"), 40: ("RESB", "in"),
}

W65C816S = {
    1: ("VPB", "out"), 2: ("RDY", "bidi"), 3: ("ABORTB", "in"), 4: ("IRQB", "in"),
    5: ("MLB", "out"), 6: ("NMIB", "in"), 7: ("VPA", "out"), 8: ("VDD", "pwr"),
    **_a(9, _bus("A", 0, 11), "tri"), 21: ("VSS", "pwr"), **_a(22, _bus("A", 12, 15), "tri"),
    **_a(26, [f"D{i}/BA{i}" for i in range(7, -1, -1)], "bidi"),
    34: ("RWB", "tri"), 35: ("E", "out"), 36: ("BE", "in"), 37: ("PHI2", "in"),
    38: ("MX", "out"), 39: ("VDA", "out"), 40: ("RESB", "in"),
}

# --- Intel 8085A (1981 Intel Component Data Catalog, book 6-10) -----------------------

I8085A = {
    1: ("X1", "in"), 2: ("X2", "in"), 3: ("RESET OUT", "out"), 4: ("SOD", "out"),
    5: ("SID", "in"), 6: ("TRAP", "in"), 7: ("RST 7.5", "in"), 8: ("RST 6.5", "in"),
    9: ("RST 5.5", "in"), 10: ("INTR", "in"), 11: ("~{INTA}", "out"),
    **_a(12, _bus("AD", 0, 7), "bidi"), 20: ("VSS", "pwr"), **_a(21, _bus("A", 8, 15), "tri"),
    29: ("S0", "out"), 30: ("ALE", "out"), 31: ("~{WR}", "tri"), 32: ("~{RD}", "tri"),
    33: ("S1", "out"), 34: ("IO/~{M}", "tri"), 35: ("READY", "in"),
    36: ("~{RESET IN}", "in"), 37: ("CLK (OUT)", "out"), 38: ("HLDA", "out"),
    39: ("HOLD", "in"), 40: ("VCC", "pwr"),
}

# --- Intel 8086 / 8088 (1981 Intel Component Data Catalog, book 7-1 / 7-25) ----------
# Pins 24-31 (and 34 on the 8088) change function with MN/~{MX}. Names give the
# minimum-mode signal first and the maximum-mode signal in parentheses, so one
# symbol serves both modes. (KiCad's stock 8088 symbols drop the bar on ~{DEN}.)

_MODE_8086 = {
    24: ("~{INTA} (QS1)", "out"), 25: ("ALE (QS0)", "out"), 26: ("~{DEN} (~{S0})", "tri"),
    27: ("DT/~{R} (~{S1})", "tri"), 28: ("M/~{IO} (~{S2})", "tri"),
    29: ("~{WR} (~{LOCK})", "tri"), 30: ("HLDA (~{RQ}/~{GT1})", "bidi"),
    31: ("HOLD (~{RQ}/~{GT0})", "bidi"),
}
_COMMON_8086 = {
    1: ("GND", "pwr"), 17: ("NMI", "in"), 18: ("INTR", "in"), 19: ("CLK", "in"),
    20: ("GND", "pwr"), 21: ("RESET", "in"), 22: ("READY", "in"), 23: ("~{TEST}", "in"),
    32: ("~{RD}", "tri"), 33: ("MN/~{MX}", "in"), 35: ("A19/S6", "tri"),
    36: ("A18/S5", "tri"), 37: ("A17/S4", "tri"), 38: ("A16/S3", "tri"), 40: ("VCC", "pwr"),
}
I8086 = {
    **_COMMON_8086, **_MODE_8086,
    **_a(2, [f"AD{i}" for i in range(14, -1, -1)], "bidi"), 34: ("~{BHE}/S7", "tri"),
    39: ("AD15", "bidi"),
}
I8088 = {
    **_COMMON_8086, **_MODE_8086, 28: ("IO/~{M} (~{S2})", "tri"),
    **_a(2, [f"A{i}" for i in range(14, 7, -1)], "tri"),
    **_a(9, [f"AD{i}" for i in range(7, -1, -1)], "bidi"),
    34: ("~{SS0} (HIGH)", "out"), 39: ("A15", "tri"),
}
_IN_8086 = ["CLK", "RESET", "READY", "~{TEST}", "NMI", "INTR", "MN/~{MX}",
            "HOLD (~{RQ}/~{GT0})"]
_OUT_8086 = ["ALE (QS0)", "~{RD}", "~{WR} (~{LOCK})", "DT/~{R} (~{S1})",
             "~{DEN} (~{S0})", "~{INTA} (QS1)", "HLDA (~{RQ}/~{GT1})"]

# --- TI TMS9900 (TMS 9900 Microprocessor Data Manual, May 1976, table 2) ------------
# TI numbers bits MSB first: A0 and D0 are the most significant bits. The 64-pin DIP
# is 0.9" wide.

TMS9900 = {
    1: ("VBB", "pwr"), 2: ("VCC", "pwr"), 3: ("WAIT", "out"), 4: ("~{LOAD}", "in"),
    5: ("HOLDA", "out"), 6: ("~{RESET}", "in"), 7: ("IAQ", "out"), 8: ("PHI1", "in"),
    9: ("PHI2", "in"), **_a(10, [f"A{i}" for i in range(14, -1, -1)], "tri"),
    25: ("PHI4", "in"), 26: ("VSS", "pwr"), 27: ("VDD", "pwr"), 28: ("PHI3", "in"),
    29: ("DBIN", "tri"), 30: ("CRUOUT", "out"), 31: ("CRUIN", "in"),
    32: ("~{INTREQ}", "in"), 33: ("IC3", "in"), 34: ("IC2", "in"), 35: ("IC1", "in"),
    36: ("IC0", "in"), 37: ("NC", "nc"), 38: ("NC", "nc"), 39: ("NC", "nc"),
    40: ("VSS", "pwr"), **_a(41, _bus("D", 0, 15), "bidi"), 57: ("NC", "nc"),
    58: ("NC", "nc"), 59: ("VCC", "pwr"), 60: ("CRUCLK", "out"), 61: ("~{WE}", "tri"),
    62: ("READY", "in"), 63: ("~{MEMEN}", "tri"), 64: ("~{HOLD}", "in"),
}

PINOUTS = {
    "MPS6502": _mos(M6502, 40, "MOS 6502 NMOS 8-bit CPU, 64K address, on-chip clock",
                    ["~{IRQ}", "~{NMI}", "RDY", "S.O."], ["SYNC", "PHI1(OUT)", "PHI2(OUT)"]),
    "MPS6503": _mos(M6503, 28, "MOS 6503 NMOS 8-bit CPU, 4K address, IRQ and NMI",
                    ["~{IRQ}", "~{NMI}"], ["PHI2(OUT)"]),
    "MPS6504": _mos(M6504, 28, "MOS 6504 NMOS 8-bit CPU, 8K address, IRQ",
                    ["~{IRQ}"], ["PHI2(OUT)"]),
    "MPS6505": _mos(M6505, 28, "MOS 6505 NMOS 8-bit CPU, 4K address, IRQ and RDY",
                    ["~{IRQ}", "RDY"], ["PHI2(OUT)"]),
    "MPS6506": _mos(M6506, 28, "MOS 6506 NMOS 8-bit CPU, 4K address, IRQ, two-phase "
                    "clock out", ["~{IRQ}"], ["PHI1(OUT)", "PHI2(OUT)"]),
    "MPS6507": _mos(M6507, 28, "MOS 6507 NMOS 8-bit CPU, 8K address, RDY, no interrupts",
                    ["RDY"], ["PHI2(OUT)"]),
    "MPS6512": _cpu(M6512, ["PHI1(IN)", "PHI2(IN)", "~{RES}", "~{IRQ}", "~{NMI}", "RDY",
                            "S.O.", "DBE"], ["R/~{W}", "SYNC", "PHI2(OUT)"], ["VCC"],
                    ["VSS"], DIP40, "MOS 6512 NMOS 8-bit CPU, 64K address, external "
                    "two-phase clock, data bus enable",
                    "6512 6502 65xx MOS NMOS CPU microprocessor 8-bit"),
    "MPS6513": _cpu(M6513, ["PHI1(IN)", "PHI2(IN)", "~{RES}", "~{IRQ}", "~{NMI}"],
                    ["R/~{W}"], ["VCC"], ["VSS"], DIP28, "MOS 6513 NMOS 8-bit CPU, 4K "
                    "address, IRQ and NMI, external two-phase clock",
                    "6513 6502 65xx MOS NMOS CPU microprocessor 8-bit"),
    "MPS6514": _cpu(M6514, ["PHI1(IN)", "PHI2(IN)", "~{RES}", "~{IRQ}"],
                    ["R/~{W}"], ["VCC"], ["VSS"], DIP28, "MOS 6514 NMOS 8-bit CPU, 8K "
                    "address, IRQ, external two-phase clock",
                    "6514 6502 65xx MOS NMOS CPU microprocessor 8-bit"),
    "MPS6515": _cpu(M6515, ["PHI1(IN)", "PHI2(IN)", "~{RES}", "~{IRQ}", "RDY"],
                    ["R/~{W}"], ["VCC"], ["VSS"], DIP28, "MOS 6515 NMOS 8-bit CPU, 4K "
                    "address, IRQ and RDY, external two-phase clock",
                    "6515 6502 65xx MOS NMOS CPU microprocessor 8-bit"),
    "6510": _cpu(M6510, ["PHI1(IN)", "~{RES}", "~{IRQ}", "~{NMI}", "RDY", "AEC"],
                 ["R/~{W}", "PHI2(OUT)", None] + [f"P{i}" for i in range(6)],
                 ["VCC"], ["VSS"], DIP40, "MOS/Commodore 6510 HMOS 8-bit CPU with "
                 "6-bit I/O port (P0-P5), 64K address, AEC bus float",
                 "6510 6502 65xx MOS Commodore C64 HMOS CPU microprocessor 8-bit",
                 data="DB"),
    "W65C02S": _cpu(W65C02S, ["PHI2", "RESB", "IRQB", "NMIB", "SOB", "BE", "RDY"],
                    ["RWB", "SYNC", "VPB", "MLB", "PHI1O", "PHI2O"], ["VDD"], ["VSS"],
                    DIP40, "WDC W65C02S static CMOS 8-bit CPU, 64K address, 1.8-5V",
                    "65C02 W65C02S 6502 WDC CMOS CPU microprocessor 8-bit"),
    "W65C816S": _cpu(W65C816S, ["PHI2", "RESB", "IRQB", "NMIB", "ABORTB", "BE", "RDY"],
                     ["RWB", "VDA", "VPA", "VPB", "MLB", "E", "MX"], ["VDD"], ["VSS"],
                     DIP40, "WDC W65C816S static CMOS 8/16-bit CPU, 16M address "
                     "(bank on D0-D7), 1.8-5V",
                     "65816 W65C816S 65C816 WDC CMOS CPU microprocessor 16-bit",
                     data="D"),
    "8085A": _cpu(I8085A, ["X1", "X2", None, "~{RESET IN}", "READY", "HOLD", "TRAP",
                           "RST 7.5", "RST 6.5", "RST 5.5", "INTR", "SID"],
                  ["ALE", "~{RD}", "~{WR}", "IO/~{M}", "S0", "S1", "~{INTA}", "HLDA",
                   None, "CLK (OUT)", "RESET OUT", "SOD"], ["VCC"], ["VSS"], DIP40,
                  "Intel 8085A NMOS 8-bit CPU, multiplexed AD0-AD7, on-chip clock, "
                  "5 interrupts, serial SID/SOD", "8085 8085A Intel NMOS CPU "
                  "microprocessor 8-bit", data="AD"),
    "8086": _cpu(I8086, _IN_8086, _OUT_8086 + ["M/~{IO} (~{S2})", "~{BHE}/S7"],
                 ["VCC"], ["GND"], DIP40,
                 "Intel 8086 HMOS 16-bit CPU, multiplexed AD0-AD15, 1M address, "
                 "min/max mode", "8086 iAPX86 Intel HMOS CPU microprocessor 16-bit x86",
                 data="AD", width=30.48),
    "8088": _cpu(I8088, _IN_8086, _OUT_8086 + ["IO/~{M} (~{S2})", "~{SS0} (HIGH)"],
                 ["VCC"], ["GND"], DIP40,
                 "Intel 8088 HMOS 16-bit CPU with 8-bit bus, multiplexed AD0-AD7, "
                 "1M address, min/max mode",
                 "8088 iAPX88 Intel HMOS CPU microprocessor 16-bit x86", data="AD",
                 width=30.48),
    "TMS9900": _cpu(TMS9900, ["PHI1", "PHI2", "PHI3", "PHI4", None, "~{RESET}",
                              "~{LOAD}", "~{INTREQ}", "IC0", "IC1", "IC2", "IC3",
                              "~{HOLD}", "READY", "CRUIN"],
                    ["~{MEMEN}", "DBIN", "~{WE}", "WAIT", "IAQ", "HOLDA", None,
                     "CRUOUT", "CRUCLK"], ["VCC", "VDD"], ["VSS", "VBB"], DIP64W,
                    "TI TMS9900 NMOS 16-bit CPU, 32K-word address (A0 = MSB), "
                    "four-phase clock, +12V/+5V/-5V",
                    "TMS9900 9900 TI NMOS CPU microprocessor 16-bit CRU"),
}
