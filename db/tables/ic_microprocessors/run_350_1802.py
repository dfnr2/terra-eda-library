#!/usr/bin/env python3
"""RCA CDP1802 COSMAC CMOS CPUs: CDP1802A, CDP1802AC, CDP1802BC.

One classic maker (RCA), each type in plastic DIP (E suffix). All Obsolete in
plastic. Renesas (via Intersil) still lists the CDP1802A as Active, but only as the
military CDP1802ACD3 in side-brazed ceramic, which neither Digi-Key nor Mouser
carries (checked 2026-11-20), so it is not generated; the Renesas page is used as
manufacturer_link.

Source: 1982 RCA CMOS LSI Products data book (datasheets/rca/, cut to both sheets
plus the 40-lead plastic and ceramic outlines, book pp. 552/554):
  - CDP1802A/CDP1802AC, book pp. 14-35: A runs 4-10.5 V (3.2 MHz at 5 V, 6.4 MHz at
    10 V), AC 4-6.5 V (3.2 MHz at 5 V).
  - CDP1802BC, book pp. 36-55, "Preliminary Data": 4-6.5 V, 5 MHz at 5 V.
The book prints only a suffix key (p. 6: D ceramic, E plastic; example CDP1802AD),
so the E codes are built from it. Temperature is the printed -40 to 85 C. The
sheets give quiescent IDD (50-200 uA) but no active-current maximum, so
active_current is NULL.

Symbols: stock KiCad CPU:CDP1802ACE and CPU:CDP1802BCE, checked pin for pin (the
stock symbol bars XTAL, which the book does not).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _cpu import ON_CHIP, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_microprocessors_generated_350_1802.sql")
CREATED_BY = Path(__file__).name
FEATURES = ("fully static (DC clock allowed); on-chip oscillator (crystal between "
            "CLOCK and XTAL); 16x16-bit register file; address multiplexed on MA0-MA7 "
            "(high byte latched by TPA); DMA in/out; interrupt; EF1-EF4 flags; Q "
            "output; N0-N2 I/O lines")

# (mpn, value, vmax, MHz at 5V, symbol, note)
PARTS = [
    ("CDP1802AE", "CDP1802A", 10.5, 3.2, "CPU:CDP1802ACE", "4-10.5V (6.4MHz at 10V)"),
    ("CDP1802ACE", "CDP1802AC", 6.5, 3.2, "CPU:CDP1802ACE", "4-6.5V"),
    ("CDP1802BCE", "CDP1802BC", 6.5, 5, "CPU:CDP1802BCE", "4-6.5V"),
]


def records():
    for mpn, value, vmax, clock, symbol, note in PARTS:
        yield row(
            created_by=CREATED_BY, manufacturer="RCA", mpn=mpn, value=value,
            family="1802", core="CMOS 1802 COSMAC", technology="CMOS", arch_bits=8,
            data_bits=8, addr_bits=16, clock=clock, clock_source=ON_CHIP, vmin=4.0,
            vmax=vmax, rails="+5V" if vmax < 7 else "+5V to +10V", package="PDIP-40",
            pins=40, symbol=symbol, temp=(-40, 85),
            datasheet="rca/cdp1802-cmos-8-bit-microprocessor.pdf",
            mfr_link="https://www.renesas.com/en/products/cdp1802a",
            description=(f"RCA {value} COSMAC CMOS 8-bit CPU, {clock:g}MHz at 5V, "
                         f"{note}, PDIP-40"),
            keywords=["1802", "CDP1802", "COSMAC", "RCA", "CMOS", "8-bit", "vintage"],
            features=FEATURES)


def main():
    write(OUTPUT_FILE, "RCA CDP1802", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
