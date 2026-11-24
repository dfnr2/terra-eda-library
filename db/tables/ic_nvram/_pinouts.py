"""Pin tables for the custom ic_nvram DIP symbols.

The 2Kx8, 32Kx8 and 512Kx8 modules match stock Memory_RAM symbols pin for pin
(M48Zx2, HM62256BLP, AS6C4008-55PCN) and use those. These two don't: where the
JEDEC SRAM has a second, active-high chip select (6264 pin 26, 628128 pin 30), the
NVRAM module leaves the pin unconnected, so a stock 6264 or 628128 symbol would
show an input that isn't there. Names follow the Dallas sheets (DQ, CE, OE, WE,
GND). Write the symbols with

    python3 tools/make_dip_symbol.py db/tables/ic_nvram/_pinouts.py \\
        kicad_symbols/terra_symbols_ic_nvram.kicad_sym

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


_DQ = ["DQ0", "DQ1", "DQ2", "DQ3", "DQ4", "DQ5", "DQ6", "DQ7"]

PINOUTS = {
    # Dallas DS1225AB/AD 8Kx8 (ADI datasheet 19-5625 Rev 11/10, p. 1). Pins 1 and 26
    # are NC, the 2764 EPROM layout. Shared pin for pin by the ST M48Z08/M48Z18
    # (DocID02424 Rev 10, fig. 2) and M48Z58/M48Z58Y (DocID02559 Rev 13, fig. 2).
    "DS1225": dict(
        pins=_pins(
            **{"in": [(10, "A0"), (9, "A1"), (8, "A2"), (7, "A3"), (6, "A4"),
                      (5, "A5"), (4, "A6"), (3, "A7"), (25, "A8"), (24, "A9"),
                      (21, "A10"), (23, "A11"), (2, "A12"),
                      (20, "~{CE}"), (22, "~{OE}"), (27, "~{WE}")],
               "bidi": [(11, "DQ0"), (12, "DQ1"), (13, "DQ2"), (15, "DQ3"),
                        (16, "DQ4"), (17, "DQ5"), (18, "DQ6"), (19, "DQ7")],
               "nc": [(1, "NC"), (26, "NC")],
               "pwr": [(28, "VCC"), (14, "GND")]}),
        left=[f"A{i}" for i in range(13)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=_DQ,
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-28_W15.24mm",
        description="8Kx8 battery-backed nonvolatile SRAM module, 6264 socket "
                    "(pin 26 NC)",
        keywords="NVRAM NV SRAM 8Kx8 DS1225 M48Z08 M48Z58 6264"),
    # Dallas DS1245Y/AB 128Kx8 (ADI datasheet 19-5638 Rev 11/10, p. 1). Pins 1 and 30
    # are NC where the 628128 has CE2.
    "DS1245": dict(
        pins=_pins(
            **{"in": [(12, "A0"), (11, "A1"), (10, "A2"), (9, "A3"), (8, "A4"),
                      (7, "A5"), (6, "A6"), (5, "A7"), (27, "A8"), (26, "A9"),
                      (23, "A10"), (25, "A11"), (4, "A12"), (28, "A13"), (3, "A14"),
                      (31, "A15"), (2, "A16"),
                      (22, "~{CE}"), (24, "~{OE}"), (29, "~{WE}")],
               "bidi": [(13, "DQ0"), (14, "DQ1"), (15, "DQ2"), (17, "DQ3"),
                        (18, "DQ4"), (19, "DQ5"), (20, "DQ6"), (21, "DQ7")],
               "nc": [(1, "NC"), (30, "NC")],
               "pwr": [(32, "VCC"), (16, "GND")]}),
        left=[f"A{i}" for i in range(17)] + [None, "~{CE}", "~{OE}", "~{WE}"],
        right=_DQ,
        top=["VCC"], bottom=["GND"],
        footprint="Package_DIP:DIP-32_W15.24mm",
        description="128Kx8 battery-backed nonvolatile SRAM module, 628128 socket "
                    "(pin 30 NC)",
        keywords="NVRAM NV SRAM 128Kx8 DS1245 628128"),
}


def _st_8k(pin1):
    """ST 8Kx8 TIMEKEEPER: the 6264 pinout with E1/E2 chip enables and an open-drain
    output on pin 1 (pin1 = (name, description) )."""
    return _pins(
        **{"in": [(10, "A0"), (9, "A1"), (8, "A2"), (7, "A3"), (6, "A4"), (5, "A5"),
                  (4, "A6"), (3, "A7"), (25, "A8"), (24, "A9"), (21, "A10"),
                  (23, "A11"), (2, "A12"), (20, "~{E1}"), (26, "E2"), (22, "~{G}"),
                  (27, "~{W}")],
           "bidi": [(11, "DQ0"), (12, "DQ1"), (13, "DQ2"), (15, "DQ3"), (16, "DQ4"),
                    (17, "DQ5"), (18, "DQ6"), (19, "DQ7")],
           "oc": [(1, pin1)],
           "pwr": [(28, "VCC"), (14, "VSS")]})


# ST 8Kx8 TIMEKEEPER SRAMs. Pinouts from each sheet's fig. 3 (DIP connections) and
# signal-names table: M48T08/M48T18 Doc ID 2411 Rev 11, pin 1 INT = power-fail
# interrupt (open drain, needs a pull-up even if unused); M48T58/M48T58Y Doc ID 2412
# Rev 8, pin 1 FT = frequency test output (open drain). Both have E2 (active-high chip
# enable 2) on pin 26, so neither the DS1225 symbol (pin 26 NC) nor a 6264 with
# pin 1 NC fits.
PINOUTS["M48T08"] = dict(
    pins=_st_8k("~{INT}"),
    left=[f"A{i}" for i in range(13)] + [None, "~{E1}", "E2", "~{G}", "~{W}"],
    right=_DQ + [None, "~{INT}"],
    top=["VCC"], bottom=["VSS"],
    footprint="Package_DIP:DIP-28_W15.24mm",
    description="8Kx8 TIMEKEEPER SRAM with real-time clock, battery-backed, "
                "power-fail interrupt output (ST M48T08/M48T18)",
    keywords="TIMEKEEPER RTC NVRAM 8Kx8 M48T08 M48T18 6264")
PINOUTS["M48T58"] = dict(
    pins=_st_8k("FT"),
    left=[f"A{i}" for i in range(13)] + [None, "~{E1}", "E2", "~{G}", "~{W}"],
    right=_DQ + [None, "FT"],
    top=["VCC"], bottom=["VSS"],
    footprint="Package_DIP:DIP-28_W15.24mm",
    description="8Kx8 TIMEKEEPER SRAM with real-time clock, battery-backed, "
                "frequency-test output (ST M48T58/M48T58Y)",
    keywords="TIMEKEEPER RTC NVRAM 8Kx8 M48T58 M48T58Y 6264")
