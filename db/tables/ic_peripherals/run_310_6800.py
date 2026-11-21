#!/usr/bin/env python3
"""Motorola 6800-family peripherals: MC6821, MC6840, MC6843, MC6844, MC6845, MC6847,
MC6850, MC6852, MC6854.

One classic maker (Motorola), every speed grade (1.0, 1.5 and 2.0 MHz bus: MC68xx,
MC68Axx, MC68Bxx), plastic DIP (P suffix), commercial temperature (no C suffix).
All Obsolete; manufacturer_link NULL, as for the 6800 CPUs.

Sources (datasheets/motorola/, each cut with its package outline pages):
  - 1983 Motorola 8-Bit Microprocessor and Peripheral Data. Ordering key on book
    p. 3-315 (MC6821 sheet): blank/A/B = 1.0/1.5/2.0 MHz; C = -40 to 85 C;
    P plastic, S cerdip, L ceramic. Each sheet's ordering table prints the codes:
      MC6821 PIA 3-307, MC6840 PTM 3-397, MC6844 DMAC 3-410, MC6845 CRTC 3-427,
      MC6850 ACIA 3-494, MC6852 SSDA 3-506, MC6854 ADLC 3-524.
    MC6847/MC6847Y VDG 3-469 prints no table, only "P SUFFIX PLASTIC PACKAGE", so
    MC6847P and MC6847YP are built from it; no speed grades (3.58 MHz clock, not on
    the CPU bus, so max_clock is the 3.579545 MHz colour-burst input).
  - 1981 Motorola Microprocessors Data Manual: MC6843 FDC 4-419 (not in the 1983 book),
    "P SUFFIX PLASTIC PACKAGE", 1 MHz only, so MC6843P.
  MC6820: neither book has a sheet (only passing mentions), so it is not generated;
  the MC6821 replaced it pin for pin.
  Power is printed as internal dissipation PINT max; active_current is that figure.

Symbols: stock KiCad Interface:6821, Interface:MC6843, Interface:MC6844 and
GPU:MC6845, checked pin for pin. Custom terra_symbols_ic_peripherals MC6840 (stock
types D0-D7 as inputs), MC6850 (stock drops the bar on ~CS2), MC6847, MC6852, MC6854.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _per import LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_peripherals_generated_310_6800.sql")
CREATED_BY = Path(__file__).name
GRADES = {"": 1, "A": 1.5, "B": 2}

# chip -> (grades, pins, function, gpio, channels, PINT, symbol, datasheet,
#          description, features)
CHIPS = {
    "21": (GRADES, 40, "PIA", 16, None, "550mW max", "Interface:6821", "mc6821-pia.pdf",
           "peripheral interface adapter (PIA)",
           "two 8-bit bidirectional ports with data-direction registers; CA1/CA2/CB1/"
           "CB2 handshake and interrupt lines; port B Darlington drive; open-drain "
           "IRQA/IRQB"),
    "40": (GRADES, 28, "timer", 0, 3, "700mW max", f"{LIB}:MC6840", "mc6840-ptm.pdf",
           "programmable timer module (PTM)",
           "three 16-bit timers with clock, gate and output each; timer 3 /8 "
           "prescaler; continuous, single-shot, frequency and pulse-width comparison "
           "modes; open-drain IRQ"),
    "43": ({"": 1}, 40, "floppy controller", 0, None, "750mW max", "Interface:MC6843",
           "mc6843-fdc.pdf", "floppy disk controller (FDC)",
           "IBM 3740 (FM) format; ten macro commands; programmed I/O or DMA via "
           "MC6844 (TxRQ/TxAK); separate 1MHz master clock; open-drain IRQ"),
    "44": (GRADES, 40, "DMA", 0, 4, "750mW max", "Interface:MC6844", "mc6844-dmac.pdf",
           "direct memory access controller (DMAC)",
           "four channels with 16-bit address and byte count; TSC steal, HALT steal "
           "and HALT burst modes; fixed or rotating priority; data chaining; 2MB/s"),
    "45": (GRADES, 40, "CRTC", 0, None, "750mW max", "GPU:MC6845", "mc6845-crtc.pdf",
           "CRT controller (CRTC)",
           "14-bit refresh address, 5-bit row address; light pen; programmable "
           "cursor; hardware scroll; interlace; character clock to 3MHz; refreshes "
           "dynamic RAM"),
    "50": (GRADES, 24, "ACIA", 0, 1, "525mW max", f"{LIB}:MC6850", "mc6850-acia.pdf",
           "asynchronous communications interface adapter (ACIA)",
           "8- and 9-bit transmission; parity; /1, /16, /64 clock modes (external "
           "TxCLK/RxCLK, no baud generator); RTS/CTS/DCD; open-drain IRQ"),
    "52": (GRADES, 24, "SSDA", 0, 1, "525mW max", f"{LIB}:MC6852", "mc6852-ssda.pdf",
           "synchronous serial data adapter (SSDA)",
           "3-byte transmit and receive FIFOs; one- or two-character sync; fill "
           "character; 7/8/9-bit words to 1.5Mbps; open-drain IRQ"),
    "54": (GRADES, 28, "ADLC", 0, 1, "850mW max", f"{LIB}:MC6854", "mc6854-adlc.pdf",
           "advanced data-link controller (ADLC), HDLC/SDLC",
           "HDLC/SDLC/ADCCP framing; zero insertion; automatic FCS; 4-byte buffers; "
           "loop mode; DMA request outputs; open-drain IRQ"),
}

VDG_FEATURES = ("internal mask-programmable character ROM or external generator; 4 "
                "alphanumeric, 2 semigraphic and 8 graphic modes to 256x192; "
                "Y/phiA/phiB/CHB outputs for the MC1372; works with the MC6883 SAM")


def records():
    for chip, (grades, pins, func, gpio, ch, pint, sym, ds, desc, feat) in \
            CHIPS.items():
        for grade, clock in grades.items():
            value = f"MC68{grade}{chip}" if grade else f"MC68{chip}"
            yield row(
                created_by=CREATED_BY, manufacturer="Motorola", mpn=f"{value}P",
                value=value, family="6800", function=func, technology="NMOS",
                clock=clock, vmin=4.75, vmax=5.25, rails="+5V", package=f"PDIP-{pins}",
                pins=pins, symbol=sym, datasheet=f"motorola/{ds}", gpio=gpio,
                channels=ch, active_current=pint,
                description=f"Motorola {value} NMOS {desc}, {clock:g}MHz, PDIP-{pins}",
                keywords=[f"68{chip}", f"MC68{chip}", func, "Motorola", "NMOS", "6800",
                          "6809", "vintage"], features=feat)
    for value, scan in (("MC6847", "non-interlaced"), ("MC6847Y", "interlaced")):
        yield row(
            created_by=CREATED_BY, manufacturer="Motorola", mpn=f"{value}P",
            value=value, family="6800", function="VDG", technology="NMOS",
            clock=3.579545, vmin=4.75, vmax=5.25, rails="+5V", package="PDIP-40",
            pins=40, symbol=f"{LIB}:MC6847", datasheet="motorola/mc6847-mc6847y-vdg.pdf",
            gpio=0, active_current="600mW max",
            description=f"Motorola {value} NMOS video display generator (VDG), {scan}"
                        ", 3.58MHz, PDIP-40",
            keywords=["6847", "MC6847", "VDG", "video", "Motorola", "NMOS", "6800",
                      "6809", "vintage"], features=f"{scan} NTSC; {VDG_FEATURES}")


def main():
    write(OUTPUT_FILE, "Motorola 6800 peripherals", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
