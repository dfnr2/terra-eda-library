#!/usr/bin/env python3
"""Zilog Z80-family peripherals: PIO, CTC, SIO/0-1-2, DART and DMA, NMOS and CMOS.

One classic maker (Zilog), every speed grade, plastic DIP, commercial temperature
where the book offers it. All Obsolete: the NMOS parts long ago, the CMOS Z84Cxx by
Zilog's EOL notice (Mouser shows Z84C2008PEG End of Life, 2026-11-20).

Sources (datasheets/zilog/, one cut per device: the 1989 sheet, the 1982 ordering
page, the 1989 ordering pages, code key and DIP outlines):
  - 1982 Zilog Data Book (June 1982 specs): NMOS codes as printed in each ordering
    table, "Z8420 PS" etc. written without the space (P plastic, S 0-70 C); grades
    Z80 / Z80A / Z80B = 2.5 / 4 / 6 MHz. PIO book 67, CTC 81, SIO 93, DART 109,
    DMA 49 (DMA has no B grade). The PIO table prints "4.0 MHz" against Z8420PS; the
    other Z8420 rows are 2.5 MHz, so 2.5 MHz is used.
  - 1989 Zilog Z80 Family Data Book: key Z + product + speed + package + temperature
    + flow (PSC = plastic, 0-70 C). NMOS peripherals stop at 6 MHz there (same parts
    as the 1982 B grade, so not repeated). CMOS codes: Z84C2004/06/08PSC,
    Z84C3004/06/08PSC, Z84C4004/06/08PSC, Z84C4104/06PSC (no 8 MHz SIO/1),
    Z84C4204/06/08PSC. The CMOS DMA comes only in E temperature (-40 to 100 C), so
    Z84C1004/06/08PEC are generated as E parts (as the CPU's Z84C0010PEC). There is
    no CMOS DART, and the SIO/3, SIO/4 and KIO have no DIP.
  ICC max: NMOS PIO 100 mA, CTC 120, SIO/DART 100, DMA 150 (Z80) / 200 (Z80A) mA;
  CMOS per the 1989 DC tables at each clock.

Symbols: stock KiCad Interface:Z8420 for the PIO (checked pin for pin). Custom
terra_symbols_ic_peripherals Z8430 (CTC), Z8440/Z8441/Z8442 (one per SIO bonding
option), Z8470 (DART) and Z8410 (DMA); NMOS and CMOS DIP pinouts are identical.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _per import LIB, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_peripherals_generated_330_z80.sql")
CREATED_BY = Path(__file__).name
NMOS_GRADES = {"": 2.5, "A": 4, "B": 6}
DS = "zilog/{}.pdf"

# device -> (nmos stem, cmos stem, pins, function, gpio, channels, symbol, datasheet,
#            name, NMOS ICC, {CMOS MHz: ICC}, features)
DEVICES = {
    "PIO": ("Z8420", "Z84C20", 40, "PIO", 16, 2, "Interface:Z8420", "z8420-z84c20-pio",
            "parallel input/output (PIO)", "100mA max", {4: "5mA", 6: "6mA", 8: "7mA"},
            "two 8-bit ports with ASTB/ARDY/BSTB/BRDY handshake; modes 0 output, 1 "
            "input, 2 bidirectional (port A), 3 bit control; IEI/IEO daisy-chain "
            "vectored interrupts; open-drain INT"),
    "CTC": ("Z8430", "Z84C30", 28, "timer", 0, 4, f"{LIB}:Z8430", "z8430-z84c30-ctc",
            "counter/timer circuit (CTC)", "120mA max", {4: "7mA", 6: "8mA", 8: "10mA"},
            "four 8-bit down counters with auto-reload; /16 or /256 prescaler; counter "
            "or timer mode; ZC/TO outputs on channels 0-2; IEI/IEO daisy-chain "
            "vectored interrupts; open-drain INT"),
    "SIO/0": ("Z8440", "Z84C40", 40, "USART", 0, 2, f"{LIB}:Z8440", "z8440-z84c40-sio",
              "SIO/0 serial input/output (TxCB and RxCB bonded)", "100mA max",
              {4: "10mA", 6: "10mA", 8: "12mA"}, None),
    "SIO/1": ("Z8441", "Z84C41", 40, "USART", 0, 2, f"{LIB}:Z8441", "z8440-z84c40-sio",
              "SIO/1 serial input/output (no DTRB)", "100mA max",
              {4: "10mA", 6: "10mA"}, None),
    "SIO/2": ("Z8442", "Z84C42", 40, "USART", 0, 2, f"{LIB}:Z8442", "z8440-z84c40-sio",
              "SIO/2 serial input/output (no SYNCB)", "100mA max",
              {4: "10mA", 6: "10mA", 8: "12mA"}, None),
    "DART": ("Z8470", None, 40, "UART", 0, 2, f"{LIB}:Z8470", "z8470-dart",
             "dual asynchronous receiver/transmitter (DART)", "100mA max", {},
             "two async channels to 1.2Mbps (x1 at 6MHz); x1/x16/x32/x64 external "
             "clocks; quad-buffered receivers; RI inputs; modem lines; IEI/IEO "
             "daisy-chain interrupts; open-drain INT"),
    "DMA": ("Z8410", "Z84C10", 40, "DMA", 0, 1, f"{LIB}:Z8410", "z8410-z84c10-dma",
            "direct memory access controller (DMA)", None,
            {4: None, 6: "25mA", 8: "35mA"},
            "one channel, two ports; byte, burst and continuous modes; transfer, "
            "search or search-and-transfer; memory and I/O in any combination; BAI/BAO "
            "bus-request daisy chain; open-drain INT/PULSE"),
}
SIO_FEATURES = ("two full-duplex channels, async and sync (bisync, SDLC/HDLC); CRC-16 "
                "and CCITT; quad-buffered receivers; external RxC/TxC (no baud "
                "generator); W/RDY for DMA; IEI/IEO daisy-chain vectored interrupts; "
                "open-drain INT")
DMA_NMOS_ICC = {"": "150mA max", "A": "200mA max"}


def records():
    for dev, (nmos, cmos, pins, func, gpio, ch, sym, ds, name, icc, c_icc, feat) in \
            DEVICES.items():
        feat = feat or SIO_FEATURES
        common = dict(created_by=CREATED_BY, manufacturer="Zilog", family="Z80",
                      function=func, rails="+5V", package=f"PDIP-{pins}", pins=pins,
                      symbol=sym, datasheet=DS.format(ds), gpio=gpio, channels=ch)
        keywords = ["Z80", dev, nmos, func, "Zilog", "vintage"]
        for grade, clock in NMOS_GRADES.items():
            if dev == "DMA" and grade == "B":
                continue  # the 1982 DMA sheet has no Z80B grade
            value = f"{nmos}{grade}"
            yield row(
                **common, mpn=f"{value}PS", value=value, technology="NMOS",
                clock=clock, vmin=4.75, vmax=5.25,
                active_current=DMA_NMOS_ICC[grade] if dev == "DMA" else icc,
                description=f"Zilog {value} Z80 {name}, NMOS, {clock:g}MHz, "
                            f"PDIP-{pins}",
                keywords=keywords + ["NMOS"], features=feat)
        for clock, cur in c_icc.items():
            temp = (-40, 100) if dev == "DMA" else (0, 70)
            mpn = f"{cmos}{clock:02d}P{'E' if temp[0] < 0 else 'S'}C"
            extra = "" if cur else "; ICC not printed at 4MHz"
            yield row(
                **common, mpn=mpn, value=cmos, technology="CMOS", clock=clock,
                vmin=4.5, vmax=5.5, temp=temp,
                active_current=f"{cur} max" if cur else None,
                description=f"Zilog {cmos} Z80 {name}, CMOS, {clock}MHz, "
                            f"{temp[0]} to {temp[1]}C, PDIP-{pins}",
                keywords=keywords + [cmos, "CMOS"],
                features=f"{feat}; static: 10uA standby with clock stopped{extra}")


def main():
    write(OUTPUT_FILE, "Zilog Z80 peripherals", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
