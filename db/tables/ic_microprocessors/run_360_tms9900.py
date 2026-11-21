#!/usr/bin/env python3
"""Texas Instruments TMS9900 16-bit NMOS CPU.

One row: TMS9900NL (plastic DIP, 0 to 70 C, 3 MHz). Obsolete.

Sources (datasheets/ti/):
  - TMS 9900 Microprocessor Data Manual, May 1976 (TENTATIVE DATA), cut to the
    introduction, architecture, pin, timing, electrical and mechanical pages (the
    instruction-set chapter is left out). Supplies VBB -5 V, VCC +5 V, VDD +12 V;
    ICC 125 mA, IDD 30 mA, IBB 1 mA max; 0.333 us clock cycle (3 MHz); 64-pin DIP
    with 0.900 in row spacing.
  - 1978 9900 Family Systems Design and Data Book, numbering system p. 8-392: TM + S
    + part + package (N plastic, J ceramic) + temperature (L = 0 to 70 C) + speed.
    No TMS9900 code is printed, so TMS9900NL is built from that key (the same page
    prints "TMS 9901 JL, NL"). The 4 MHz TMS9900-40 is not generated: its suffix
    placement isn't shown.

Symbol: custom terra_symbols_ic_microprocessors:TMS9900 (no stock symbol). TI numbers
bits MSB first, so A0 and D0 are the most significant bits.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _cpu import EXT_4PH, LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_microprocessors_generated_360_tms9900.sql")
CREATED_BY = Path(__file__).name


def records():
    yield row(
        created_by=CREATED_BY, manufacturer="Texas Instruments", mpn="TMS9900NL",
        value="TMS9900", family="9900", core="NMOS TMS9900", technology="NMOS",
        arch_bits=16, data_bits=16, addr_bits=15, clock=3, clock_source=EXT_4PH,
        vmin=4.75, vmax=5.25, rails="+12V, +5V, -5V",
        active_current="ICC 125mA, IDD 30mA, IBB 1mA max", package="PDIP-64 900mil",
        pins=64, width_in=0.9, symbol=f"{LIB}:TMS9900",
        datasheet="ti/tms9900-16-bit-microprocessor.pdf",
        description=("TI TMS9900 NMOS 16-bit CPU, 32K-word (64KB) address, four-phase "
                     "12V clock, +12V/+5V/-5V, 3MHz, PDIP-64 900mil"),
        keywords=["9900", "TMS9900", "TI", "NMOS", "16-bit", "CRU", "vintage"],
        features="memory-to-memory architecture (workspace registers in RAM); CRU "
                 "serial I/O (CRUIN/CRUOUT/CRUCLK); 16 interrupt levels (INTREQ, "
                 "IC0-IC3); LOAD non-maskable trap; HOLD/HOLDA; external four-phase "
                 "clock")


def main():
    write(OUTPUT_FILE, "TI TMS9900", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
