#!/usr/bin/env python3
"""Intel peripherals and system-support chips for the 8080/8085 and 8086/8088.

8080/8085: 8212, 8216, 8226, 8224, 8228, 8238, 8251A, 8253, 8255A, 8257, 8259A, 8279.
8086/8088: 8284A clock generator, 8288 bus controller.
One classic maker (Intel), every grade, plastic DIP, commercial temperature. All
Obsolete. The CMOS Renesas/Intersil CP82C55A and CP82C59A are End of Life at Mouser
(2026-11-20), so no Active rows.

Source: 1981 Intel Component Data Catalog (datasheets/intel/, each sheet cut with
its DIP outlines, book pp. 12-3..12-9, and the ordering page 12-12):
  - Ordering codes: no sheet prints one. Page 12-12 gives the rule (P = plastic;
    B/C/D hermetic; no M/I prefix = commercial; example "P8085A-2"), so the plastic
    codes below are built from it, as for the phase-3 CPUs.
  - 8212 book 6-58, 8216/8226 6-66 (also sold as 3216/3226), 8224 6-82, 8228/8238
    6-87 (also 3228/3238): bipolar. The sheets don't say so; their characteristics
    are TTL (input clamps, 3.65V VOH) and Intel's other literature calls them
    Schottky bipolar.
  - 8251A book 8-43 (headed "8251A/S2657"; no plain 8251 commercial sheet); 8253/8253-5
    8-59 (count rate to 2 MHz; DC and AC headers disagree on +/-5% vs +/-10%, so
    +/-5% is used); 8255A/8255A-5 8-85; 8257/8257-5 6-106; 8259A/-2/-8 6-123
    (PRELIMINARY; static, no clock); 8279/8279-5 8-264. Only the 8251A, 8253 and
    8259A sheets print "NMOS"; NMOS is assumed for the 8255A, 8257 and 8279.
  - 8284A book 7-90 (PRELIMINARY; bipolar per the I8284/M8284 sheets; 12-30 MHz
    crystal at 3x the CPU clock, so CLK to 10 MHz; no 8284A-1 in this book);
    8288 7-103 ("20-pin bipolar component"; CLK to 10 MHz).
  The -5 grades are "MCS-85 compatible" (faster bus timing for the 8085A); the
  8259A-2 is the fast and the 8259A-8 the slow grade. Static parts have no
  max_clock.

Symbols: stock KiCad Timer:8253, Interface:8255A, Interface:8259A, Timer:8284 (the
8284A pinout) and Interface:8288, checked pin for pin. Custom
terra_symbols_ic_peripherals 8212, 8216 (shared by the 8226), 8224, 8228 (shared by
the 8238), 8251A, 8257 and 8279.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _per import LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_peripherals_generated_340_intel.sql")
CREATED_BY = Path(__file__).name

# (value, family, function, technology, MHz, vmin, vmax, rails, ICC, pins, width,
#  gpio, channels, symbol, datasheet, description, features)
PARTS = [
    ("8212", "8080", "I/O port", "bipolar", None, 4.75, 5.25, "+5V", "130mA max", 24,
     0.6, 8, None, f"{LIB}:8212", "8212-8-bit-io-port.pdf", "8-bit input/output port",
     "8-bit latch with 3-state outputs; input or output mode (MD); service-request "
     "flip-flop with INT output; asynchronous clear; 15mA outputs, 3.65V VOH"),
    ("8216", "8080", "bus driver", "bipolar", None, 4.75, 5.25, "+5V", "130mA max", 16,
     0.3, 0, None, f"{LIB}:8216", "8216-8226-bus-driver.pdf",
     "4-bit bidirectional bus driver, non-inverting",
     "3-state; DIEN direction control; DB side sinks 55mA; DO side 3.65V VOH for MOS"),
    ("8226", "8080", "bus driver", "bipolar", None, 4.75, 5.25, "+5V", "120mA max", 16,
     0.3, 0, None, f"{LIB}:8216", "8216-8226-bus-driver.pdf",
     "4-bit bidirectional bus driver, inverting",
     "3-state; DIEN direction control; DB side sinks 50mA; DO side 3.65V VOH for MOS"),
    ("8224", "8080", "clock generator", "bipolar", None, 4.75, 5.25, "+12V, +5V",
     "ICC 115mA, IDD 12mA max", 16, 0.3, 0, None, f"{LIB}:8224",
     "8224-clock-generator.pdf", "clock generator and driver for the 8080A",
     "crystal (series, fundamental; TANK for overtone) divided by 9 into 12V "
     "phi1/phi2; phi2 TTL and OSC outputs; RESIN Schmitt reset; READY sync; STSTB for "
     "the 8228; 18.432MHz crystal gives 2.048MHz"),
    ("8228", "8080", "system controller", "bipolar", None, 4.75, 5.25, "+5V",
     "190mA max", 28, 0.6, 0, None, f"{LIB}:8228", "8228-8238-system-controller.pdf",
     "system controller and bus driver for the 8080A",
     "bidirectional data-bus driver; decodes latched status into MEMR/MEMW/I/OR/I/OW/"
     "INTA; single-level RST 7 vector; BUSEN 3-states the system side"),
    ("8238", "8080", "system controller", "bipolar", None, 4.75, 5.25, "+5V",
     "190mA max", 28, 0.6, 0, None, f"{LIB}:8228", "8228-8238-system-controller.pdf",
     "system controller and bus driver for the 8080A, advanced IOW/MEMW",
     "as the 8228 with advanced IOW/MEMW for large-system timing"),
    ("8251A", "8080", "USART", "NMOS", 3.125, 4.75, 5.25, "+5V", "100mA max", 28, 0.6,
     0, 1, f"{LIB}:8251A", "8251a-usart.pdf",
     "programmable communication interface (USART)",
     "sync (internal or external sync, auto sync insertion) and async to 19.2k baud; "
     "5-8 bits; parity, overrun and framing detection; break; external TxC/RxC (no "
     "baud generator); modem lines DTR/RTS/DSR/CTS"),
    ("8253", "8080", "timer", "NMOS", 2, 4.75, 5.25, "+5V", "140mA max", 24, 0.6, 0, 3,
     "Timer:8253", "8253-8253-5-interval-timer.pdf", "programmable interval timer",
     "three 16-bit counters to 2MHz with CLK, GATE and OUT each; binary or BCD; six "
     "modes; count latch"),
    ("8253-5", "8080", "timer", "NMOS", 2, 4.75, 5.25, "+5V", "140mA max", 24, 0.6, 0,
     3, "Timer:8253", "8253-8253-5-interval-timer.pdf",
     "programmable interval timer, MCS-85 bus timing",
     "three 16-bit counters to 2MHz with CLK, GATE and OUT each; binary or BCD; six "
     "modes; count latch"),
    ("8255A", "8080", "PPI", "NMOS", None, 4.75, 5.25, "+5V", "120mA max", 40, 0.6, 24,
     None, "Interface:8255A", "8255a-ppi.pdf", "programmable peripheral interface (PPI)",
     "three 8-bit ports; mode 0 basic I/O, mode 1 strobed, mode 2 bidirectional (port "
     "A); port C bit set/reset; Darlington drive on ports B and C"),
    ("8255A-5", "8080", "PPI", "NMOS", None, 4.75, 5.25, "+5V", "120mA max", 40, 0.6,
     24, None, "Interface:8255A", "8255a-ppi.pdf",
     "programmable peripheral interface (PPI), MCS-85 bus timing",
     "three 8-bit ports; mode 0 basic I/O, mode 1 strobed, mode 2 bidirectional (port "
     "A); port C bit set/reset; Darlington drive on ports B and C"),
    ("8257", "8080", "DMA", "NMOS", 3.125, 4.75, 5.25, "+5V", "120mA max", 40, 0.6, 0,
     4, f"{LIB}:8257", "8257-dma-controller.pdf", "programmable DMA controller",
     "four channels with fixed or rotating priority; TC and modulo-128 MARK outputs; "
     "auto-load; 16-bit address with the upper byte latched via ADSTB"),
    ("8257-5", "8080", "DMA", "NMOS", 3.125, 4.5, 5.5, "+5V", "120mA max", 40, 0.6, 0,
     4, f"{LIB}:8257", "8257-dma-controller.pdf",
     "programmable DMA controller, MCS-85 bus timing",
     "four channels with fixed or rotating priority; TC and modulo-128 MARK outputs; "
     "auto-load; 16-bit address with the upper byte latched via ADSTB"),
    ("8259A", "8080", "interrupt controller", "NMOS", None, 4.5, 5.5, "+5V",
     "85mA max", 28, 0.6, 0, 8, "Interface:8259A", "8259a-interrupt-controller.pdf",
     "programmable interrupt controller",
     "eight inputs, cascadable to 64 via CAS0-CAS2; fully nested, rotating and "
     "special-mask modes; edge or level triggered; poll; 8080/8085 and 8086/8088 "
     "modes; static"),
    ("8259A-2", "8080", "interrupt controller", "NMOS", None, 4.5, 5.5, "+5V",
     "85mA max", 28, 0.6, 0, 8, "Interface:8259A", "8259a-interrupt-controller.pdf",
     "programmable interrupt controller, fast grade",
     "eight inputs, cascadable to 64 via CAS0-CAS2; fully nested, rotating and "
     "special-mask modes; edge or level triggered; poll; 8080/8085 and 8086/8088 "
     "modes; static"),
    ("8259A-8", "8080", "interrupt controller", "NMOS", None, 4.75, 5.25, "+5V",
     "85mA max", 28, 0.6, 0, 8, "Interface:8259A", "8259a-interrupt-controller.pdf",
     "programmable interrupt controller, slow grade",
     "eight inputs, cascadable to 64 via CAS0-CAS2; fully nested, rotating and "
     "special-mask modes; edge or level triggered; poll; 8080/8085 and 8086/8088 "
     "modes; static"),
    ("8279", "8080", "keyboard/display controller", "NMOS", 2, 4.75, 5.25, "+5V",
     "120mA max", 40, 0.6, 0, None, f"{LIB}:8279",
     "8279-keyboard-display-controller.pdf",
     "programmable keyboard/display interface",
     "scanned keyboard, sensor matrix or strobed input; 8-character FIFO; 2-key "
     "lockout or N-key rollover; 16x8 display RAM; IRQ on key entry"),
    ("8279-5", "8080", "keyboard/display controller", "NMOS", 3.125, 4.5, 5.5, "+5V",
     "120mA max", 40, 0.6, 0, None, f"{LIB}:8279",
     "8279-keyboard-display-controller.pdf",
     "programmable keyboard/display interface, MCS-85 bus timing",
     "scanned keyboard, sensor matrix or strobed input; 8-character FIFO; 2-key "
     "lockout or N-key rollover; 16x8 display RAM; IRQ on key entry"),
    ("8284A", "8086", "clock generator", "bipolar", 10, 4.5, 5.5, "+5V", "162mA max",
     18, 0.3, 0, None, "Timer:8284", "8284a-clock-generator.pdf",
     "clock generator and driver for the 8086/8088",
     "12-30MHz crystal or EFI input divided by 3 (33% duty CLK); PCLK and OSC "
     "outputs; Schmitt RES to synchronized RESET; two RDY/AEN pairs with ASYNC "
     "select; CSYNC"),
    ("8288", "8086", "bus controller", "bipolar", 10, 4.5, 5.5, "+5V", "230mA max", 20,
     0.3, 0, None, "Interface:8288", "8288-bus-controller.pdf",
     "bus controller for the 8086/8088 in maximum mode",
     "decodes S0-S2 into 3-state memory, I/O and INTA commands (32mA); advanced write "
     "commands; ALE, DEN, DT/R; IOB I/O-bus mode; CEN; Multibus compatible"),
]


def records():
    for (value, family, func, tech, clock, vmin, vmax, rails, icc, pins, width, gpio,
         ch, sym, ds, desc, feat) in PARTS:
        chip = value.split("-")[0]
        speed = f", {clock:g}MHz" if clock else ""
        yield row(
            created_by=CREATED_BY, manufacturer="Intel", mpn=f"P{value}", value=value,
            family=family, function=func, technology=tech, clock=clock, vmin=vmin,
            vmax=vmax, rails=rails, package=f"PDIP-{pins}", pins=pins, width_in=width,
            symbol=sym, datasheet=f"intel/{ds}", gpio=gpio, channels=ch,
            active_current=icc,
            description=f"Intel {value} {desc}{speed}, PDIP-{pins}",
            keywords=[chip, func, "Intel", tech, family]
            + (["8085", "MCS-80"] if family == "8080" else ["8088", "iAPX"])
            + ["vintage"], features=feat)


def main():
    write(OUTPUT_FILE, "Intel 8080/8086 peripherals", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
