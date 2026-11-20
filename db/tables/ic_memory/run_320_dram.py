#!/usr/bin/env python3
"""Vintage dynamic RAMs: Intel, Mostek, TI, Toshiba.

One classic example per chip (see plans/vintage-computer-parts.md, "Manufacturer
coverage"), one row per speed grade the classic datasheet lists, commercial
temperature, plastic DIP (CERDIP for the 2118, the only package Intel's books
code for it). All are Obsolete.

Sources, each cut down to the chip's pages in datasheets/<mfr>/:
  - Intel 1975 Data Catalog: 1103, 1103-1, 1103A, 1103A-1, 1103A-2 pp. 2-7..2-28,
    with the ordering instructions (1-12) and 18-lead outlines (1-9) appended.
  - Intel 1981 Component Data Catalog: 2118 pp. 1-16..1-26, with the ordering
    information (12-12) and the 16-lead P and D package outlines appended.
  - Mostek 1980 Memory Data Book and Designers Guide: MK4027 pp. V-1..V-16,
    MK4096 V-17..V-24, MK4116 V-33..V-46 plus V-67..V-68 (typical characteristics),
    MK4164 V-69..V-77 (PRELIMINARY). Mostek 1984/1985 Microelectronic Data Book:
    MK4564-12 pp. IV-61..IV-69 and MK4564-15/20 IV-71..IV-79, with the ordering key
    (II-14) and package outlines (II-5) appended; the 1982 sheet is preliminary.
  - TI 1986 MOS Memory Data Book (SMYD006): TMS4416 pp. 4-99..4-115, TMS4464
    4-117..4-134, each with the selection guide (1-10), the numbering key (11-3)
    and package outlines appended. The 1984 book has both only as product previews.
  - Toshiba 1987 MOS Memory: TMM41256P pp. A-3..A-12 and the TMM41256AP die
    revision A-13..A-31, both kept in one PDF.

Ordering codes:
  - Intel's 1975 ordering instructions give the package prefix rule with this very
    example, "P 1103" (P = plastic), and list P/C/D for every 1103 grade.
  - No Intel book prints a plastic P2118. The only package-coded 2118s are the
    1983 Memory Component Handbook's Express codes "QD 2118-3/-4/-7", i.e. CERDIP
    (D), so the rows are D2118 with the 1981 catalog's grade numbers. That catalog
    prints the grades as -10/-12/-15; the 1979 catalog and 1983 handbook give the
    same three speeds as -3/-4/-7.
  - Mostek prints no ordering table. Each sheet's title gives the packages and
    grades, e.g. "MK4116(J/N/E)-2/3", and p. II-1 gives the rule: MK + device +
    package letter + dash number, N = plastic. The codes below are built that way.
  - TI's sheets print grades and packages but not whole codes; the 1986 book's
    numbering key (p. 11-3) gives TMS + device + -speed + package + temperature,
    N = plastic DIP, L = 0 to 70 C (as printed elsewhere: "TMS4256-12NL").
  - Toshiba's selection guide prints the codes ("TMM41256P/T-12"); P = plastic DIP.

Symbols: the 1103 and 1103A differ only in pin 5 (precharge clock vs N.C.) and get
one custom symbol each. Stock Memory_RAM MK4116N, MK4164N and TMM41256AP match their chips pin
for pin; the MK4096/MK4027 and TMS4416/TMS4464 pinouts are custom symbols in
terra_symbols_ic_memory (pin tables in _pinouts.py).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _memory import org, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_memory_generated_320_dram.sql")
CREATED_BY = Path(__file__).name
LIB = "terra_symbols_ic_memory"

THREE_RAIL = "+12V, +5V, -5V"
VBB_FIRST = "apply VBB (-5V) first and remove it last"


def C(**kw):
    return kw


# Each chip: its grades as (ordering code, tRAC ns, tRC ns, grade note[, rails,
# temperature]) -- the 1103 grades differ in supply voltages and temperature.
CHIPS = [
    # ---- Intel ------------------------------------------------------------------
    # PMOS, negative logic: VDD is the 0V reference, VSS the main supply and VBB
    # the substrate 3-4V above it (selection guide: "+16, +19" / "+19, +22").
    C(mfr="Intel", value="1103", words=1024, bits=1, pins=18, width=0.3,
      symbol=f"{LIB}:1103", ds="intel/1103-1kx1-dynamic-ram.pdf", tech="PMOS",
      io="precharge clock, MOS-level inputs, current output needs a sense amplifier",
      grades=[("P1103", 300, 580, "VSS +16V, VBB +19V, VDD 0V", "+19V, +16V", (0, 70)),
              ("P1103-1", 150, 340, "VSS +19V, VBB +22V, VDD 0V, 1 ms refresh",
               "+22V, +19V", (0, 55))],
      kw=["1103", "first DRAM", "3208A"]),
    C(mfr="Intel", value="1103A", words=1024, bits=1, pins=18, width=0.3,
      symbol=f"{LIB}:1103A", ds="intel/1103-1kx1-dynamic-ram.pdf", tech="PMOS",
      io="no precharge clock, MOS-level inputs, current output needs a sense amplifier",
      grades=[("P1103A", 205, 580, "VSS +16V, VBB +19V, VDD 0V", "+19V, +16V", (0, 70)),
              ("P1103A-1", 145, 340, "VSS +19V, VBB +22V, VDD 0V, 1 ms refresh",
               "+22V, +19V", (0, 55)),
              ("P1103A-2", 145, 400, "VSS +19V, VBB +22V, VDD 0V, 1 ms refresh",
               "+22V, +19V", (0, 55))],
      kw=["1103", "1103A", "3208A"]),
    C(mfr="Intel", value="2118", words=16384, bits=1, pins=16, width=0.3,
      symbol=f"{LIB}:2118", ds="intel/2118-16kx1-dynamic-ram.pdf", tech="NMOS",
      io="single supply (page mode and hidden refresh are S-number options)",
      rails="+5V", package="CERDIP-16",
      note="pins 1 and 9 N/C, not 4116-socket compatible",
      grades=[("D2118-10", 100, 235, "also graded 2118-3"),
              ("D2118-12", 120, 270, "also graded 2118-4"),
              ("D2118-15", 150, 320, "also graded 2118-7")],
      kw=["2118", "2118-3", "2118-4", "2118-7"]),
    # ---- Mostek -----------------------------------------------------------------
    C(mfr="Mostek", value="MK4096", words=4096, bits=1, pins=16, width=0.3,
      symbol=f"{LIB}:MK4096", ds="mostek/mk4096-4kx1-dynamic-ram.pdf", tech="NMOS",
      io="latched output, chip select", rails=THREE_RAIL,
      note="apply VBB within 5 s of VDD; not for new design (1980)",
      grades=[("MK4096N-6", 250, 375, None), ("MK4096N-16", 300, 425, None),
              ("MK4096N-11", 350, 500, None)],
      kw=["4096", "MK4027 pinout"]),
    C(mfr="Mostek", value="MK4027", words=4096, bits=1, pins=16, width=0.3,
      symbol=f"{LIB}:MK4096", ds="mostek/mk4027-4kx1-dynamic-ram.pdf", tech="NMOS",
      io="latched output, chip select, page mode", rails=THREE_RAIL, note=VBB_FIRST,
      grades=[("MK4027N-2", 150, 320, None), ("MK4027N-3", 200, 375, None),
              ("MK4027N-4", 250, 380, None)],
      kw=["4027", "MK4096 pinout"]),
    C(mfr="Mostek", value="MK4116", words=16384, bits=1, pins=16, width=0.3,
      symbol="Memory_RAM:MK4116N", ds="mostek/mk4116-16kx1-dynamic-ram.pdf",
      tech="NMOS", io="page mode", rails=THREE_RAIL, note=VBB_FIRST,
      grades=[("MK4116N-2", 150, 320, None), ("MK4116N-3", 200, 375, None),
              ("MK4116N-4", 250, 410, None)],
      kw=["4116", "TRS-80", "Apple II"]),
    C(mfr="Mostek", value="MK4164", words=65536, bits=1, pins=16, width=0.3,
      symbol="Memory_RAM:MK4164N", ds="mostek/mk4164-64kx1-dynamic-ram.pdf",
      tech="NMOS", io="page mode, pin 1 refresh (~RFSH)", rails="+5V",
      note="preliminary data sheet (1980)",
      grades=[("MK4164N-12", 120, 265, None), ("MK4164N-15", 150, 325, None)],
      kw=["4164", "MK4116 successor"]),
    C(mfr="Mostek", value="MK4564", words=65536, bits=1, pins=16, width=0.3,
      symbol=f"{LIB}:MK4564", ds="mostek/mk4564-64kx1-dynamic-ram.pdf",
      tech="NMOS", io="page mode, pin 1 N/C", rails="+5V",
      note="production successor to the MK4164",
      grades=[("MK4564N-12", 120, 220, None), ("MK4564N-15", 150, 260, None),
              ("MK4564N-20", 200, 330, None)],
      kw=["4564", "4164", "JEDEC 4164 pinout"]),
    # ---- Texas Instruments ------------------------------------------------------
    C(mfr="Texas Instruments", value="TMS4416", words=16384, bits=4, pins=18,
      width=0.3, symbol=f"{LIB}:TMS4416", ds="ti/tms4416-16kx4-dynamic-ram.pdf",
      tech="NMOS", io="common I/O, output enable, page mode", rails="+5V",
      grades=[("TMS4416-12NL", 120, 230, None), ("TMS4416-15NL", 150, 260, None),
              ("TMS4416-20NL", 200, 330, None)],
      kw=["4416", "41416"]),
    C(mfr="Texas Instruments", value="TMS4464", words=65536, bits=4, pins=18,
      width=0.3, symbol=f"{LIB}:TMS4416", ds="ti/tms4464-64kx4-dynamic-ram.pdf",
      tech="NMOS", io="common I/O, output enable, page mode, CAS-before-RAS refresh",
      rails="+5V",
      grades=[("TMS4464-12NL", 120, 230, None), ("TMS4464-15NL", 150, 260, None),
              ("TMS4464-20NL", 200, 330, None)],
      kw=["4464", "41464", "TMS4416 pinout"]),
    # ---- Toshiba ----------------------------------------------------------------
    C(mfr="Toshiba", value="TMM41256", words=262144, bits=1, pins=16, width=0.3,
      symbol="Memory_RAM:TMM41256AP", ds="toshiba/tmm41256-256kx1-dynamic-ram.pdf",
      tech="NMOS", io="page mode", rails="+5V",
      grades=[("TMM41256P-12", 120, 220, None), ("TMM41256P-15", 150, 260, None),
              ("TMM41256AP-10", 100, 190, "A version, CAS-before-RAS refresh"),
              ("TMM41256AP-12", 120, 220, "A version, CAS-before-RAS refresh"),
              ("TMM41256AP-15", 150, 260, "A version, CAS-before-RAS refresh")],
      kw=["41256", "TMM41256AP", "uPD41256"]),
]


def records():
    for chip in CHIPS:
        o = org(chip["words"], chip["bits"])
        for grade in chip["grades"]:
            mpn, trac, trc, note = grade[:4]
            rails = grade[4] if len(grade) > 4 else chip["rails"]
            temp = grade[5] if len(grade) > 5 else (0, 70)
            package = chip.get("package", f"PDIP-{chip['pins']}")
            bits = [f"{chip['mfr']} {chip['value']} {o} {chip['tech']} dynamic RAM",
                    chip["io"], f"{trac}ns access, {trc}ns cycle"]
            if note:
                bits.append(note)
            # The 1103 grade notes already name each rail.
            if rails != "+5V" and len(grade) <= 4:
                bits.append(rails.replace(", ", "/"))
            if chip.get("note"):
                bits.append(chip["note"])
            if temp != (0, 70):
                bits.append(f"{temp[0]} to {temp[1]}C")
            bits.append(package)
            yield row(
                created_by=CREATED_BY, manufacturer=chip["mfr"], mpn=mpn,
                value=chip["value"], memory_type="DRAM",
                words=chip["words"], bits=chip["bits"], speed=f"{trac} ns",
                package=package, pins=chip["pins"], width_in=chip["width"],
                symbol=chip["symbol"], datasheet=chip["ds"],
                description=", ".join(bits),
                keywords=chip["kw"] + ["DRAM", "dynamic RAM", chip["tech"], "vintage"],
                supply_rails=rails, mfr_link=chip.get("link"), temp=temp)


def main():
    write(OUTPUT_FILE, "vintage dynamic RAMs", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
