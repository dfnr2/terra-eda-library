#!/usr/bin/env python3
"""Zilog Z80 CPUs: NMOS Z80/Z80A/Z80B/Z80H and CMOS Z84C00.

One classic maker (Zilog), every speed grade, plastic DIP, commercial temperature
where the book offers it. All Obsolete: the NMOS parts long ago, the Z84C00 by
Zilog's EOL notice of 2024-04-15 (Digi-Key shows Z84C0010PEG Obsolete, 2026-11-20).

Sources (datasheets/zilog/):
  - 1982 Zilog Data Book, "Z8400 Z80 CPU Product Specification" (June 1982), book
    pp. 5-26 (PDF 16-37) plus the 40-pin outlines (PDF 549/550). Ordering table
    p. 26 prints "Z8400 PS", "Z8400A PS", "Z8400B PS" (P plastic, S 0-70 C), written
    here without the space. ICC 150 mA (Z80), 200 mA (Z80A/B).
  - 1989 Zilog Z80 Family Data Book, "Z8400/Z84C00 NMOS/CMOS Z80 CPU Product
    Specification" (January 1989, ADVANCED INFORMATION), PDF 8-29, ordering pages
    433/436 and the 40-pin outline (438). Gives the 8 MHz NMOS Z80H (Z0840008PSC,
    which the 1982 book lacks) and the CMOS codes: Z84C0004/06/08PSC (0-70 C) and
    Z84C0010PEC (10 MHz comes only in E, -40 to 100 C). CMOS ICC 20/30/40/50 mA at
    4/6/8/10 MHz, 10 uA standby with the clock stopped.

Symbol: stock KiCad CPU:Z84C00xxP for every grade; the NMOS and CMOS parts share the
pinout, checked pin for pin against both books.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _cpu import EXT_1PH, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_microprocessors_generated_330_z80.sql")
CREATED_BY = Path(__file__).name
SYMBOL = "CPU:Z84C00xxP"
DS_1982 = "zilog/z80-cpu-8-bit-microprocessor.pdf"
DS_1989 = "zilog/z84c00-z8400-cmos-nmos-z80-cpu.pdf"
FEATURES = ("158 instructions (8080A superset); alternate register set; IX/IY; "
            "built-in DRAM refresh (RFSH, R register); interrupt modes 0/1/2 with "
            "daisy-chain vectoring; BUSREQ/BUSACK; external clock (VIH Vcc-0.6)")

# (mpn, value, technology, MHz, ICC, datasheet, temperature)
PARTS = [
    ("Z8400PS", "Z80", "NMOS", 2.5, "150mA max", DS_1982, (0, 70)),
    ("Z8400APS", "Z80A", "NMOS", 4, "200mA max", DS_1982, (0, 70)),
    ("Z8400BPS", "Z80B", "NMOS", 6, "200mA max", DS_1982, (0, 70)),
    ("Z0840008PSC", "Z80H", "NMOS", 8, "200mA max", DS_1989, (0, 70)),
    ("Z84C0004PSC", "Z84C00", "CMOS", 4, "20mA max", DS_1989, (0, 70)),
    ("Z84C0006PSC", "Z84C00", "CMOS", 6, "30mA max", DS_1989, (0, 70)),
    ("Z84C0008PSC", "Z84C00", "CMOS", 8, "40mA max", DS_1989, (0, 70)),
    ("Z84C0010PEC", "Z84C00", "CMOS", 10, "50mA max", DS_1989, (-40, 100)),
]


def records():
    for mpn, value, tech, clock, icc, ds, temp in PARTS:
        cmos = tech == "CMOS"
        extra = "; static: 10uA standby with clock stopped" if cmos else ""
        yield row(
            created_by=CREATED_BY, manufacturer="Zilog", mpn=mpn, value=value,
            family="Z80", core=f"{tech} Z80", technology=tech, arch_bits=8,
            data_bits=8, addr_bits=16, clock=clock, clock_source=EXT_1PH, vmin=4.75,
            vmax=5.25, rails="+5V", active_current=icc, package="PDIP-40", pins=40,
            symbol=SYMBOL, datasheet=ds, temp=temp,
            description=(f"Zilog {value} {tech} 8-bit CPU, {clock:g}MHz, "
                         f"{temp[0]} to {temp[1]}C, PDIP-40"),
            keywords=["Z80", value, "Z8400", "Zilog", tech, "8-bit", "vintage"],
            features=FEATURES + extra)


def main():
    write(OUTPUT_FILE, "Zilog Z80", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
