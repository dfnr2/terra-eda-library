"""Pin tables for the custom ic_memory DIP symbols.

One entry per distinct pinout, named after the first chip that uses it; chips with
identical pins share the symbol. Each table was read from the data book's
pin-configuration drawing named in its comment. Write the symbols with

    python3 tools/make_dip_symbol.py db/tables/ic_memory/_pinouts.py \\
        kicad_symbols/terra_symbols_ic_memory.kicad_sym

Pin types: in, out, tri, bidi, oc, oe, pwr, nc (see tools/make_dip_symbol.py).
"""


def _pins(**groups):
    """Build {number: (name, type)} from type=[(number, name), ...] groups."""
    out = {}
    for ptype, pins in groups.items():
        for num, name in pins:
            if num in out:
                raise ValueError(f"pin {num} given twice")
            out[num] = (name, ptype)
    return out


# SST39SF0x0 address pins A0-A16 and data pins, shared by the three flash symbols.
_SST_ADDR = [(12, "A0"), (11, "A1"), (10, "A2"), (9, "A3"), (8, "A4"), (7, "A5"),
             (6, "A6"), (5, "A7"), (27, "A8"), (26, "A9"), (23, "A10"), (25, "A11"),
             (4, "A12"), (28, "A13"), (29, "A14"), (3, "A15"), (2, "A16")]
_SST_DQ = [(13, "DQ0"), (14, "DQ1"), (15, "DQ2"), (17, "DQ3"), (18, "DQ4"),
           (19, "DQ5"), (20, "DQ6"), (21, "DQ7")]

# Parallel EEPROM data pins, written in-system, so bidirectional.
_IO24 = [(9, "I/O0"), (10, "I/O1"), (11, "I/O2"), (13, "I/O3"), (14, "I/O4"),
         (15, "I/O5"), (16, "I/O6"), (17, "I/O7")]
_IO28 = [(n + 2, name) for n, name in _IO24]
_IO32 = [(n + 4, name) for n, name in _IO24]
# 2Kx8 address pins on the 24-pin JEDEC site, and the same pins moved up two on 28.
_A24 = [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"), (3, "A5"), (2, "A6"),
        (1, "A7"), (23, "A8"), (22, "A9"), (19, "A10")]
_A28 = [(n + 2, name) for n, name in _A24]


def _prom(addr, outs, enables, vcc, gnd, ptype, pins, desc, kw, extra_nc=()):
    """A bipolar PROM pinout: addr/outs/enables are [(number, name), ...]."""
    width = "7.62" if pins < 24 else "15.24"
    left = [name for _, name in sorted(addr, key=lambda p: int(p[1][1:]))]
    return dict(
        pins=_pins(**{"in": addr + enables, ptype: outs,
                      "nc": [(n, "NC") for n in extra_nc],
                      "pwr": [(vcc, "VCC"), (gnd, "GND")]}),
        left=left + [None] + [name for _, name in enables],
        right=[name for _, name in outs],
        top=["VCC"], bottom=["GND"],
        footprint=f"Package_DIP:DIP-{pins}_W{width}mm",
        description=desc, keywords=kw)


# Bipolar PROM pin groups, shared by every maker's equivalent part (Signetics 1977,
# AMD 1984, MMI 1981, TI 1981, National 1983 books agree pin for pin). Outputs are
# named O0..On (Signetics prints O1../B0.., National Q1..).
_P16_ADDR4 = [(5, "A0"), (6, "A1"), (7, "A2"), (4, "A3"), (3, "A4"), (2, "A5"),
              (1, "A6"), (15, "A7")]
_P16_OUT4 = [(12, "O0"), (11, "O1"), (10, "O2"), (9, "O3")]
_P18_ADDR4 = _P16_ADDR4[:7] + [(17, "A7"), (16, "A8"), (15, "A9")]
_P18_OUT4 = [(14, "O0"), (13, "O1"), (12, "O2"), (11, "O3")]
_P24_ADDR8 = [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"), (3, "A5"),
              (2, "A6"), (1, "A7"), (23, "A8")]
_P24_OUT8 = [(9, "O0"), (10, "O1"), (11, "O2"), (13, "O3"), (14, "O4"), (15, "O5"),
             (16, "O6"), (17, "O7")]
_PROMS = {
    # name OC, name TS: (addr, outs, enables, vcc, gnd, pins, org, extra NC, keywords)
    ("82S23", "82S123"): (
        [(10, "A0"), (11, "A1"), (12, "A2"), (13, "A3"), (14, "A4")],
        [(1, "O0"), (2, "O1"), (3, "O2"), (4, "O3"), (5, "O4"), (6, "O5"), (7, "O6"),
         (9, "O7")],
        [(15, "~{CE}")], 16, 8, 16, "32x8", (),
        "82S23 82S123 74S188 74S288 27S18 27S19 6330 6331 TBP18S030"),
    ("82S126", "82S129"): (
        _P16_ADDR4, _P16_OUT4, [(13, "~{CE1}"), (14, "~{CE2}")], 16, 8, 16, "256x4", (),
        "82S126 82S129 74S387 74S287 27S20 27S21 6300 6301 TBP24S10"),
    ("82S130", "82S131"): (
        _P16_ADDR4 + [(14, "A8")], _P16_OUT4, [(13, "~{CE}")], 16, 8, 16, "512x4", (),
        "82S130 82S131 74S570 74S571 27S12 27S13 6305 6306"),
    ("82S136", "82S137"): (
        _P18_ADDR4, _P18_OUT4, [(8, "~{CE1}"), (10, "~{CE2}")], 18, 9, 18, "1Kx4", (),
        "82S136 82S137 74S572 74S573 27S32 27S33 6352 6353 TBP24S41"),
    ("82S184", "82S185"): (
        _P18_ADDR4 + [(8, "A10")], _P18_OUT4, [(10, "~{CE}")], 18, 9, 18, "2Kx4", (),
        "82S184 82S185 87S184 87S185 27S184 27S185 6388 6389 TBP24S81"),
    ("27S28", "27S29"): (
        [(1, "A0"), (2, "A1"), (3, "A2"), (4, "A3"), (5, "A4"), (16, "A5"), (17, "A6"),
         (18, "A7"), (19, "A8")],
        [(6, "O0"), (7, "O1"), (8, "O2"), (9, "O3"), (11, "O4"), (12, "O5"), (13, "O6"),
         (14, "O7")],
        [(15, "~{CE}")], 20, 10, 20, "512x8", (),
        "27S28 27S29 74S473 74S472 6348 6349 82S146 82S147 TBP18S42"),
    ("6340", "6341"): (
        _P24_ADDR8, _P24_OUT8,
        [(21, "~{CE1}"), (20, "~{CE2}"), (19, "CE3"), (18, "CE4")], 24, 12, 24, "512x8",
        (22,), "6340 6341 74S475 74S474 27S30 27S31 82S141 TBP18S46"),
    ("82S180", "82S181"): (
        _P24_ADDR8 + [(22, "A9")], _P24_OUT8,
        [(21, "~{CE1}"), (20, "~{CE2}"), (19, "CE3"), (18, "CE4")], 24, 12, 24, "1Kx8",
        (), "82S180 82S181 87S180 87S181 27S180 27S181 6380 6381 TBP28S86"),
    ("82S190", "82S191"): (
        _P24_ADDR8 + [(22, "A9"), (21, "A10")], _P24_OUT8,
        [(20, "~{CE1}"), (19, "CE2"), (18, "CE3")], 24, 12, 24, "2Kx8", (),
        "82S190 82S191 87S190 87S191 27S190 27S191 TBP28S166"),
}

PINOUTS = {
    # Intel 2101A 256x4, separate I/O (1979 Component Data Catalog, p. 3-4). Shared,
    # pin for pin, by the Intel 5101 (p. 3-111, pin 20 printed R/W, low = write) and
    # the RCA CDP1822 (1982 CMOS book, p. 134, VDD/VSS, ~CS1/CS2, R/~W). OD high turns
    # the outputs off so DI and DO can be tied for common I/O.
    "2101A": dict(
        pins=_pins(
            **{"in": [(4, "A0"), (3, "A1"), (2, "A2"), (1, "A3"), (21, "A4"),
                      (5, "A5"), (6, "A6"), (7, "A7"),
                      (9, "DI1"), (11, "DI2"), (13, "DI3"), (15, "DI4"),
                      (19, "~{CE1}"), (17, "CE2"), (18, "OD"), (20, "~{WE}")],
               "tri": [(10, "DO1"), (12, "DO2"), (14, "DO3"), (16, "DO4")],
               "pwr": [(22, "VCC"), (8, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", None,
              "~{CE1}", "CE2", "OD", "~{WE}"],
        right=["DI1", "DI2", "DI3", "DI4", None, "DO1", "DO2", "DO3", "DO4"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-22_W10.16mm",
        description="256x4 static RAM, separate I/O, output disable (2101A/5101/CDP1822 pinout)",
        keywords="RAM SRAM 256x4 2101A 5101 CDP1822"),
    # Intel 2102A 1Kx1 (1979 catalog, p. 3-8). GND/VCC on pins 9/10, not the corners.
    # R/W is printed without an overbar; the truth table has low = write.
    "2102A": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (4, "A1"), (5, "A2"), (6, "A3"), (7, "A4"),
                      (2, "A5"), (1, "A6"), (16, "A7"), (15, "A8"), (14, "A9"),
                      (11, "DIN"), (13, "~{CE}"), (3, "R/~{W}")],
               "tri": [(12, "DOUT")],
               "pwr": [(10, "VCC"), (9, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", None,
              "~{CE}", "R/~{W}"],
        right=["DIN", None, "DOUT"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-16_W7.62mm",
        description="1Kx1 static RAM, separate data in/out",
        keywords="RAM SRAM 1Kx1 2102"),
    # Intel 2111A 256x4, common I/O (1979 catalog, p. 3-45). Both chip enables are
    # active low (unlike the 2101A's CE2); OD high turns the outputs off.
    "2111A": dict(
        pins=_pins(
            **{"in": [(4, "A0"), (3, "A1"), (2, "A2"), (1, "A3"), (17, "A4"),
                      (5, "A5"), (6, "A6"), (7, "A7"),
                      (15, "~{CE1}"), (10, "~{CE2}"), (9, "OD"), (16, "R/~{W}")],
               "bidi": [(11, "I/O1"), (12, "I/O2"), (13, "I/O3"), (14, "I/O4")],
               "pwr": [(18, "VCC"), (8, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", None,
              "~{CE1}", "~{CE2}", "OD", "R/~{W}"],
        right=["I/O1", "I/O2", "I/O3", "I/O4"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-18_W7.62mm",
        description="256x4 static RAM, common I/O, output disable",
        keywords="RAM SRAM 256x4 2111"),
    # Intel 2112A 256x4, common I/O, no OD (1979 catalog, p. 3-49).
    "2112A": dict(
        pins=_pins(
            **{"in": [(4, "A0"), (3, "A1"), (2, "A2"), (1, "A3"), (15, "A4"),
                      (5, "A5"), (6, "A6"), (7, "A7"), (13, "~{CE}"), (14, "~{WE}")],
               "bidi": [(9, "I/O1"), (10, "I/O2"), (11, "I/O3"), (12, "I/O4")],
               "pwr": [(16, "VCC"), (8, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", None, "~{CE}", "~{WE}"],
        right=["I/O1", "I/O2", "I/O3", "I/O4"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-16_W7.62mm",
        description="256x4 static RAM, common I/O",
        keywords="RAM SRAM 256x4 2112"),
    # Intel 2114 1Kx4 (1979 catalog, p. 3-54); the 2114A (1981 catalog, p. 1-2) has
    # the same pins.
    "2114": dict(
        pins=_pins(
            **{"in": [(5, "A0"), (6, "A1"), (7, "A2"), (4, "A3"), (3, "A4"),
                      (2, "A5"), (1, "A6"), (17, "A7"), (16, "A8"), (15, "A9"),
                      (8, "~{CS}"), (10, "~{WE}")],
               "bidi": [(14, "I/O1"), (13, "I/O2"), (12, "I/O3"), (11, "I/O4")],
               "pwr": [(18, "VCC"), (9, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", None,
              "~{CS}", "~{WE}"],
        right=["I/O1", "I/O2", "I/O3", "I/O4"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-18_W7.62mm",
        description="1Kx4 static RAM, common I/O",
        keywords="RAM SRAM 1Kx4 2114"),
    # Intel 2147 4Kx1 HMOS (1979 catalog, p. 3-99). Powers down when ~CS is high.
    "2147": dict(
        pins=_pins(
            **{"in": [(1, "A0"), (2, "A1"), (3, "A2"), (4, "A3"), (5, "A4"),
                      (6, "A5"), (17, "A6"), (16, "A7"), (15, "A8"), (14, "A9"),
                      (13, "A10"), (12, "A11"), (11, "DIN"), (10, "~{CS}"),
                      (8, "~{WE}")],
               "tri": [(7, "DOUT")],
               "pwr": [(18, "VCC"), (9, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
              "A11", None, "~{CS}", "~{WE}"],
        right=["DIN", None, "DOUT"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-18_W7.62mm",
        description="4Kx1 HMOS static RAM, separate data in/out, automatic power-down",
        keywords="RAM SRAM 4Kx1 2147 HMOS"),
    # TI SN7489 64-bit RAM (Bipolar Microcomputer Components Data Book, 1981, p. 2-41).
    # Outputs are the open-collector complement of the stored data.
    "7489": dict(
        pins=_pins(
            **{"in": [(1, "A0"), (15, "A1"), (14, "A2"), (13, "A3"),
                      (4, "D1"), (6, "D2"), (10, "D3"), (12, "D4"),
                      (2, "~{ME}"), (3, "~{WE}")],
               "oc": [(5, "~{Q1}"), (7, "~{Q2}"), (9, "~{Q3}"), (11, "~{Q4}")],
               "pwr": [(16, "VCC"), (8, "GND")]}),
        left=["A0", "A1", "A2", "A3", None, "D1", "D2", "D3", "D4", None,
              "~{ME}", "~{WE}"],
        right=["~{Q1}", "~{Q2}", "~{Q3}", "~{Q4}"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-16_W7.62mm",
        description="16x4 bipolar TTL RAM, open-collector inverting outputs",
        keywords="RAM SRAM 16x4 TTL scratchpad"),
    # TI SN74S189A (same book, p. 2-49): the 7489 pinout pin for pin, with ~ME/~WE
    # named ~S/~W and 3-state outputs, so it needs its own symbol for ERC.
    "74S189A": dict(
        pins=_pins(
            **{"in": [(1, "A0"), (15, "A1"), (14, "A2"), (13, "A3"),
                      (4, "D1"), (6, "D2"), (10, "D3"), (12, "D4"),
                      (2, "~{S}"), (3, "~{W}")],
               "tri": [(5, "~{Q1}"), (7, "~{Q2}"), (9, "~{Q3}"), (11, "~{Q4}")],
               "pwr": [(16, "VCC"), (8, "GND")]}),
        left=["A0", "A1", "A2", "A3", None, "D1", "D2", "D3", "D4", None,
              "~{S}", "~{W}"],
        right=["~{Q1}", "~{Q2}", "~{Q3}", "~{Q4}"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-16_W7.62mm",
        description="16x4 Schottky TTL RAM, 3-state inverting outputs",
        keywords="RAM SRAM 16x4 TTL Schottky scratchpad"),
    # Hitachi HM6116 2Kx8 (IC Memory Data Book, 1984, p. 65): the JEDEC 24-pin
    # byte-wide pinout, a 2716 with ~WE on pin 21 in place of VPP.
    "HM6116": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"),
                      (3, "A5"), (2, "A6"), (1, "A7"), (23, "A8"), (22, "A9"),
                      (19, "A10"), (18, "~{CS}"), (20, "~{OE}"), (21, "~{WE}")],
               "bidi": [(9, "I/O1"), (10, "I/O2"), (11, "I/O3"), (13, "I/O4"),
                        (14, "I/O5"), (15, "I/O6"), (16, "I/O7"), (17, "I/O8")],
               "pwr": [(24, "VCC"), (12, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10",
              None, "~{CS}", "~{OE}", "~{WE}"],
        right=["I/O1", "I/O2", "I/O3", "I/O4", "I/O5", "I/O6", "I/O7", "I/O8"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="2Kx8 CMOS static RAM, JEDEC 24-pin byte-wide (6116) pinout",
        keywords="RAM SRAM 2Kx8 6116 CMOS"),
    # Motorola MCM6810 (Memory Data Book, 1979, p. 2-74). Six chip selects, four
    # active low and two active high. R/W is printed without an overbar; read = high.
    "MCM6810": dict(
        pins=_pins(
            **{"in": [(23, "A0"), (22, "A1"), (21, "A2"), (20, "A3"), (19, "A4"),
                      (18, "A5"), (17, "A6"), (10, "CS0"), (11, "~{CS1}"),
                      (12, "~{CS2}"), (13, "CS3"), (14, "~{CS4}"), (15, "~{CS5}"),
                      (16, "R/~{W}")],
               "bidi": [(2, "D0"), (3, "D1"), (4, "D2"), (5, "D3"), (6, "D4"),
                        (7, "D5"), (8, "D6"), (9, "D7")],
               "pwr": [(24, "VCC"), (1, "GND")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", None, "CS0", "~{CS1}",
              "~{CS2}", "CS3", "~{CS4}", "~{CS5}", "R/~{W}"],
        right=["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="128x8 NMOS static RAM for 6800 systems, six chip selects",
        keywords="RAM SRAM 128x8 6800 NMOS"),
    # RCA CDP1824 (same book, p. 147). Common I/O; ~MRD is the output enable and
    # overrides ~MWR, so it connects straight to the CDP1802 bus.
    "CDP1824": dict(
        pins=_pins(
            **{"in": [(5, "MA0"), (4, "MA1"), (3, "MA2"), (2, "MA3"), (1, "MA4"),
                      (15, "~{CS}"), (16, "~{MRD}"), (17, "~{MWR}")],
               "bidi": [(14, "BUS0"), (13, "BUS1"), (12, "BUS2"), (11, "BUS3"),
                        (10, "BUS4"), (8, "BUS5"), (7, "BUS6"), (6, "BUS7")],
               "pwr": [(18, "VDD"), (9, "VSS")]}),
        left=["MA0", "MA1", "MA2", "MA3", "MA4", None, "~{CS}", "~{MRD}", "~{MWR}"],
        right=["BUS0", "BUS1", "BUS2", "BUS3", "BUS4", "BUS5", "BUS6", "BUS7"],
        top=["VDD"], bottom=["VSS"],
        footprint="Package_DIP:DIP-18_W7.62mm",
        description="32x8 CMOS static RAM for CDP1802 systems, common I/O",
        keywords="RAM SRAM 32x8 CMOS 1802 COSMAC"),
    # Intel 1103 1Kx1 PMOS DRAM (1975 Intel Data Catalog, p. 2-7). Names from the
    # sheet's pin-name legend. VDD is the 0V reference, VSS the +16/+19V supply and
    # VBB the substrate, 3-4V above VSS. ~DOUT is an inverted open-drain current
    # output (sourced from VSS) that needs a sense amplifier such as the 3208A.
    "1103": dict(
        pins=_pins(
            **{"in": [(3, "A0"), (4, "A1"), (2, "A2"), (1, "A3"), (15, "A4"),
                      (8, "A5"), (7, "A6"), (9, "A7"), (13, "A8"), (6, "A9"),
                      (12, "DIN"), (5, "PRC"), (16, "CE"), (18, "R/W")],
               "oe": [(14, "~{DOUT}")],
               "pwr": [(17, "VSS"), (10, "VBB"), (11, "VDD")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", None,
              "PRC", "CE", "R/W"],
        right=["DIN", None, "~{DOUT}"],
        top=["VSS", "VBB"], bottom=["VDD"],
        footprint="Package_DIP:DIP-18_W7.62mm",
        description="1Kx1 PMOS dynamic RAM, precharge clock, current-sourcing output (1103)",
        keywords="RAM DRAM 1Kx1 1103 PMOS"),
    # Intel 1103A (same catalog, p. 2-15): the 1103 without the precharge clock, so
    # pin 5 is N.C.; otherwise pin for pin the same. Shared by the 1103A-1/-2.
    "1103A": dict(
        pins=_pins(
            **{"in": [(3, "A0"), (4, "A1"), (2, "A2"), (1, "A3"), (15, "A4"),
                      (8, "A5"), (7, "A6"), (9, "A7"), (13, "A8"), (6, "A9"),
                      (12, "DIN"), (16, "CE"), (18, "R/W")],
               "oe": [(14, "~{DOUT}")],
               "nc": [(5, "NC")],
               "pwr": [(17, "VSS"), (10, "VBB"), (11, "VDD")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", None,
              "CE", "R/W"],
        right=["DIN", None, "~{DOUT}"],
        top=["VSS", "VBB"], bottom=["VDD"],
        footprint="Package_DIP:DIP-18_W7.62mm",
        description="1Kx1 PMOS dynamic RAM, current-sourcing output (1103A pinout, pin 5 N.C.)",
        keywords="RAM DRAM 1Kx1 1103A PMOS"),
    # Mostek MK4096 4Kx1 DRAM (1980 Memory Data Book, p. V-17). Shared, pin for pin,
    # by the MK4027 (p. V-1). The MK4116 layout except pin 13, which is ~CS (latched
    # at ~CAS) rather than A6. Three supplies: VDD +12V, VCC +5V, VBB -5V.
    "MK4096": dict(
        pins=_pins(
            **{"in": [(5, "A0"), (7, "A1"), (6, "A2"), (12, "A3"), (11, "A4"),
                      (10, "A5"), (2, "DIN"), (4, "~{RAS}"), (15, "~{CAS}"),
                      (13, "~{CS}"), (3, "~{WRITE}")],
               "tri": [(14, "DOUT")],
               "pwr": [(9, "VCC"), (8, "VDD"), (16, "VSS"), (1, "VBB")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", None,
              "~{RAS}", "~{CAS}", "~{CS}", "~{WRITE}"],
        right=["DIN", None, "DOUT"],
        top=["VCC", "VDD"], bottom=["VSS", "VBB"],
        footprint="Package_DIP:DIP-16_W7.62mm",
        description="4Kx1 dynamic RAM, latched output, chip select, +12V/+5V/-5V (MK4096/MK4027 pinout)",
        keywords="RAM DRAM 4Kx1 4096 4027"),
    # Intel 2118 16Kx1 +5V DRAM (1981 Component Data Catalog, p. 1-16). The MK4116
    # address pins, but 4164-style power (+5V on 8, ground on 16) and N/C on pins 1
    # and 9, so it does not fit a 4116 socket.
    "2118": dict(
        pins=_pins(
            **{"in": [(5, "A0"), (7, "A1"), (6, "A2"), (12, "A3"), (11, "A4"),
                      (10, "A5"), (13, "A6"), (2, "DIN"), (4, "~{RAS}"),
                      (15, "~{CAS}"), (3, "~{WE}")],
               "tri": [(14, "DOUT")],
               "nc": [(1, "N/C"), (9, "N/C")],
               "pwr": [(8, "VDD"), (16, "VSS")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", None,
              "~{RAS}", "~{CAS}", "~{WE}"],
        right=["DIN", None, "DOUT"],
        top=["VDD"], bottom=["VSS"],
        footprint="Package_DIP:DIP-16_W7.62mm",
        description="16Kx1 dynamic RAM, single +5V supply, pins 1 and 9 N/C (2118)",
        keywords="RAM DRAM 16Kx1 2118"),
    # Mostek MK4564 64Kx1 +5V DRAM (1984/1985 Microelectronic Data Book, p. IV-61;
    # same drawing in the 1982 book, p. IV-63). The stock MK4164N pinout with pin 1
    # N/C instead of ~RFSH -- the common JEDEC 4164 arrangement.
    "MK4564": dict(
        pins=_pins(
            **{"in": [(5, "A0"), (7, "A1"), (6, "A2"), (12, "A3"), (11, "A4"),
                      (10, "A5"), (13, "A6"), (9, "A7"), (2, "DIN"), (4, "~{RAS}"),
                      (15, "~{CAS}"), (3, "~{WRITE}")],
               "tri": [(14, "DOUT")],
               "nc": [(1, "N/C")],
               "pwr": [(8, "VCC"), (16, "VSS")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", None,
              "~{RAS}", "~{CAS}", "~{WRITE}"],
        right=["DIN", None, "DOUT"],
        top=["VCC"], bottom=["VSS"],
        footprint="Package_DIP:DIP-16_W7.62mm",
        description="64Kx1 dynamic RAM, single +5V supply, pin 1 N/C (MK4564 / JEDEC 4164 pinout)",
        keywords="RAM DRAM 64Kx1 4564 4164"),
    # TI TMS4416 16Kx4 DRAM (1986 MOS Memory Data Book, p. 4-99, N package). Shared,
    # pin for pin, by the TMS4464 64Kx4 (p. 4-117, "Pinout Identical to TMS4416"):
    # the 4416 uses A7 for rows only, the 4464 for rows and columns. ~G is the
    # output enable; DQ1-DQ4 are common I/O.
    "TMS4416": dict(
        pins=_pins(
            **{"in": [(14, "A0"), (13, "A1"), (12, "A2"), (11, "A3"), (8, "A4"),
                      (7, "A5"), (6, "A6"), (10, "A7"),
                      (5, "~{RAS}"), (16, "~{CAS}"), (4, "~{W}"), (1, "~{G}")],
               "bidi": [(2, "DQ1"), (3, "DQ2"), (15, "DQ3"), (17, "DQ4")],
               "pwr": [(9, "VDD"), (18, "VSS")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", None,
              "~{RAS}", "~{CAS}", "~{W}", "~{G}"],
        right=["DQ1", "DQ2", "DQ3", "DQ4"],
        top=["VDD"], bottom=["VSS"],
        footprint="Package_DIP:DIP-18_W7.62mm",
        description="16Kx4 / 64Kx4 dynamic RAM, common I/O, output enable (TMS4416/TMS4464 pinout)",
        keywords="RAM DRAM 16Kx4 64Kx4 4416 4464 41464"),

    # ---- UV EPROM / OTP EPROM / flash ----------------------------------------------
    # Intel 1702A 256x8 (1979 Component Data Catalog, p. 4-5). Silicon-gate PMOS-era
    # part on +5V/-9V; VCC appears on pins 12, 22 and 23 (stacked) and VBB (pin 15) is
    # tied to VCC in read. The book's data pins are "DATA OUT 1-8" (1 = LSB).
    "1702A": dict(
        pins=_pins(
            **{"in": [(3, "A0"), (2, "A1"), (1, "A2"), (21, "A3"), (20, "A4"),
                      (19, "A5"), (18, "A6"), (17, "A7"), (14, "~{CS}"),
                      (13, "PROGRAM")],
               "tri": [(4, "DO1"), (5, "DO2"), (6, "DO3"), (7, "DO4"), (8, "DO5"),
                       (9, "DO6"), (10, "DO7"), (11, "DO8")],
               "pwr": [(12, "VCC"), (22, "VCC"), (23, "VCC"), (15, "VBB"),
                       (24, "VDD"), (16, "VGG")]}),
        left=["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", None,
              "~{CS}", "PROGRAM"],
        right=["DO1", "DO2", "DO3", "DO4", "DO5", "DO6", "DO7", "DO8"],
        top=["VCC", "VBB"], bottom=["VDD", "VGG"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="256x8 UV EPROM, +5V/-9V, -48V programming (1702A pinout)",
        keywords="EPROM UV 256x8 1702 1702A"),
    # Intel 2708 1Kx8 (1979 catalog, p. 4-20), +12V/+5V/-5V. Shared by the 2704
    # (512x8; pin 22 tied to VSS). PROGRAM (pin 18) must be grounded in read.
    "2708": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"),
                      (3, "A5"), (2, "A6"), (1, "A7"), (23, "A8"), (22, "A9"),
                      (20, "~{CS}/WE"), (18, "PROGRAM")],
               "tri": [(9, "O0"), (10, "O1"), (11, "O2"), (13, "O3"), (14, "O4"),
                       (15, "O5"), (16, "O6"), (17, "O7")],
               "pwr": [(24, "VCC"), (19, "VDD"), (12, "VSS"), (21, "VBB")]}),
        left=[f"A{i}" for i in range(10)] + [None, "~{CS}/WE", "PROGRAM"],
        right=[f"O{i}" for i in range(8)],
        top=["VCC", "VDD"], bottom=["VSS", "VBB"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="1Kx8 UV EPROM, +12V/+5V/-5V (2708/2704 pinout)",
        keywords="EPROM UV 1Kx8 2708 2704"),
    # Intel 2716 2Kx8 +5V (1979 catalog, p. 4-23). Shared by the TI TMS2516 (1982
    # MOS Memory Data Book, p. 137), which names pin 18 PD/PGM and pin 20 ~CS.
    "2716": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"),
                      (3, "A5"), (2, "A6"), (1, "A7"), (23, "A8"), (22, "A9"),
                      (19, "A10"), (18, "~{CE}/PGM"), (20, "~{OE}"), (21, "VPP")],
               "tri": [(9, "O0"), (10, "O1"), (11, "O2"), (13, "O3"), (14, "O4"),
                       (15, "O5"), (16, "O6"), (17, "O7")],
               "pwr": [(24, "VCC"), (12, "GND")]}),
        left=[f"A{i}" for i in range(11)] + [None, "~{CE}/PGM", "~{OE}", "VPP"],
        right=[f"O{i}" for i in range(8)],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="2Kx8 UV EPROM, +5V, VPP on pin 21 (Intel 2716 / TMS2516 pinout)",
        keywords="EPROM UV 2Kx8 2716 2516"),
    # Intel 2732 4Kx8 (1979 catalog, p. 4-28). Shared by the 2732A (1983 Memory
    # Components Handbook, p. 4-12), which programs at 21V instead of 25V.
    "2732": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"),
                      (3, "A5"), (2, "A6"), (1, "A7"), (23, "A8"), (22, "A9"),
                      (19, "A10"), (21, "A11"), (18, "~{CE}"), (20, "~{OE}/VPP")],
               "tri": [(9, "O0"), (10, "O1"), (11, "O2"), (13, "O3"), (14, "O4"),
                       (15, "O5"), (16, "O6"), (17, "O7")],
               "pwr": [(24, "VCC"), (12, "GND")]}),
        left=[f"A{i}" for i in range(12)] + [None, "~{CE}", "~{OE}/VPP", None],
        right=[f"O{i}" for i in range(8)],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="4Kx8 UV EPROM, +5V, ~OE/VPP on pin 20 (Intel 2732/2732A pinout)",
        keywords="EPROM UV 4Kx8 2732 2732A"),
    # TI TMS2716 2Kx8, +12V/+5V/-5V (1982 MOS Memory Data Book, p. 167). Not the Intel
    # 2716: VDD on 19, VBB on 21; pin 24 is VCC in read and program enable (+12V).
    "TMS2716": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"),
                      (3, "A5"), (2, "A6"), (1, "A7"), (23, "A8"), (22, "A9"),
                      (20, "A10"), (18, "~{CS}/PGM")],
               "tri": [(9, "Q1"), (10, "Q2"), (11, "Q3"), (13, "Q4"), (14, "Q5"),
                       (15, "Q6"), (16, "Q7"), (17, "Q8")],
               "pwr": [(24, "VCC"), (19, "VDD"), (12, "VSS"), (21, "VBB")]}),
        left=[f"A{i}" for i in range(11)] + [None, "~{CS}/PGM"],
        right=[f"Q{i}" for i in range(1, 9)],
        top=["VCC", "VDD"], bottom=["VSS", "VBB"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="2Kx8 UV EPROM, +12V/+5V/-5V (TI TMS2716 pinout, not Intel 2716)",
        keywords="EPROM UV 2Kx8 TMS2716"),
    # TI TMS2532 4Kx8 +5V (1982 MOS Memory Data Book, p. 145). Differs from the Intel
    # 2732 on pins 18 (A11), 20 (PD/~PGM, the only control pin) and 21 (VPP).
    "TMS2532": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"),
                      (3, "A5"), (2, "A6"), (1, "A7"), (23, "A8"), (22, "A9"),
                      (19, "A10"), (18, "A11"), (20, "PD/~{PGM}"), (21, "VPP")],
               "tri": [(9, "Q1"), (10, "Q2"), (11, "Q3"), (13, "Q4"), (14, "Q5"),
                       (15, "Q6"), (16, "Q7"), (17, "Q8")],
               "pwr": [(24, "VCC"), (12, "VSS")]}),
        left=[f"A{i}" for i in range(12)] + [None, "PD/~{PGM}", "VPP"],
        right=[f"Q{i}" for i in range(1, 9)],
        top=["VCC"], bottom=["VSS"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="4Kx8 UV EPROM, +5V (TI TMS2532 pinout, not Intel 2732)",
        keywords="EPROM UV 4Kx8 TMS2532 2532"),
    # Motorola MCM68764 8Kx8 in 24 pins (1980 Memory Data Book, p. 2-148): the
    # MCM68A364 mask-ROM pinout with ~E/VPP on pin 20 and A12 on pin 21.
    "MCM68764": dict(
        pins=_pins(
            **{"in": [(8, "A0"), (7, "A1"), (6, "A2"), (5, "A3"), (4, "A4"),
                      (3, "A5"), (2, "A6"), (1, "A7"), (23, "A8"), (22, "A9"),
                      (19, "A10"), (18, "A11"), (21, "A12"), (20, "~{E}/VPP")],
               "tri": [(9, "DQ0"), (10, "DQ1"), (11, "DQ2"), (13, "DQ3"), (14, "DQ4"),
                       (15, "DQ5"), (16, "DQ6"), (17, "DQ7")],
               "pwr": [(24, "VCC"), (12, "VSS")]}),
        left=[f"A{i}" for i in range(13)] + [None, "~{E}/VPP"],
        right=[f"DQ{i}" for i in range(8)],
        top=["VCC"], bottom=["VSS"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="8Kx8 UV EPROM in 24 pins, ~E/VPP on pin 20 (MCM68764 / 2364 mask-ROM pinout)",
        keywords="EPROM UV 8Kx8 MCM68764 68764 2364"),
    # Microchip (SST) SST39SF010A/020A/040 5V multi-purpose flash (DS20005022,
    # fig. 2-1). JEDEC 27C010-040 read pinout with ~WE on pin 31. The stock
    # Memory_Flash:SST39SF0x0 symbols name ~WE "PGM", drop the active-low bars and
    # type the NC pins as inputs, so these replace them.
    "SST39SF010A": dict(
        pins=_pins(
            **{"in": _SST_ADDR + [(22, "~{CE}"), (24, "~{OE}"), (31, "~{WE}")],
               "bidi": _SST_DQ, "nc": [(1, "NC"), (30, "NC")],
               "pwr": [(32, "VDD"), (16, "VSS")]}),
        left=[f"A{i}" for i in range(17)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=[f"DQ{i}" for i in range(8)],
        top=["VDD"], bottom=["VSS"],
        footprint="Package_DIP:DIP-32_W15.24mm",
        description="128Kx8 5V flash, pins 1 and 30 NC (SST39SF010A pinout)",
        keywords="flash 128Kx8 SST39SF010A 39SF"),
    "SST39SF020A": dict(
        pins=_pins(
            **{"in": _SST_ADDR + [(30, "A17"), (22, "~{CE}"), (24, "~{OE}"), (31, "~{WE}")],
               "bidi": _SST_DQ, "nc": [(1, "NC")],
               "pwr": [(32, "VDD"), (16, "VSS")]}),
        left=[f"A{i}" for i in range(18)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=[f"DQ{i}" for i in range(8)],
        top=["VDD"], bottom=["VSS"],
        footprint="Package_DIP:DIP-32_W15.24mm",
        description="256Kx8 5V flash, pin 1 NC (SST39SF020A pinout)",
        keywords="flash 256Kx8 SST39SF020A 39SF"),
    "SST39SF040": dict(
        pins=_pins(
            **{"in": _SST_ADDR + [(30, "A17"), (1, "A18"), (22, "~{CE}"), (24, "~{OE}"),
                                  (31, "~{WE}")],
               "bidi": _SST_DQ,
               "pwr": [(32, "VDD"), (16, "VSS")]}),
        left=[f"A{i}" for i in range(19)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=[f"DQ{i}" for i in range(8)],
        top=["VDD"], bottom=["VSS"],
        footprint="Package_DIP:DIP-32_W15.24mm",
        description="512Kx8 5V flash (SST39SF040 pinout)",
        keywords="flash 512Kx8 SST39SF040 39SF"),
    # Intel 2816 2Kx8 EEPROM (1981 Component Data Catalog, Figure 2, p. 2-23): the 2716
    # pinout with a 21V write/erase pulse on VPP (pin 21) and no on-chip latches.
    "2816": dict(
        pins=_pins(
            **{"in": _A24 + [(18, "~{CE}"), (20, "~{OE}"), (21, "VPP")],
               "bidi": _IO24, "pwr": [(24, "VCC"), (12, "GND")]}),
        left=[f"A{i}" for i in range(11)] + [None, "~{CE}", "~{OE}", "VPP"],
        right=[f"I/O{i}" for i in range(8)],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="2Kx8 EEPROM, 21V write pulse on VPP pin 21 (Intel 2816 pinout)",
        keywords="EEPROM E2PROM 2Kx8 2816"),
    # Intel 2816A 2Kx8 5V EEPROM (1984 Memory Components Handbook, p. 5-83): the 6116
    # static-RAM pinout, ~WE on pin 21. Shared by the Xicor X2816A/B/C (1985 p. 3-13,
    # 1990 pp. 3-9, 3-19), SEEQ 2816A and 52B13 (1985 pp. 2-4, 2-20) and Atmel
    # AT28C16 (1990 p. 2-51). The 2816A also takes the 2816's 21V pulse on pin 21.
    "2816A": dict(
        pins=_pins(
            **{"in": _A24 + [(18, "~{CE}"), (20, "~{OE}"), (21, "~{WE}")],
               "bidi": _IO24, "pwr": [(24, "VCC"), (12, "GND")]}),
        left=[f"A{i}" for i in range(11)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=[f"I/O{i}" for i in range(8)],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-24_W15.24mm",
        description="2Kx8 5V EEPROM, ~WE on pin 21 (2816A / X2816 / AT28C16, 6116 pinout)",
        keywords="EEPROM E2PROM 2Kx8 2816A 28C16 X2816 6116"),
    # Intel 2817A 2Kx8 EEPROM in 28 pins (1984 handbook, Figure 2, p. 5-95): the 2864
    # site with A11/A12 NC and open-drain RDY/~BUSY on pin 1. Shared by the Atmel
    # AT28C17 (1990 p. 2-61).
    "2817A": dict(
        pins=_pins(
            **{"in": _A28 + [(20, "~{CE}"), (22, "~{OE}"), (27, "~{WE}")],
               "bidi": _IO28, "oc": [(1, "RDY/~{BUSY}")],
               "nc": [(2, "NC"), (23, "NC"), (26, "NC")],
               "pwr": [(28, "VCC"), (14, "GND")]}),
        left=[f"A{i}" for i in range(11)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=[f"I/O{i}" for i in range(8)] + [None, "RDY/~{BUSY}"],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-28_W15.24mm",
        description="2Kx8 5V EEPROM in 28 pins, RDY/~BUSY on pin 1 (2817A / AT28C17)",
        keywords="EEPROM E2PROM 2Kx8 2817A 28C17"),
    # SEEQ 52B33 8Kx8 latched EEPROM (1985 Data Book, p. 2-27): the 2864 site with an
    # active-low chip-clear input ~CC on pin 1 instead of RDY/~BUSY.
    "52B33": dict(
        pins=_pins(
            **{"in": [(n, f"A{i}") for i, n in enumerate(
                       [10, 9, 8, 7, 6, 5, 4, 3, 25, 24, 21, 23, 2])]
                     + [(20, "~{CE}"), (22, "~{OE}"), (27, "~{WE}"), (1, "~{CC}")],
               "bidi": _IO28, "nc": [(26, "NC")],
               "pwr": [(28, "VCC"), (14, "GND")]}),
        left=[f"A{i}" for i in range(13)] + [None, "~{CE}", "~{OE}", "~{WE}", "~{CC}"],
        right=[f"I/O{i}" for i in range(8)],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-28_W15.24mm",
        description="8Kx8 EEPROM, chip clear ~CC on pin 1 (SEEQ 52B33 pinout)",
        keywords="EEPROM E2PROM 8Kx8 52B33 2864"),
    # 128Kx8 EEPROM, Atmel AT28C010 (1990 Data Book, p. 2-125) and Xicor X28C010 (1990
    # p. 3-111): the JEDEC 32-pin byte-wide site with pins 1 and 30 NC.
    "28C010": dict(
        pins=_pins(
            **{"in": [(n, f"A{i}") for i, n in enumerate(
                       [12, 11, 10, 9, 8, 7, 6, 5, 27, 26, 23, 25, 4, 28, 29, 3, 2])]
                     + [(22, "~{CE}"), (24, "~{OE}"), (31, "~{WE}")],
               "bidi": _IO32, "nc": [(1, "NC"), (30, "NC")],
               "pwr": [(32, "VCC"), (16, "GND")]}),
        left=[f"A{i}" for i in range(17)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=[f"I/O{i}" for i in range(8)],
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-32_W15.24mm",
        description="128Kx8 5V EEPROM, pins 1 and 30 NC (AT28C010 / X28C010 pinout)",
        keywords="EEPROM E2PROM 128Kx8 28C010 X28C010"),
}

# Add the bipolar PROM pinouts: an open-collector and a 3-state symbol per pinout.
for (_oc, _ts), (_a, _o, _e, _vcc, _gnd, _n, _org, _nc, _kw) in _PROMS.items():
    for _name, _type, _what in ((_oc, "oc", "open-collector"), (_ts, "tri", "3-state")):
        PINOUTS[_name] = _prom(
            _a, _o, _e, _vcc, _gnd, _type, _n,
            f"{_org} bipolar fuse PROM, {_what} outputs ({_name} pinout)",
            f"PROM bipolar fuse {_org} {_kw}", _nc)

