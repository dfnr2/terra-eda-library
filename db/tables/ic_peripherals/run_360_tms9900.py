#!/usr/bin/env python3
"""TI TMS9900 support chips: TMS9901, TMS9902 and TIM9904 (SN74LS362).

One classic maker (Texas Instruments), plastic DIP, 0 to 70 C, 3 MHz class. All
Obsolete; manufacturer_link NULL.

Source: 1978 TI 9900 Family Systems Design and Data Book (datasheets/ti/, each sheet
cut with the numbering-system page 8-392 and the outlines 8-393/8-394):
  - TMS9901 programmable systems interface, book 8-138, and TMS9902 asynchronous
    communications controller, book 8-160: headers print "TMS 9901 JL, NL" and
    "TMS 9902 JL, NL" (N plastic, L 0-70 C), written here without the space. NMOS,
    +5 V +/-5%, single-phase clock (phi3 from the TIM9904), ICC 150 / 100 mA max.
    The 4 MHz -40 versions are marked DESIGN GOAL and are not generated.
  - TIM9904 four-phase clock generator, book 8-249: the sheet prints only "TIM 9904
    (SN74LS362)", plastic and ceramic, 0-70 C. The 9900 numbering key does not apply
    to this bipolar SN74 part; the neighbouring TIM9905-9908 sheets order SN74LSxxx
    as "J OR N PACKAGE", so SN74LS362N (plastic) is built from that. Low-power
    Schottky, VCC 5 V and VDD 12 V; 48 MHz crystal gives 3 MHz phases.

Symbols: custom terra_symbols_ic_peripherals TMS9901, TMS9902 and TIM9904 (no stock
symbols).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _per import LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_peripherals_generated_360_tms9900.sql")
CREATED_BY = Path(__file__).name

# (mpn, value, symbol, function, technology, pins, width, rails, current, gpio,
#  channels, datasheet, description, features)
PARTS = [
    ("TMS9901NL", "TMS9901", "TMS9901", "system controller", "NMOS", 40, 0.6, "+5V",
     "150mA max", 16, 15, "tms9901-programmable-systems-interface.pdf",
     "NMOS programmable systems interface",
     "15 prioritized interrupt inputs encoded on IC0-IC3 with INTREQ; 16 I/O lines "
     "(P7-P15 shared with INT15-INT7); 14-bit interval/event timer; CRU interface "
     "(S0-S4 select); cascadable"),
    ("TMS9902NL", "TMS9902", "TMS9902", "UART", "NMOS", 18, 0.3, "+5V", "100mA max", 0,
     1, "tms9902-asynchronous-communications-controller.pdf",
     "NMOS asynchronous communications controller",
     "programmable data-rate generator; 5-8 data bits, 1/1.5/2 stop bits, parity; "
     "interval timer 64-16320us; RTS/CTS/DSR; CRU interface"),
    ("SN74LS362N", "TIM9904", "TIM9904", "clock generator", "bipolar", 20, 0.3,
     "+12V, +5V", "ICC 175mA, IDD 20mA max", 0, None,
     "tim9904-sn74ls362-four-phase-clock-generator.pdf",
     "four-phase clock generator/driver",
     "crystal, LC tank or TTL oscillator (48MHz nominal) divided by 16 into four 12V "
     "MOS phases for the TMS9900 plus four inverted TTL phases; OSCOUT; Schmitt-input "
     "D flip-flop clocked by phi3 for reset sync"),
]


def records():
    for (mpn, value, sym, func, tech, pins, width, rails, cur, gpio, ch, ds, desc,
         feat) in PARTS:
        yield row(
            created_by=CREATED_BY, manufacturer="Texas Instruments", mpn=mpn,
            value=value, family="9900", function=func, technology=tech, clock=3,
            vmin=4.75, vmax=5.25, rails=rails, package=f"PDIP-{pins}", pins=pins,
            width_in=width, symbol=f"{LIB}:{sym}", datasheet=f"ti/{ds}", gpio=gpio,
            channels=ch, active_current=cur,
            description=f"TI {value} {desc}, 3MHz, PDIP-{pins}",
            keywords=[value[-4:], value, mpn, func, "TI", "9900", "TMS9900", "vintage"],
            features=feat)


def main():
    write(OUTPUT_FILE, "TI TMS9900 support chips", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
