#!/usr/bin/env python3
"""6502-family CPUs: MOS 6502-6507 (NMOS), GTE G65SC802 and WDC W65C02S/W65C816S (CMOS).

One classic maker per chip (plans/vintage-computer-parts.md, "Manufacturer coverage"),
every speed grade, plastic DIP, commercial temperature, plus the WDC parts that are
still made.

Sources (cut to the CPU pages plus the DIP outlines, in datasheets/<mfr>/):
  - MOS: 1982 MOS Technology Data Catalog (Commodore Semiconductor Group), "6500
    Microprocessors", book pp. 2-14..2-24 (PDF 25-35), outlines 5-2, clock app brief
    16. One sheet for 6502-6507 (and 6512-6515, not generated). Ordering key on
    p. 2-14: "MXS 65XX_" with the middle letter the package (C ceramic, P plastic)
    and the suffix the speed (none 1 MHz, A 2 MHz, B 3 MHz); the book prints no
    individual codes, and says every chip comes in all three speeds, so the plastic
    MPS codes are built from the key. The book has no 28-pin outline; the 28-pin
    parts are taken as 0.6" like the other 28-pin NMOS DIPs.
  - GTE: 1987 GTE Microcircuits Data Book, "CMOS 8/16-Bit Microprocessor Family"
    (G65SC802/G65SC816), book pp. 1-83..1-103 (ADVANCE INFORMATION), outlines
    6-3/6-4. Ordering key on p. 1-103: G + 65SC802 + package (P plastic) + temperature
    (none = 0 to 70 C) + -2/-4/-6/-8 MHz; codes built from it. The G65SC802 is the
    65816 core in the NMOS 6502 pinout, so it shares the MPS6502 symbol (GTE calls
    VCC "VDD" and phi0(IN) "phi2(IN)"). The G65SC816 is not generated: the WDC
    W65C816S is the same chip and still made.
  - WDC: current data sheets W65C02S (2022-04-08) and W65C816S (2024-03-13), whole.
    Section 10 gives only a key and a PLCC example; the PDIP codes are the ones
    Mouser stocks (W65C02S6TPG-14, W65C816S6PG-14; checked 2026-11-20, Active). The
    W65C02S key gives 0 to 70 C for DIP; the W65C816S sheet gives -40 to 85 C only.

Symbols are custom (terra_symbols_ic_microprocessors, pin tables in _pinouts.py):
one per 6503-6507 pinout, MPS6502 for the 6502 and G65SC802, and one each for the
W65C02S and W65C816S, whose pins 1, 3, 5, 7, 35-39 differ from the NMOS 6502.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _cpu import EXT_1PH, LIB, ON_CHIP, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_microprocessors_generated_300_6502.sql")
CREATED_BY = Path(__file__).name
MOS_DS = "mos/6502-6507-8-bit-microprocessor.pdf"

# chip -> (pins, address bits, signals kept beyond RES/IRQ basics, one-line note)
MOS = {
    "6502": (40, 16, "IRQ, NMI, RDY, SYNC, S.O., two-phase clock out",
             "64K address"),
    "6503": (28, 12, "IRQ, NMI", "4K address (A0-A11)"),
    "6504": (28, 13, "IRQ", "8K address (A0-A12)"),
    "6505": (28, 12, "IRQ, RDY", "4K address (A0-A11)"),
    "6506": (28, 12, "IRQ, phi1 and phi2 clock out", "4K address (A0-A11)"),
    "6507": (28, 13, "RDY, no interrupts (Atari 2600 CPU)", "8K address (A0-A12)"),
}
MOS_SPEEDS = {"": 1, "A": 2, "B": 3}


def mos_rows():
    for chip, (pins, addr, signals, note) in MOS.items():
        for suffix, clock in MOS_SPEEDS.items():
            value = f"{chip}{suffix}"
            yield row(
                created_by=CREATED_BY, manufacturer="MOS Technology", mpn=f"MPS{value}",
                value=value, family="6502", core="NMOS 6502", technology="NMOS",
                arch_bits=8, data_bits=8, addr_bits=addr, clock=clock,
                clock_source=ON_CHIP, vmin=4.75, vmax=5.25, rails="+5V",
                active_current="160mA max", package=f"PDIP-{pins}", pins=pins,
                symbol=f"{LIB}:MPS{chip}", datasheet=MOS_DS,
                description=(f"MOS {value} NMOS 8-bit CPU, {note}, {clock}MHz, "
                             f"on-chip clock (crystal, RC or TTL in), PDIP-{pins}"),
                keywords=["6502", "65xx", "MOS", "MCS6500", "NMOS", "8-bit", "vintage"],
                features=f"{signals}; on-chip clock generator; 56 instructions, "
                         "13 addressing modes; M6800 bus compatible")


def gte_rows():
    for clock in (2, 4, 6, 8):
        mpn = f"G65SC802P-{clock}"
        yield row(
            created_by=CREATED_BY, manufacturer="GTE", mpn=mpn, value="65SC802",
            family="6502", core="CMOS 65816 (6502 pinout)", technology="CMOS",
            arch_bits=16, data_bits=8, addr_bits=16, clock=clock, clock_source=ON_CHIP,
            vmin=4.75, vmax=5.25, rails="+5V", active_current=f"{clock * 5}mA max",
            package="PDIP-40", pins=40, symbol=f"{LIB}:MPS6502",
            datasheet="gte/g65sc802-g65sc816-16-bit-microprocessor.pdf",
            description=(f"GTE G65SC802 CMOS 8/16-bit CPU (65802), 6502 pin compatible, "
                         f"64K address, {clock}MHz, PDIP-40"),
            keywords=["65802", "65SC802", "65816", "6502", "GTE", "CMOS", "16-bit",
                      "vintage"],
            features="65816 core in the 40-pin 6502 pinout: 16-bit registers with 6502 "
                     "emulation mode, WAI/STP, block move; on-chip or external clock; "
                     "static (clock can stop)")


def wdc_rows():
    common = dict(created_by=CREATED_BY, manufacturer="WDC", family="6502",
                  technology="CMOS", data_bits=8, clock=14, clock_source=EXT_1PH,
                  vmin=1.71, vmax=5.25, rails="+5V", package="PDIP-40", pins=40,
                  lifecycle="Active", rohs="Yes")
    yield row(
        **common, mpn="W65C02S6TPG-14", value="W65C02S", core="CMOS 65C02",
        arch_bits=8, addr_bits=16, active_current="1.5mA/MHz max @ 5V",
        symbol=f"{LIB}:W65C02S", datasheet="wdc/w65c02s-8-bit-microprocessor.pdf",
        mfr_link="https://www.westerndesigncenter.com/wdc/w65c02s-chip.php",
        description=("WDC W65C02S static CMOS 8-bit CPU (65C02), 64K address, 14MHz at "
                     "5V, 1.8-5V, PDIP-40"),
        keywords=["65C02", "W65C02S", "6502", "WDC", "CMOS", "8-bit"],
        features="fully static (clock can stop); BE bus enable, RDY with WAI, STP; "
                 "VPB vector pull, MLB memory lock; PHI1O/PHI2O clock outputs; "
                 "14MHz @ 5V, 8MHz @ 3.3V, 2MHz @ 1.8V")
    yield row(
        **common, mpn="W65C816S6PG-14", value="W65C816S", core="CMOS 65816",
        arch_bits=16, addr_bits=24, active_current="2.0mA/MHz max @ 5V",
        symbol=f"{LIB}:W65C816S", datasheet="wdc/w65c816s-16-bit-microprocessor.pdf",
        mfr_link="https://www.westerndesigncenter.com/wdc/w65c816s-chip.php",
        temp=(-40, 85),
        description=("WDC W65C816S static CMOS 8/16-bit CPU (65816), 16M address with "
                     "bank on D0-D7, 14MHz at 5V, 1.8-5V, PDIP-40"),
        keywords=["65816", "65C816", "W65C816S", "WDC", "CMOS", "16-bit"],
        features="6502 emulation mode; 24-bit address (bank address multiplexed on "
                 "D0-D7, latch on PHI2 low); ABORTB, VDA/VPA, E and MX status; fully "
                 "static; 14MHz @ 5V")


def main():
    write(OUTPUT_FILE, "6502 family (MOS, GTE, WDC)", CREATED_BY,
          [*mos_rows(), *gte_rows(), *wdc_rows()])


if __name__ == "__main__":
    main()
