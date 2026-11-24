#!/usr/bin/env python3
"""6502-family peripherals: MOS 6520, 6522, 6530, 6532, 6551 and WDC W65C21/22/51N.

One classic maker (MOS Technology), every speed grade the book prints, plastic DIP
(MPS prefix), commercial temperature. All Obsolete; manufacturer_link NULL (MOS is
defunct). Plus the WDC CMOS drop-ins, Active and stocked at Mouser (checked
2026-11-20).

Source: 1982-83 MOS/Commodore Data Catalog (datasheets/mos/, each sheet cut with the
40-pin outline from book p. 5-2):
  - Ordering: the cross reference (book pp. 1-6/1-7) keys "MPS=Plastic, MCS=Ceramic,
    A=2MHz, B=3MHz" and lists MPS6520/A, MPS6522/A, MPS6530, MPS6532/A, MPS6551.
    The 6532 and 6551 sheets print their own key (MXS 65xx + A/B + C/P).
  - 6520 PIA book 2-46, 6522 VIA 2-50: 1 and 2 MHz (no B grade in the book).
  - 6530 RRIOT 2-96: 1 MHz only. Its 1Kx8 ROM, decode addresses and the PB5/PB6 chip-
    select option are mask-programmed and specified when ordering (no "-xxx" scheme
    is printed), so the row is the generic MPS6530.
  - KIM-1 6530-002 and 6530-003: the two mask-programmed 6530s that hold the KIM-1
    monitor. Source: MOS Technology KIM-1 User Manual (datasheets/mos/
    kim-1-user-manual.pdf, archive.6502.org scan), pp. 22-23 and the memory map on
    p. 38-39. The -002 has ROM at 1C00-1FFF, I/O and timer at 1740-177F, RAM at
    17C0-17FF, and its I/O runs the keypad, display, TTY and tape. The -003 has ROM at
    1800-1BFF, I/O and timer at 1700-173F, RAM at 1780-17BF, and its ports go to the
    application connector. mpn is the number the manual and the parts use, and the
    pinout and electrical data are the generic 6530's, so they share its symbol and
    data sheet.
  - 6532 RIOT 2-107: 1 and 2 MHz. The feature list claims 3 MHz but no B code is
    printed, so MPS6532B is not generated.
  - 6551 ACIA 2-129 (PRELIMINARY): MPS6551 and MPS6551A. The key allows a B (3 MHz)
    but the timing tables stop at 2 MHz, so it is not generated. The book has no
    28-pin outline; 0.6" row spacing is taken from the pin-compatible W65C51N.
  Power is printed as PD max; active_current is that figure.

WDC (datasheets/wdc/, current datasheets, whole PDFs): W65C21N6TPG-14 and
W65C21S6TPG-14 (-40 to 85 C, 4.5-5.5 V), W65C22N6TPG-14 (open-drain IRQB, 4.75-
5.25 V) and W65C22S6TPG-14 (totem-pole IRQB, 1.71-5.5 V; 14 MHz at 5 V), all -40 to
85 C; W65C51N6TPG-14 (5 V +/-5%, 0 to 70 C per Mouser). The W65C51N transmitter is
not buffered (TDRE always reads 1), unlike the MOS 6551.

Symbols: custom terra_symbols_ic_peripherals MPS6520/6522/6530/6532/6551 (MOS names)
and W65C21, W65C22N, W65C22S, W65C51N (WDC names; same pinouts).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _per import LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_peripherals_generated_300_6502.sql")
CREATED_BY = Path(__file__).name

# chip -> (pins, function, gpio, channels, PD, datasheet, description, features)
CHIPS = {
    "6520": (40, "PIA", 16, None, "500mW max", "6520-peripheral-interface-adapter.pdf",
             "peripheral interface adapter (PIA)",
             "two 8-bit bidirectional ports with data-direction registers; CA1/CA2/"
             "CB1/CB2 handshake and interrupt lines; open-drain IRQA/IRQB; Motorola "
             "MC6820/MC6821 equivalent"),
    "6522": (40, "VIA", 16, 2, "1000mW max", "6522-versatile-interface-adapter.pdf",
             "versatile interface adapter (VIA)",
             "two 8-bit ports with input latching and handshake; two 16-bit timers "
             "(T1 free-run/one-shot with PB7 output, T2 interval or PB6 pulse count); "
             "8-bit shift register on CB1/CB2; open-drain IRQ"),
    "6530": (40, "RAM-I/O-timer combo", 16, 1, "1000mW max",
             "6530-rriot-memory-io-timer-array.pdf",
             "ROM-RAM-I/O-timer (RRIOT), mask ROM",
             "1Kx8 mask-programmed ROM; 64x8 static RAM; 16 I/O lines (PB5-PB7 may be "
             "CS2/CS1/IRQ by mask option); 8-bit interval timer with /1/8/64/1024 "
             "prescale"),
    "6532": (40, "RAM-I/O-timer combo", 16, 1, "1000mW max",
             "6532-riot-memory-io-timer-array.pdf", "RAM-I/O-timer (RIOT)",
             "128x8 static RAM; two 8-bit ports; interval timer 1 to 262144 clocks; "
             "PA7 edge-detect interrupt; open-drain IRQ"),
    "6551": (28, "ACIA", 0, 1, "300mW max", "6551-acia.pdf",
             "asynchronous communications interface adapter (ACIA)",
             "on-chip baud-rate generator (15 rates, 50-19200 baud) from a 1.8432MHz "
             "crystal, or external 16x clock; 5-8 data bits; parity; RTS/CTS/DTR/DSR/"
             "DCD modem lines; open-drain IRQ"),
}

# (chip, speed suffix, MHz)
MOS_PARTS = [
    ("6520", "", 1), ("6520", "A", 2),
    ("6522", "", 1), ("6522", "A", 2),
    ("6530", "", 1),
    ("6532", "", 1), ("6532", "A", 2),
    ("6551", "", 1), ("6551", "A", 2),
]

# KIM-1 mask ROMs: (suffix, ROM, I/O+timer, RAM, role)
KIM1_6530 = [
    ("002", "1C00-1FFF", "1740-177F", "17C0-17FF",
     "KIM-1 monitor ROM with the reset/interrupt vectors; I/O drives keypad, display, "
     "TTY and cassette"),
    ("003", "1800-1BFF", "1700-173F", "1780-17BF",
     "second half of the KIM-1 monitor ROM; I/O and timer free for the "
     "application connector"),
]

# (mpn, value, chip, symbol, vmin, vmax, temp, gpio, channels, extra feature)
WDC_PARTS = [
    ("W65C21N6TPG-14", "W65C21N", "6520", "W65C21", 4.5, 5.5, (-40, 85),
     "NMOS-compatible (current-limited port outputs)"),
    ("W65C21S6TPG-14", "W65C21S", "6520", "W65C21", 4.5, 5.5, (-40, 85),
     "direct-drive port outputs, lower power"),
    ("W65C22N6TPG-14", "W65C22N", "6522", "W65C22N", 4.75, 5.25, (-40, 85),
     "NMOS-compatible, open-drain IRQB"),
    ("W65C22S6TPG-14", "W65C22S", "6522", "W65C22S", 1.71, 5.5, (-40, 85),
     "totem-pole IRQB; bus-hold on D0-D7; 14MHz at 5V, 2MHz at 1.8V"),
    ("W65C51N6TPG-14", "W65C51N", "6551", "W65C51N", 4.75, 5.25, (0, 70),
     "115.2k baud max; transmitter not buffered (TDRE always 1)"),
]
WDC_DS = {"6520": "w65c21-peripheral-interface-adapter.pdf",
          "6522": "w65c22-versatile-interface-adapter.pdf", "6551": "w65c51n-acia.pdf"}
WDC_LINK = {"6520": "w65c21", "6522": "w65c22", "6551": "w65c51n"}


def records():
    for chip, grade, clock in MOS_PARTS:
        pins, func, gpio, ch, pd, ds, desc, feat = CHIPS[chip]
        value = f"{chip}{grade}"
        yield row(
            created_by=CREATED_BY, manufacturer="MOS Technology", mpn=f"MPS{value}",
            value=value, family="6502", function=func, technology="NMOS", clock=clock,
            vmin=4.75, vmax=5.25, rails="+5V", package=f"PDIP-{pins}", pins=pins,
            symbol=f"{LIB}:MPS{chip}", datasheet=f"mos/{ds}", gpio=gpio, channels=ch,
            active_current=pd,
            description=f"MOS {value} NMOS {desc}, {clock}MHz, PDIP-{pins}",
            keywords=[chip, func, "MOS", "NMOS", "6502", "vintage"], features=feat)
    for suffix, rom, io, ram, role in KIM1_6530:
        pins, func, gpio, ch, pd, ds, desc, feat = CHIPS["6530"]
        value = f"6530-{suffix}"
        yield row(
            created_by=CREATED_BY, manufacturer="MOS Technology", mpn=value,
            value=value, family="6502", function=func, technology="NMOS", clock=1,
            vmin=4.75, vmax=5.25, rails="+5V", package=f"PDIP-{pins}", pins=pins,
            symbol=f"{LIB}:MPS6530", datasheet=f"mos/{ds}", gpio=gpio, channels=ch,
            active_current=pd,
            description=(f"MOS 6530-{suffix} KIM-1 ROM-RAM-I/O-timer (RRIOT), mask ROM "
                         f"at {rom}, I/O+timer at {io}, RAM at {ram}, 1MHz, "
                         f"PDIP-{pins}"),
            keywords=["6530", value, "RRIOT", "KIM-1", "MOS", "NMOS", "6502", "vintage"],
            features=f"{role}; {feat}")
    for mpn, value, chip, sym, vmin, vmax, temp, extra in WDC_PARTS:
        pins, func, gpio, ch, _, _, desc, feat = CHIPS[chip]
        yield row(
            created_by=CREATED_BY, manufacturer="WDC", mpn=mpn, value=value,
            family="6502", function=func, technology="CMOS", clock=14, vmin=vmin,
            vmax=vmax, rails="+5V" if vmin > 4 else "+1.8V to +5V",
            package=f"PDIP-{pins}", pins=pins, symbol=f"{LIB}:{sym}",
            datasheet=f"wdc/{WDC_DS[chip]}", gpio=gpio, channels=ch, temp=temp,
            lifecycle="Active", rohs="Yes",
            mfr_link=f"https://www.westerndesigncenter.com/wdc/{WDC_LINK[chip]}-chip.php",
            description=f"WDC {value} static CMOS {desc}, 14MHz, PDIP-{pins}",
            keywords=[chip, value, f"65C{chip[2:]}", func, "WDC", "CMOS", "6502"],
            # drop the MOS IRQ wording: WDC's IRQ type varies by variant (see extra)
            features=f"{extra}; " + feat.split("; open-drain")[0])


def main():
    write(OUTPUT_FILE, "MOS/WDC 6502 peripherals", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
