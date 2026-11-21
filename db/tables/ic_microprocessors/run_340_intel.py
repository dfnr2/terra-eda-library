#!/usr/bin/env python3
"""Intel CPUs: 8080A, 8085A, 8086 and 8088.

One classic maker (Intel), every speed grade, plastic DIP, commercial temperature.
All Obsolete.

Source: 1981 Intel Component Data Catalog (datasheets/intel/, each cut to the data
sheet plus the 40-lead plastic and CERDIP outlines, book pp. 12-4/12-7):
  - 8080A/8080A-1/8080A-2, book 6-1..6-9. Clock is 1/tCY min: 0.48 us (2.08 MHz),
    0.32 us (3.125 MHz) and 0.38 us (2.63 MHz).
  - 8085A/8085A-2, book 6-10..6-25 (3 and 5 MHz). The HMOS 8085AH is a separate
    sheet and not generated.
  - 8086/8086-2/8086-1 (iAPX 86/10), book 7-1..7-24 (5, 8, 10 MHz).
  - 8088 (iAPX 88/10), book 7-25 on, marked PRELIMINARY; 5 MHz only (no 8088-2 in
    this book).

Ordering codes: no sheet has its own table. The catalog's ordering page (12-12)
gives the rule (P = plastic, D/C/B = hermetic types, no M/I prefix = commercial)
and prints "P8085A-2" as an example, so the plastic codes are built from that rule:
P8080A, P8080A-1, P8080A-2, P8085A, P8085A-2, P8086, P8086-2, P8086-1, P8088.

Symbols: stock KiCad MCU_Intel:8080A (checked pin for pin). Custom
terra_symbols_ic_microprocessors 8085A (no stock symbol), and 8086/8088 with both
the minimum- and maximum-mode names on pins 24-31 and 34; the stock 8088 symbols
drop the bar on ~{DEN}.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _cpu import EXT_1PH, EXT_2PH, LIB, ON_CHIP, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_microprocessors_generated_340_intel.sql")
CREATED_BY = Path(__file__).name

F8080 = ("external non-overlapping 12V phi1/phi2 clock (8224); SYNC status strobe "
         "(8228/8238 system controller); INT/INTE; HOLD/HLDA; READY/WAIT")
F8085 = ("on-chip clock (crystal, LC or RC on X1/X2), CLK OUT; multiplexed AD0-AD7 "
         "with ALE; 5 interrupts (TRAP, RST 7.5/6.5/5.5, INTR); serial SID/SOD; "
         "HOLD/HLDA")
F8086 = ("multiplexed address/data with ALE; MN/~MX selects minimum mode or maximum "
         "mode (8288 bus controller); NMI and INTR; external clock from the 8284A; "
         "6-byte prefetch queue")

# (mpn, value, chip, MHz, vmin, vmax, ICC)
PARTS = [
    ("P8080A", "8080A", "8080A", 2.08, 4.75, 5.25, "IDD 70mA, ICC 80mA, IBB 1mA max"),
    ("P8080A-1", "8080A-1", "8080A", 3.125, 4.75, 5.25, "IDD 70mA, ICC 80mA, IBB 1mA max"),
    ("P8080A-2", "8080A-2", "8080A", 2.63, 4.75, 5.25, "IDD 70mA, ICC 80mA, IBB 1mA max"),
    ("P8085A", "8085A", "8085A", 3, 4.75, 5.25, "170mA max"),
    ("P8085A-2", "8085A-2", "8085A", 5, 4.75, 5.25, "170mA max"),
    ("P8086", "8086", "8086", 5, 4.5, 5.5, "340mA max"),
    ("P8086-2", "8086-2", "8086", 8, 4.75, 5.25, "350mA max"),
    ("P8086-1", "8086-1", "8086", 10, 4.75, 5.25, "360mA max"),
    ("P8088", "8088", "8088", 5, 4.5, 5.5, "340mA max"),
]

# chip -> (family, technology, arch, data, addr, clock source, rails, symbol,
#          datasheet, description, features)
CHIPS = {
    "8080A": ("8080", "NMOS", 8, 8, 16, EXT_2PH, "+12V, +5V, -5V", "MCU_Intel:8080A",
              "8080a-8-bit-microprocessor.pdf", "NMOS 8-bit CPU, +12V/+5V/-5V", F8080),
    "8085A": ("8085", "NMOS", 8, 8, 16, ON_CHIP, "+5V", f"{LIB}:8085A",
              "8085a-8-bit-microprocessor.pdf",
              "NMOS 8-bit CPU, on-chip clock, single +5V", F8085),
    "8086": ("8086", "HMOS", 16, 16, 20, EXT_1PH, "+5V", f"{LIB}:8086",
             "8086-16-bit-microprocessor.pdf",
             "HMOS 16-bit CPU, 16-bit bus, 1M address", F8086),
    "8088": ("8086", "HMOS", 16, 8, 20, EXT_1PH, "+5V", f"{LIB}:8088",
             "8088-8-bit-bus-microprocessor.pdf",
             "HMOS 16-bit CPU, 8-bit bus, 1M address", F8086),
}


def records():
    for mpn, value, chip, clock, vmin, vmax, icc in PARTS:
        family, tech, arch, data, addr, clk, rails, sym, ds, desc, feat = CHIPS[chip]
        yield row(
            created_by=CREATED_BY, manufacturer="Intel", mpn=mpn, value=value,
            family=family, core=f"{tech} {chip}", technology=tech, arch_bits=arch,
            data_bits=data, addr_bits=addr, clock=clock, clock_source=clk, vmin=vmin,
            vmax=vmax, rails=rails, active_current=icc, package="PDIP-40", pins=40,
            symbol=sym, datasheet=f"intel/{ds}",
            description=f"Intel {value} {desc}, {clock:g}MHz, PDIP-40",
            keywords=[chip, family, "Intel", tech, f"{arch}-bit", "vintage"]
            + (["x86", "iAPX"] if family == "8086" else []),
            features=feat)


def main():
    write(OUTPUT_FILE, "Intel 8080A/8085A/8086/8088", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
