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
}
