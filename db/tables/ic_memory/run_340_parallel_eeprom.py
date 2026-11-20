#!/usr/bin/env python3
"""Parallel (byte-wide) EEPROMs for vintage and retro builds.

Programmable memories get every maker's sheet rather than one classic example (see
plans/vintage-computer-parts.md, "Manufacturer coverage"): makers differ in write
voltage and write protocol (the Intel 2816 needs a shaped 21V pulse, the SEEQ 52B13
must be erased before each write, later parts are self-timed with page writes). One
row per speed grade, commercial temperature, plastic DIP where the book offers it and
ceramic only where it is the only option. Vintage parts are Obsolete; the two
Microchip -PU rows are the modern parts, with lifecycle from Mouser.

Sources, each cut down to the chip's pages (plus the DIP outline) in datasheets/<mfr>/:
  - Intel 1981 Component Data Catalog: 2816 pp. 2-23..2-34 (PRELIMINARY), with the
    24-lead Type D outline (12-6).
  - Intel 1984 Memory Components Handbook: 2816A pp. 5-83..5-94 and 2817A
    5-95..5-103 (both PRELIMINARY), with the Type D outlines (7-3, 7-4).
  - Xicor 1985 Data Book: X2816A pp. 3-13..3-18, with the part numbering system
    (7-4) and the 24-lead outlines (7-10, 7-11).
  - Xicor 1990 Data Book: X2816B pp. 3-9..3-17, X2816C 3-19..3-27, X2864A
    3-29..3-37, X28C64 3-55..3-67, X28256 3-69..3-82, X28C256 3-83..3-96, X28C010
    3-111..3-113 (a fact sheet), each with its ordering key (10-10..10-13) and outlines.
  - SEEQ 1985 Data Book: 2816A pp. 2-4..2-8, 2864 2-14..2-19 (PRELIMINARY), 52B13
    2-20..2-26, 52B33 2-27..2-33.
  - Atmel 1990 Data Book: AT28C16 pp. 2-51..2-59, AT28C17 2-61..2-69, AT28C64/64X
    2-71..2-82, AT28C256 2-93..2-104, AT28C010 2-125..2-132 (PRELIMINARY), with the
    package outlines (14-5..14-7, 14-14).
  - Microchip: AT28C64B (DS20006432B), AT28C256 (DS20006386B).

Ordering codes:
  - Intel prints no codes for these parts. As for the EPROMs, they follow the
    catalog's rule (package prefix + device + grade) with D, Type D hermetic DIP, the
    outline appended to each sheet. Built, not printed.
  - Xicor 1985 prints one generic key (7-4): device + package (P plastic) + blank
    temperature (commercial) + access-time suffix; the grades are the sheet's AC
    columns. The 1990 book prints a key per device; plastic P codes are used, except
    the X28C010, which has only ceramic (D cerdip). Grades that appear only in a key
    and not in the sheet's AC table (X28256-20, X28C010-15) are left out.
  - SEEQ sells only D (cerdip) Q (0 to 70 C) parts; each sheet's ordering box gives
    the key with the access time in ns as the suffix, and the grades are its AC
    columns. The 52B33's key adds "35 = 350ns @ 5% VCC". Not generated: the 2817A
    (no ordering box or outline on the commercial sheet) and the 2864-35 (in the AC
    table but not the key).
  - Atmel 1990 prints its codes; the plastic PC ones are used (the AT28C010 has only
    the BC side-braze ceramic DIP). The E (high endurance) and F (fast write)
    options printed beside them are left out.
  - Microchip prints its codes; the PDIP -15PU ones are used.

Symbols: stock Memory_EEPROM where the pinout matches pin for pin: KM28C64A (8Kx8,
pins 1 and 26 NC), KM28C65A (8Kx8, RDY/~BUSY on pin 1) and 28C256. Custom DIP symbols
in terra_symbols_ic_memory for the rest (pin tables in _pinouts.py): 2816 (VPP on pin
21), 2816A (6116 pinout, ~WE on pin 21), 2817A, 52B33 and 28C010.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _memory import row, write

OUTPUT_FILE = Path(__file__).with_name("ic_memory_generated_340_parallel_eeprom.sql")
CREATED_BY = Path(__file__).name
LIB = "terra_symbols_ic_memory"
MCHP = "https://www.microchip.com/en-us/product/"
NC1 = "Memory_EEPROM:KM28C64A"   # 8Kx8, pins 1 and 26 NC
RDY1 = "Memory_EEPROM:KM28C65A"  # 8Kx8, RDY/~BUSY on pin 1, pin 26 NC
K256 = "Memory_EEPROM:28C256"

FIVE = "VCC +/-5%"
TEN = "VCC +/-10%"


def C(**kw):
    return kw


def grades(prefix, suffixes, note=None):
    """[(suffix, ns), ...] -> [(code, ns, note), ...] for one device prefix."""
    return [(f"{prefix}{s}", ns, note) for s, ns in suffixes]


CHIPS = [
    # ---- Intel (codes built: D = Type D hermetic DIP) --------------------------------
    C(mfr="Intel", value="2816", words=2048, pins=24, package="CERDIP-24",
      symbol=f"{LIB}:2816", ds="intel/2816-2kx8-eeprom.pdf", tech="NMOS",
      vpp="21V", cycles="10K", years=None, vcc=FIVE,
      write="21V exponential pulse on VPP (pin 21) for each byte, erase before write, "
            "no on-chip latches; 2716 pinout; from a PRELIMINARY sheet",
      grades=grades("D2816", [("", 250), ("-3", 350)]), kw=["2816", "D2816", "2716"]),
    C(mfr="Intel", value="2816A", words=2048, pins=24, package="CERDIP-24",
      symbol=f"{LIB}:2816A", ds="intel/2816a-2kx8-eeprom.pdf", tech="HMOS-E",
      vpp=None, cycles="10K", years="10 years", vcc=FIVE,
      write="5V-only, 9-15ms ~WE pulse with address and data held, erase before write; "
            "also takes the 2816's 21V pulse on pin 21; from a PRELIMINARY sheet",
      grades=grades("D2816A", [("-2", 200), ("", 250), ("-3", 350), ("-4", 450)]),
      kw=["2816A", "2816", "28C16", "6116"]),
    C(mfr="Intel", value="2817A", words=2048, pins=28, package="CERDIP-28",
      symbol=f"{LIB}:2817A", ds="intel/2817a-2kx8-eeprom.pdf", tech="HMOS-E",
      vpp=None, cycles="10K", years="10 years", vcc=FIVE,
      write="5V-only, latched self-timed byte write, open-drain RDY/~BUSY on pin 1; "
            "from a PRELIMINARY sheet",
      grades=[("D2817A-1", 200, "10ms write"), ("D2817A-2", 200, "20ms write"),
              ("D2817A", 250, None), ("D2817A-3", 350, None),
              ("D2817A-4", 450, "30ms write")],
      kw=["2817A", "2817", "28C17"]),
    # ---- Xicor (P = plastic DIP; X28C010 D = cerdip) ---------------------------------
    C(mfr="Xicor", value="X2816A", words=2048, pins=24, package="PDIP-24",
      symbol=f"{LIB}:2816A", ds="xicor/x2816a-2kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles=None, years="100 years", vcc=FIVE,
      write="5V-only, self-timed 10ms byte write",
      grades=grades("X2816AP", [("-25", 250), ("", 300), ("-35", 350), ("-45", 450)]),
      kw=["X2816A", "2816A", "2816", "28C16", "6116"]),
    C(mfr="Xicor", value="X2816B", words=2048, pins=24, package="PDIP-24",
      symbol=f"{LIB}:2816A", ds="xicor/x2816b-2kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="100 years", vcc=TEN,
      write="5V-only, 16-byte page write, 10ms, DATA polling",
      grades=grades("X2816BP", [("-25", 250), ("", 300)]),
      kw=["X2816B", "2816", "28C16", "6116"]),
    C(mfr="Xicor", value="X2816C", words=2048, pins=24, package="PDIP-24",
      symbol=f"{LIB}:2816A", ds="xicor/x2816c-2kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="100 years", vcc=TEN,
      write="5V-only, 16-byte page write, 10ms, DATA polling",
      grades=grades("X2816CP", [("-20", 200)]), kw=["X2816C", "2816", "28C16", "6116"]),
    C(mfr="Xicor", value="X2864A", words=8192, pins=28, package="PDIP-28",
      symbol=NC1, ds="xicor/x2864a-8kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="100 years", vcc=FIVE,
      write="5V-only, 16-byte page write, 10ms, DATA polling",
      grades=grades("X2864AP", [("-25", 250), ("", 300), ("-35", 350), ("-45", 450)]),
      kw=["X2864A", "2864", "28C64"]),
    C(mfr="Xicor", value="X28C64", words=8192, pins=28, package="PDIP-28",
      symbol=NC1, ds="xicor/x28c64-8kx8-cmos-eeprom.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="100 years", vcc=TEN,
      write="5V-only, 64-byte page write, 10ms, DATA polling and toggle bit, "
            "software data protection",
      grades=grades("X28C64P", [("-12", 120), ("-15", 150), ("-20", 200), ("-25", 250)]),
      kw=["X28C64", "28C64", "2864"]),
    C(mfr="Xicor", value="X28256", words=32768, pins=28, package="PDIP-28",
      symbol=K256, ds="xicor/x28256-32kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="100 years", vcc=FIVE,
      write="5V-only, 64-byte page write, 10ms, DATA polling and toggle bit, "
            "software data protection",
      grades=grades("X28256P", [("-25", 250), ("", 300), ("-35", 350)]),
      kw=["X28256", "28256", "28C256", "62256"]),
    C(mfr="Xicor", value="X28C256", words=32768, pins=28, package="PDIP-28",
      symbol=K256, ds="xicor/x28c256-32kx8-cmos-eeprom.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="100 years", vcc=TEN,
      write="5V-only, 64-byte page write, 10ms, DATA polling and toggle bit, "
            "software data protection",
      grades=grades("X28C256P", [("-15", 150), ("-20", 200), ("-25", 250), ("", 300)]),
      kw=["X28C256", "28C256", "62256"]),
    C(mfr="Xicor", value="X28C010", words=131072, pins=32, package="CERDIP-32",
      symbol=f"{LIB}:28C010", ds="xicor/x28c010-128kx8-cmos-eeprom.pdf", tech="CMOS",
      vpp=None, cycles=None, years="10 years", vcc=None,
      write="5V-only, 128-byte page write, DATA polling and toggle bit, software data "
            "protection; from a fact sheet",
      grades=grades("X28C010D", [("-20", 200)]), kw=["X28C010", "28C010", "27C010"]),
    # ---- SEEQ (D = cerdip, Q = 0 to 70 C) --------------------------------------------
    C(mfr="SEEQ", value="2816A", words=2048, pins=24, package="CERDIP-24",
      symbol=f"{LIB}:2816A", ds="seeq/2816a-2kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years=None, vcc=TEN,
      write="5V-only, latched self-timed 10ms byte write",
      grades=grades("DQ2816A", [("-250", 250), ("-300", 300), ("-350", 350)]),
      kw=["2816A", "DQ2816A", "2816", "X2816A", "6116"]),
    C(mfr="SEEQ", value="2816AH", words=2048, pins=24, package="CERDIP-24",
      symbol=f"{LIB}:2816A", ds="seeq/2816a-2kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years=None, vcc=TEN,
      write="5V-only, latched self-timed 2ms byte write",
      grades=grades("DQ2816AH", [("-250", 250), ("-300", 300)]),
      kw=["2816AH", "2816A", "2816", "6116"]),
    C(mfr="SEEQ", value="2864", words=8192, pins=28, package="CERDIP-28",
      symbol=RDY1, ds="seeq/2864-8kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN,
      write="5V-only, latched self-timed 10ms byte write, open-drain RDY/~BUSY on "
            "pin 1; from a PRELIMINARY sheet",
      grades=grades("DQ2864", [("-250", 250), ("-300", 300)]),
      kw=["2864", "DQ2864", "X2864", "AM9864", "28C64"]),
    C(mfr="SEEQ", value="2864H", words=8192, pins=28, package="CERDIP-28",
      symbol=RDY1, ds="seeq/2864-8kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN,
      write="5V-only, latched self-timed 2ms byte write, open-drain RDY/~BUSY on "
            "pin 1; from a PRELIMINARY sheet",
      grades=grades("DQ2864H", [("-250", 250), ("-300", 300)]),
      kw=["2864H", "2864", "28C64"]),
    C(mfr="SEEQ", value="52B13", words=2048, pins=24, package="CERDIP-24",
      symbol=f"{LIB}:2816A", ds="seeq/52b13-2kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years=None, vcc=TEN,
      write="latched, no timer: hold ~WE low 9-70ms per write, erase each byte "
            "before writing; also takes a 21V ~WE pulse",
      grades=grades("DQ52B13", [("-200", 200), ("-250", 250), ("-350", 350)]),
      kw=["52B13", "5213", "2816", "6116"]),
    C(mfr="SEEQ", value="52B13H", words=2048, pins=24, package="CERDIP-24",
      symbol=f"{LIB}:2816A", ds="seeq/52b13-2kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years=None, vcc=TEN,
      write="latched, no timer: hold ~WE low 1-10ms per write, erase each byte "
            "before writing; 5V only",
      grades=grades("DQ52B13H", [("-200", 200), ("-250", 250), ("-350", 350)]),
      kw=["52B13H", "52B13", "2816", "6116"]),
    C(mfr="SEEQ", value="52B33", words=8192, pins=28, package="CERDIP-28",
      symbol=f"{LIB}:52B33", ds="seeq/52b33-8kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN,
      write="latched, no timer: hold ~WE low 9ms per write, erase each byte before "
            "writing; chip clear ~CC on pin 1",
      grades=grades("DQ52B33", [("-200", 200), ("-250", 250), ("-350", 350)])
      + [("DQ52B33-35", 350, FIVE)],
      kw=["52B33", "2864"]),
    C(mfr="SEEQ", value="52B33H", words=8192, pins=28, package="CERDIP-28",
      symbol=f"{LIB}:52B33", ds="seeq/52b33-8kx8-eeprom.pdf", tech="NMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN,
      write="latched, no timer: hold ~WE low 1ms per write, erase each byte before "
            "writing; chip clear ~CC on pin 1",
      grades=grades("DQ52B33H", [("-250", 250)]), kw=["52B33H", "52B33", "2864"]),
    # ---- Atmel 1990 (PC = plastic DIP, 0 to 70 C; AT28C010 BC = side-braze) ----------
    C(mfr="Atmel", value="AT28C16", words=2048, pins=24, package="PDIP-24",
      symbol=f"{LIB}:2816A", ds="atmel/at28c16-2kx8-eeprom-1990.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN, link=MCHP + "AT28C16",
      write="5V-only, self-timed 1ms byte write, DATA polling",
      grades=grades("AT28C16", [("-15PC", 150), ("-20PC", 200), ("-25PC", 250)]),
      kw=["AT28C16", "28C16", "2816", "6116"]),
    C(mfr="Atmel", value="AT28C17", words=2048, pins=28, package="PDIP-28",
      symbol=f"{LIB}:2817A", ds="atmel/at28c17-2kx8-eeprom-1990.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN, link=MCHP + "AT28C17",
      write="5V-only, self-timed 1ms byte write, DATA polling, open-drain RDY/~BUSY "
            "on pin 1",
      grades=grades("AT28C17", [("-15PC", 150), ("-20PC", 200), ("-25PC", 250)]),
      kw=["AT28C17", "28C17", "2817A"]),
    C(mfr="Atmel", value="AT28C64", words=8192, pins=28, package="PDIP-28",
      symbol=RDY1, ds="atmel/at28c64-8kx8-eeprom-1990.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN, link=MCHP + "AT28C64",
      write="5V-only, self-timed 1ms byte write, DATA polling, open-drain RDY/~BUSY "
            "on pin 1",
      grades=grades("AT28C64", [("-15PC", 150), ("-20PC", 200), ("-25PC", 250)]),
      kw=["AT28C64", "28C64", "2864"]),
    C(mfr="Atmel", value="AT28C64X", words=8192, pins=28, package="PDIP-28",
      symbol=NC1, ds="atmel/at28c64-8kx8-eeprom-1990.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN, link=MCHP + "AT28C64",
      write="5V-only, self-timed 1ms byte write, DATA polling, pin 1 NC (no RDY/~BUSY)",
      grades=grades("AT28C64X", [("-15PC", 150), ("-20PC", 200), ("-25PC", 250)]),
      kw=["AT28C64X", "AT28C64", "28C64", "2864"]),
    C(mfr="Atmel", value="AT28C256", words=32768, pins=28, package="PDIP-28",
      symbol=K256, ds="atmel/at28c256-32kx8-eeprom-1990.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN, link=MCHP + "AT28C256",
      write="5V-only, 64-byte page write, 10ms, DATA polling and toggle bit, "
            "software data protection",
      grades=grades("AT28C256", [("-15PC", 150), ("-20PC", 200), ("-25PC", 250)]),
      kw=["AT28C256", "28C256", "62256"]),
    C(mfr="Atmel", value="AT28C010", words=131072, pins=32,
      package="side-braze ceramic DIP-32",
      symbol=f"{LIB}:28C010", ds="atmel/at28c010-128kx8-eeprom-1990.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN, link=MCHP + "AT28C010",
      write="5V-only, 128-byte page write, 10ms, DATA polling and toggle bit, "
            "software data protection; from a PRELIMINARY sheet",
      grades=grades("AT28C010", [("-15BC", 150), ("-20BC", 200), ("-25BC", 250)]),
      kw=["AT28C010", "28C010", "27C010"]),
    # ---- Microchip (current, Active on Mouser 2026-11-20) ----------------------------
    C(mfr="Microchip", value="AT28C64B", words=8192, pins=28, package="PDIP-28",
      symbol=NC1, ds="microchip/at28c64b-8kx8-eeprom.pdf", tech="CMOS",
      vpp=None, cycles="100K", years="10 years", vcc=TEN, link=MCHP + "AT28C64B",
      lifecycle="Active", rohs="Yes", temp=(-40, 85),
      write="5V-only, 64-byte page write, 10ms, DATA polling and toggle bit, "
            "software data protection, pins 1 and 26 NC",
      grades=[("AT28C64B-15PU", 150, None)], kw=["AT28C64B", "28C64", "2864", "retro"]),
    C(mfr="Microchip", value="AT28C256", words=32768, pins=28, package="PDIP-28",
      symbol=K256, ds="microchip/at28c256-32kx8-eeprom.pdf", tech="CMOS",
      vpp=None, cycles="10K", years="10 years", vcc=TEN, link=MCHP + "AT28C256",
      lifecycle="Active", rohs="Yes", temp=(-40, 85),
      write="5V-only, 64-byte page write, 10ms, DATA polling and toggle bit, "
            "software data protection",
      grades=[("AT28C256-15PU", 150, None)], kw=["AT28C256", "28C256", "62256", "retro"]),
]


def org(words):
    return f"{words // 1024}Kx8"


def records():
    for chip in CHIPS:
        o = org(chip["words"])
        modern = chip.get("lifecycle") == "Active"
        tmin, tmax = chip.get("temp", (0, 70))
        for mpn, ns, note in chip["grades"]:
            bits = [f"{chip['mfr']} {chip['value']} {o} {chip['tech']} parallel EEPROM",
                    f"{ns}ns"]
            vcc = note if note in (FIVE, TEN) else chip["vcc"]
            if note and note not in (FIVE, TEN):
                bits.append(note)
            if vcc:
                bits.append(vcc)
            bits.append(chip["write"])
            bits.append(chip["package"] if not modern else f"{chip['package']}, "
                        f"{tmin} to {tmax}C")
            yield row(
                created_by=CREATED_BY, manufacturer=chip["mfr"], mpn=mpn,
                value=chip["value"], memory_type="EEPROM", words=chip["words"], bits=8,
                speed=f"{ns} ns", package=chip["package"], pins=chip["pins"],
                width_in=0.6, symbol=chip["symbol"], datasheet=chip["ds"],
                description=", ".join(bits),
                keywords=chip["kw"] + ["EEPROM", "E2PROM", "parallel EEPROM", chip["tech"]]
                + ([] if modern else ["vintage"]),
                supply_rails="+5V", programming_voltage=chip["vpp"],
                cycles=chip["cycles"], years=chip["years"],
                lifecycle=chip.get("lifecycle", "Obsolete"), rohs=chip.get("rohs", "No"),
                mfr_link=chip.get("link"), temp=(tmin, tmax))


def main():
    write(OUTPUT_FILE, "parallel EEPROMs", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
