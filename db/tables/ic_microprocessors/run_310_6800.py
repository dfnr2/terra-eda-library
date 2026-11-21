#!/usr/bin/env python3
"""Motorola 6800-family CPUs: MC6800, MC6802 (and NS), MC6808, MC6809, MC6809E.

One classic maker (Motorola), every speed grade (1.0, 1.5 and 2.0 MHz: MC68xx,
MC68Axx, MC68Bxx), plastic DIP (P suffix), commercial temperature (no C suffix).
All Obsolete. NXP has no product pages for these, so manufacturer_link is NULL.

Source: 1983 Motorola 8-Bit Microprocessor and Peripheral Data ("M6800"), each
chip's ordering-information table, cut to the data sheet plus the 40-pin outlines
(CASE 711 plastic, 715 ceramic, 734 CERDIP; book pp. 4-10/4-11) in
datasheets/motorola/:
  - MC6800 pp. 3-149..3-178
  - MC6802/MC6802NS/MC6808 pp. 3-179..3-199 (one sheet; plastic and ceramic only,
    no MC68A02NS/MC68B02NS)
  - MC6809 pp. 3-233..3-265
  - MC6809E pp. 3-266..3-299

Symbols: stock KiCad CPU_NXP_6800, one per grade, all checked pin for pin against
the data sheets. The MC6808 and MC6802NS share the MC6802 pinout (pin 36 RE tied
low on the 6808; pin 35 VCC standby tied to 5V on the NS), so they use the MC6802
symbol of their speed grade.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _cpu import EXT_2PH, ON_CHIP, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_microprocessors_generated_310_6800.sql")
CREATED_BY = Path(__file__).name
STOCK = "CPU_NXP_6800"
GRADES = {"": 1, "A": 1.5, "B": 2}  # MC68xx / MC68Axx / MC68Bxx

# chip -> (symbol stem, technology, clock source, datasheet, description, features)
CHIPS = {
    "00": ("00", "NMOS", EXT_2PH, "mc6800-8-bit-microprocessor.pdf",
           "NMOS 8-bit CPU, external two-phase clock",
           "external non-overlapping phi1/phi2 clock (MC6875); TSC three-state control "
           "and DBE for DMA; HALT, IRQ, NMI; dynamic (clock must run)"),
    "02": ("02", "NMOS", ON_CHIP, "mc6802-mc6808-microprocessor-with-clock-and-ram.pdf",
           "NMOS 8-bit CPU with clock and 128 bytes RAM",
           "on-chip oscillator (crystal at 4x E); 128 bytes RAM at $0000, first 32 "
           "bytes kept on VCC standby (pin 35); RE RAM enable, MR memory ready"),
    "02NS": ("02", "NMOS", ON_CHIP, "mc6802-mc6808-microprocessor-with-clock-and-ram.pdf",
             "NMOS 8-bit CPU with clock and 128 bytes RAM, no standby",
             "on-chip oscillator (crystal at 4x E); 128 bytes RAM at $0000, no "
             "standby (pin 35 tied to 5V); MR memory ready"),
    "08": ("02", "NMOS", ON_CHIP, "mc6802-mc6808-microprocessor-with-clock-and-ram.pdf",
           "NMOS 8-bit CPU with clock, no RAM",
           "MC6802 without the RAM (pin 36 RE tied to ground); on-chip oscillator "
           "(crystal at 4x E); MR memory ready"),
    "09": ("09", "HMOS", ON_CHIP, "mc6809-8-bit-microprocessor.pdf",
           "HMOS 8-bit CPU, on-chip clock",
           "on-chip oscillator (crystal at 4x E), E and Q clock outputs; FIRQ, IRQ, "
           "NMI; DMA/BREQ; MRDY; 16-bit index registers and stack pointers"),
    "09E": ("09E", "HMOS", EXT_2PH, "mc6809e-8-bit-microprocessor.pdf",
            "HMOS 8-bit CPU, external E/Q clock",
            "external E and Q quadrature clock inputs; TSC three-state control, LIC, "
            "AVMA and BUSY for multiprocessing; FIRQ, IRQ, NMI"),
}


def records():
    for chip, (stem, tech, clock_src, ds, desc, features) in CHIPS.items():
        base = "6809" if chip.startswith("09") else "6800"
        for grade, clock in GRADES.items():
            if chip == "02NS" and grade:
                continue  # the sheet lists only the 1 MHz MC6802NS
            value = f"MC68{grade}{chip}"       # MC6802, MC68A02, MC68B02
            sym_value = f"MC68{grade}{stem}"
            yield row(
                created_by=CREATED_BY, manufacturer="Motorola", mpn=f"{value}P",
                value=value, family=base, core=f"{tech} {value}", technology=tech,
                arch_bits=8, data_bits=8, addr_bits=16, clock=clock,
                clock_source=clock_src, vmin=4.75, vmax=5.25, rails="+5V",
                active_current="1.0W max", package="PDIP-40", pins=40,
                symbol=f"{STOCK}:{sym_value}", datasheet=f"motorola/{ds}",
                description=f"Motorola {value} {desc}, {clock:g}MHz, PDIP-40",
                keywords=[f"68{chip}", f"MC680{chip}", base, "Motorola", tech, "8-bit",
                          "vintage"],
                features=features)


def main():
    write(OUTPUT_FILE, "Motorola 6800 family", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
