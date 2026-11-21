#!/usr/bin/env python3
"""Motorola 68000-family peripherals: MC68230 PI/T, MC68901 MFP, MC68681 DUART.

One classic maker (Motorola), every grade printed, plastic DIP, commercial
temperature. All Obsolete; manufacturer_link NULL.

Sources (datasheets/motorola/):
  - MC68230: 1981 Motorola Microprocessors Data Manual, book 4-783..4-811 (Advance
    Information), with the 48-pin Case 740 outline (book 5-9). The sheet prints only
    the ceramic MC68230L8 and MC68230L10 (8 and 10 MHz) and "P SUFFIX PLASTIC
    PACKAGE AVAILABLE 2Q82", so MC68230P8 and MC68230P10 are built from it. HMOS;
    PINT 500 mW max. The 1984 16/32-bit book has no 68230 sheet.
  - MC68901: January 1984 manual (Advance Information), ordering p. 8-3 prints
    MC68901P (plastic, 4 MHz). ICC 180 mA max. Process not stated, so technology is
    NULL.
  - MC68681: September 1985 manual (Advance Information), ordering p. 6-1 prints
    MC68681P (plastic, 4 MHz X1/CLK; the bus is asynchronous). ICC 150 mA max;
    3.6864 MHz baud crystal. Process not stated. The MC2681/MC2682 general-bus
    variants in the same manual are not generated (one classic part per chip).

Symbols: custom terra_symbols_ic_peripherals MC68230, MC68901 and MC68681. The stock
Interface:68230 and Interface:68681 match pin for pin but drop every active-low bar;
the stock MC68901 is PLCC only.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _per import LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_peripherals_generated_320_68000.sql")
CREATED_BY = Path(__file__).name

F68230 = ("ports A and B (8/16-bit, uni- or bidirectional, double-buffered) with H1-"
          "H4 handshake; port C bit I/O shared with timer and interrupt pins; 24-bit "
          "timer with 5-bit prescaler; vectored port and timer interrupts; DMAREQ for "
          "the MC68450")
F68901 = ("USART (async, and byte-sync with external CRC); four 8-bit timers (A/B "
          "delay, pulse-width, event count; C/D delay); 8 I/O lines each an "
          "interrupt input; 16-source vectored interrupt controller with IEI/IEO daisy "
          "chain; timer clock crystal on XTAL1/XTAL2; RR/TR DMA requests")
F68681 = ("two full-duplex async channels; baud-rate generator with 18 rates (50-"
          "38.4k) from a 3.6864MHz crystal; 16-bit counter/timer; 6 inputs (IP0-IP5) "
          "and 8 outputs (OP0-OP7); quad-buffered receivers; vectored IACK; open-drain "
          "IRQ and DTACK")

# (mpn, value, MHz, pins, function, technology, gpio, channels, current, symbol,
#  datasheet, description, features)
PARTS = [
    ("MC68230P8", "MC68230", 8, 48, "PI/T", "HMOS", 16, 1, "500mW max", "MC68230",
     "mc68230-parallel-interface-timer.pdf", "HMOS parallel interface/timer (PI/T)",
     F68230),
    ("MC68230P10", "MC68230", 10, 48, "PI/T", "HMOS", 16, 1, "500mW max", "MC68230",
     "mc68230-parallel-interface-timer.pdf", "HMOS parallel interface/timer (PI/T)",
     F68230),
    ("MC68901P", "MC68901", 4, 48, "MFP", None, 8, 4, "180mA max", "MC68901",
     "mc68901-multi-function-peripheral.pdf",
     "multi-function peripheral (MFP): USART, four timers, interrupt controller",
     F68901),
    ("MC68681P", "MC68681", 4, 40, "UART", None, 14, 2, "150mA max", "MC68681",
     "mc68681-mc2681-mc2682-duart.pdf",
     "dual asynchronous receiver/transmitter (DUART)", F68681),
]


def records():
    for mpn, value, clock, pins, func, tech, gpio, ch, cur, sym, ds, desc, feat in \
            PARTS:
        yield row(
            created_by=CREATED_BY, manufacturer="Motorola", mpn=mpn, value=value,
            family="68000", function=func, technology=tech, clock=clock, vmin=4.75,
            vmax=5.25, rails="+5V", package=f"PDIP-{pins}", pins=pins,
            symbol=f"{LIB}:{sym}", datasheet=f"motorola/{ds}", gpio=gpio, channels=ch,
            active_current=cur,
            description=f"Motorola {value} {desc}, {clock}MHz, PDIP-{pins}",
            keywords=[value[2:], value, func, "Motorola", "68000", "68k", "vintage"],
            features=feat)


def main():
    write(OUTPUT_FILE, "Motorola 68000 peripherals", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
