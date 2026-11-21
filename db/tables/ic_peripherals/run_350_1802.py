#!/usr/bin/env python3
"""RCA CDP1800-family peripherals: CDP1852, CDP1853, CDP1854A and CDP1861C.

One classic maker (RCA), each type in plastic DIP (E suffix). All Obsolete;
manufacturer_link NULL (no successor product pages for these, unlike the CDP1802A).

Source: 1982 RCA CMOS LSI Products data book (datasheets/rca/, each sheet cut with
the E/D outlines, book pp. 551-554). The book prints only a suffix key (book p. 6:
D ceramic, E plastic), so CDP1852E/CE and CDP1853E/CE are built from it;
CDP1854AE/ACE are printed in the CDP1854 photo caption and CDP1861CE in its
static-characteristics header. RCA offers no 0-70 C grade: plastic parts are rated
-40 to 85 C, as the CDP1802 rows.
  - CDP1852/CDP1852C byte I/O port, book 203: 4-10.5 V / 4-6.5 V; strobed by TPB.
  - CDP1853/CDP1853C 1-of-8 decoder, book 210: 4-10.5 V / 4-6.5 V; clocked by
    TPA/TPB.
  - CDP1854A/CDP1854AC UART, book 214: 4-10.5 V / 4-6.5 V; 200 kbit/s at 5 V
    (400 kbit/s at 10 V, A only); 3 mA max at 5 V.
  - CDP1861C video display controller ("Pixie"), book 258, Preliminary Data: 4-6.5 V,
    clock DC-2.5 MHz at 5 V (1.76064 MHz typical). No plain CDP1861 in this book.
  The sheets give quiescent and in-system IDD of a few hundred uA rather than an
  active-current maximum, so active_current is NULL except for the UART.

Symbols: custom terra_symbols_ic_peripherals CDP1852, CDP1853, CDP1854 (mode-1
CDP1800-bus names) and CDP1861; the A/C variants share their type's pinout.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _per import LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_peripherals_generated_350_1802.sql")
CREATED_BY = Path(__file__).name

F1852 = ("8-bit latch with 3-state outputs; programmed as input or output port "
         "(MODE); service-request output; asynchronous clear; also an address latch")
F1853 = ("decodes the 1802 N0-N2 lines into eight active-high outputs; CE for "
         "multi-level decoding; clocked by TPA/TPB")
F1854 = ("CDP1800 bus interface (mode 1) or TR1602A-compatible (mode 0); 5-8 data "
         "bits, 1/1.5/2 stop bits, parity; 16x T/R clocks (no baud generator); "
         "RTS/CTS, PSI and ES; interrupt output")
F1861 = ("64x128 bit-mapped display via 1802 DMA (1KB); composite sync and video "
         "outputs; interrupt once per field; open-drain DMAO and INT; Schmitt RESET; "
         "CLEAR output")

# (mpn, value, symbol, function, pins, width, vmax, MHz, gpio, channels, current,
#  datasheet, description, features)
PARTS = [
    ("CDP1852E", "CDP1852", "CDP1852", "I/O port", 24, 0.6, 10.5, None, 8, None, None,
     "cdp1852-cdp1852c-byte-io-port.pdf", "byte-wide I/O port, 4-10.5V", F1852),
    ("CDP1852CE", "CDP1852C", "CDP1852", "I/O port", 24, 0.6, 6.5, None, 8, None, None,
     "cdp1852-cdp1852c-byte-io-port.pdf", "byte-wide I/O port, 4-6.5V", F1852),
    ("CDP1853E", "CDP1853", "CDP1853", "I/O decoder", 16, 0.3, 10.5, None, 0, None,
     None, "cdp1853-cdp1853c-1-of-8-decoder.pdf", "N-bit 1-of-8 decoder, 4-10.5V",
     F1853),
    ("CDP1853CE", "CDP1853C", "CDP1853", "I/O decoder", 16, 0.3, 6.5, None, 0, None,
     None, "cdp1853-cdp1853c-1-of-8-decoder.pdf", "N-bit 1-of-8 decoder, 4-6.5V",
     F1853),
    ("CDP1854AE", "CDP1854A", "CDP1854", "UART", 40, 0.6, 10.5, None, 0, 1,
     "3mA max at 5V", "cdp1854a-cdp1854ac-uart.pdf", "UART, 4-10.5V", F1854),
    ("CDP1854ACE", "CDP1854AC", "CDP1854", "UART", 40, 0.6, 6.5, None, 0, 1,
     "3mA max at 5V", "cdp1854a-cdp1854ac-uart.pdf", "UART, 4-6.5V", F1854),
    ("CDP1861CE", "CDP1861C", "CDP1861", "video display controller", 24, 0.6, 6.5, 2.5,
     0, None, None, "cdp1861c-video-display-controller.pdf",
     "video display controller (Pixie), 4-6.5V", F1861),
]


def records():
    for (mpn, value, sym, func, pins, width, vmax, clock, gpio, ch, cur, ds, desc,
         feat) in PARTS:
        yield row(
            created_by=CREATED_BY, manufacturer="RCA", mpn=mpn, value=value,
            family="1802", function=func, technology="CMOS", clock=clock, vmin=4.0,
            vmax=vmax, rails="+5V" if vmax < 7 else "+5V to +10V",
            package=f"PDIP-{pins}", pins=pins, width_in=width, symbol=f"{LIB}:{sym}",
            datasheet=f"rca/{ds}", gpio=gpio, channels=ch, active_current=cur,
            temp=(-40, 85), description=f"RCA {value} CMOS {desc}, PDIP-{pins}",
            keywords=[value[3:7], value[:7], func, "RCA", "COSMAC", "CMOS", "1802",
                      "vintage"], features=feat)


def main():
    write(OUTPUT_FILE, "RCA CDP1800 peripherals", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
