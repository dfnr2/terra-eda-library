#!/usr/bin/env python3
"""Motorola 68000-family CPUs in DIP: MC68000, MC68008, MC68010.

One classic maker (Motorola), every clock grade the ordering table lists in plastic
DIP, commercial temperature (0 to 70 C, no C/A prefix). All Obsolete. PLCC (FN),
LCC (ZB/ZC) and PGA (R/RC) versions exist but are out of scope.

Sources (Advance Information data sheets, cut to the signal description, electrical
characteristics, ordering and package pages, in datasheets/motorola/):
  - MC68000 16-Bit Microprocessor, April 1983 (ADI-814-R4). Ordering p. 9-1: this
    sheet calls the plastic DIP "G" (plastic with heat spreader) and has no P codes:
    MC68000G4/G6/G8/G10/G12. Power dissipation 1.5 W (1.75 W at 12.5 MHz).
  - MC68008, April 1985 (ADI939R2). Ordering p. 9-1: MC68008P8/P10 (48-pin DIP; the
    52-pin FN adds A20/A21, BGACK and a separate IPL2).
  - MC68010/MC68012, May 1985 (ADI942R2). Ordering p. 9-1: MC68010P8/P10 (no plastic
    12.5 MHz part). The MC68012 is PGA only.

The 64-pin DIPs are 0.9" wide (CASE 746/754: 22.86 mm row spacing), the 48-pin DIP
0.6" (CASE 767). Symbols: stock KiCad CPU_NXP_68000 MC68000P/MC68008P/MC68010P,
checked pin for pin against the data sheets.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _cpu import EXT_1PH, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_microprocessors_generated_320_68000.sql")
CREATED_BY = Path(__file__).name
STOCK = "CPU_NXP_68000"

COMMON_FEATURES = ("asynchronous bus (DTACK); 7 interrupt levels on IPL pins; "
                   "BR/BG bus arbitration; E/VPA/VMA 6800-peripheral interface; "
                   "external TTL clock (must not stop)")

# chip -> dict of per-chip facts; grades -> {suffix: MHz}
CHIPS = {
    "MC68000": dict(
        grades={"G4": 4, "G6": 6, "G8": 8, "G10": 10, "G12": 12.5}, pins=64,
        width_in=0.9, data=16, addr=24, ds="mc68000-16-bit-microprocessor.pdf",
        desc="HMOS 16/32-bit CPU, 16-bit data, 24-bit address",
        features=COMMON_FEATURES, symbol="MC68000P"),
    "MC68008": dict(
        grades={"P8": 8, "P10": 10}, pins=48, width_in=0.6, data=8, addr=20,
        ds="mc68008-8-bit-bus-microprocessor.pdf",
        desc="HMOS 8/32-bit CPU, 8-bit data, 20-bit address",
        features="68000 core with 8-bit data bus and single DS strobe; IPL2/IPL0 "
                 "share pin 42 (levels 0, 2, 5, 7); no VMA or BGACK on the DIP; "
                 "external TTL clock (must not stop)", symbol="MC68008P"),
    "MC68010": dict(
        grades={"P8": 8, "P10": 10}, pins=64, width_in=0.9, data=16, addr=24,
        ds="mc68010-virtual-memory-microprocessor.pdf",
        desc="HMOS 16/32-bit virtual-memory CPU, 16-bit data, 24-bit address",
        features="68000 pin compatible; restartable bus-error exceptions for "
                 "virtual memory; vector base register; loop mode; " + COMMON_FEATURES,
        symbol="MC68010P"),
}


def records():
    for chip, c in CHIPS.items():
        for suffix, clock in c["grades"].items():
            pd = "1.75W max" if clock > 10 else "1.5W max"
            wide = " 900mil" if c["width_in"] == 0.9 else ""
            yield row(
                created_by=CREATED_BY, manufacturer="Motorola", mpn=f"{chip}{suffix}",
                value=chip, family="68000", core=f"HMOS {chip[2:]}", technology="HMOS",
                arch_bits=32, data_bits=c["data"], addr_bits=c["addr"], clock=clock,
                clock_source=EXT_1PH, vmin=4.75, vmax=5.25, rails="+5V",
                active_current=pd, package=f"PDIP-{c['pins']}{wide}", pins=c["pins"],
                width_in=c["width_in"], symbol=f"{STOCK}:{c['symbol']}",
                datasheet=f"motorola/{c['ds']}",
                description=(f"Motorola {chip} {c['desc']}, {clock:g}MHz, "
                             f"PDIP-{c['pins']}{wide}"),
                keywords=[chip[2:], "68000", "68k", "m68k", "Motorola", "HMOS",
                          "16-bit", "32-bit", "vintage"],
                features=c["features"])


def main():
    write(OUTPUT_FILE, "Motorola 68000 family", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
