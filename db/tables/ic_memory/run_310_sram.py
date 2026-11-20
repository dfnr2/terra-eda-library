#!/usr/bin/env python3
"""Vintage and retro-build static RAMs: Intel, Motorola, TI, RCA, Hitachi, Alliance.

One classic example per chip (see plans/vintage-computer-parts.md, "Manufacturer
coverage"), one row per speed/power grade the classic datasheet lists, commercial
temperature, plastic DIP. Vintage parts are Obsolete; the Alliance AS6C parts are the
in-production drop-ins.

Sources, each cut down to the chip's pages in datasheets/<mfr>/:
  - Intel 1979 Component Data Catalog: 2101A pp. 3-4..3-7, 2102A 3-8..3-11,
    2111A 3-45..3-48, 2112A 3-49..3-53, 2114 3-54..3-57, 2147 3-99..3-104,
    5101 3-111..3-114. Intel 1981 Component Data Catalog: 2114A pp. 1-2..1-5.
  - Motorola 1979 Memory Data Book: MCM6810 pp. 2-74..2-77.
  - TI 1981 Bipolar Microcomputer Components Data Book (3rd ed.): SN7489
    pp. 2-41..2-44, SN74S189A pp. 2-49..2-52.
  - RCA 1982 CMOS Microprocessors, Memories and Peripherals: CDP1822 pp. 134-140,
    CDP1824 pp. 147-152.
  - Hitachi: see HITACHI below.
  - Alliance Memory current datasheets; AS6C6264/AS6C62256 discontinuation notices
    PDN#301020261/PDN#301020262 (30-Oct-2026, last-time buy 30-Apr-2027).

Ordering codes:
  - Intel's sections give a speed/power grade table but no ordering table. The
    codes are the catalog's own rule (1979 p. 2-3, example "P5101L"): package
    prefix + grade, P = plastic. The datasheets name plastic packaging for the 2101A,
    2111A, 2112A, 2114 and 2102AL; the 2102A, 2114A and 2147 sections name no package
    material, and P is assumed for them.
  - Motorola's table prints the codes as MC6810P / MC68A10P / MC68B10P (the device
    is titled MCM6810); the codes are kept exactly as printed.
  - TI and RCA sheets name their packages (TI "J OR N", RCA D/E) rather than
    printing a table; N and E are their plastic packages. RCA's plastic parts are
    rated -40 to 85 C; there is no commercial-only grade.

Symbols: custom DIP symbols in terra_symbols_ic_memory (pin tables in _pinouts.py,
written by tools/make_dip_symbol.py), stock Memory_RAM symbols for the JEDEC
byte-wide parts.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _memory import org, row, write

OUTPUT_FILE = Path(__file__).with_name("ic_memory_generated_310_sram.sql")
CREATED_BY = Path(__file__).name
LIB = "terra_symbols_ic_memory"
# Signetics, Motorola and Philips semiconductor lines all ended up at NXP, whose
# obsolete-products page routes to authorized EOL resellers.
NXP_OBSOLETE = "https://www.nxp.com/support/sample-and-buy/obsolete-products:WTOBUY_OBSOL"


def C(**kw):
    return kw


# Each chip: its grades as (ordering code, access time ns, grade note).
CHIPS = [
    # ---- Intel -------------------------------------------------------------------
    C(mfr="Intel", value="2101A", words=256, bits=4, pins=22, width=0.4,
      symbol=f"{LIB}:2101A", ds="intel/2101a-256x4-static-ram.pdf", tech="NMOS",
      io="separate I/O, output disable", rails="+5V",
      grades=[("P2101A-2", 250, None), ("P2101A", 350, None), ("P2101A-4", 450, None)],
      kw=["8101A"]),
    C(mfr="Intel", value="2102A", words=1024, bits=1, pins=16, width=0.3,
      symbol=f"{LIB}:2102A", ds="intel/2102a-1kx1-static-ram.pdf", tech="NMOS",
      io="separate data in/out", rails="+5V",
      grades=[("P2102A-2", 250, None), ("P2102A", 350, None), ("P2102A-4", 450, None),
              ("P2102AL-2", 250, "low power, 1.5V standby"),
              ("P2102AL", 350, "low power, 1.5V standby"),
              ("P2102AL-4", 450, "low power, 1.5V standby")],
      kw=["2102", "8102A", "Altair"]),
    C(mfr="Intel", value="2111A", words=256, bits=4, pins=18, width=0.3,
      symbol=f"{LIB}:2111A", ds="intel/2111a-256x4-static-ram.pdf", tech="NMOS",
      io="common I/O, output disable", rails="+5V",
      grades=[("P2111A-2", 250, None), ("P2111A", 350, None), ("P2111A-4", 450, None)],
      kw=["2111", "8111A"]),
    C(mfr="Intel", value="2112A", words=256, bits=4, pins=16, width=0.3,
      symbol=f"{LIB}:2112A", ds="intel/2112a-256x4-static-ram.pdf", tech="NMOS",
      io="common I/O", rails="+5V",
      grades=[("P2112A-2", 250, None), ("P2112A", 350, None), ("P2112A-4", 450, None)],
      kw=["2112"]),
    C(mfr="Intel", value="2114", words=1024, bits=4, pins=18, width=0.3,
      symbol=f"{LIB}:2114", ds="intel/2114-1kx4-static-ram.pdf", tech="NMOS",
      io="common I/O", rails="+5V",
      grades=[("P2114-2", 200, None), ("P2114-3", 300, None), ("P2114", 450, None),
              ("P2114L2", 200, "low power"), ("P2114L3", 300, "low power"),
              ("P2114L", 450, "low power")],
      kw=["2114L"]),
    C(mfr="Intel", value="2114A", words=1024, bits=4, pins=18, width=0.3,
      symbol=f"{LIB}:2114", ds="intel/2114a-1kx4-static-ram.pdf", tech="HMOS",
      io="common I/O", rails="+5V",
      grades=[("P2114AL-1", 100, "low power"), ("P2114AL-2", 120, "low power"),
              ("P2114AL-3", 150, "low power"), ("P2114AL-4", 200, "low power"),
              ("P2114A-4", 200, None), ("P2114A-5", 250, None)],
      kw=["2114", "2114AL"]),
    C(mfr="Intel", value="2147", words=4096, bits=1, pins=18, width=0.3,
      symbol=f"{LIB}:2147", ds="intel/2147-4kx1-static-ram.pdf", tech="HMOS",
      io="separate data in/out, automatic power-down", rails="+5V",
      grades=[("P2147-3", 55, None), ("P2147", 70, None), ("P2147L", 70, "low power")],
      kw=["2147L"]),
    C(mfr="Intel", value="5101", words=256, bits=4, pins=22, width=0.4,
      symbol=f"{LIB}:2101A", ds="intel/5101-256x4-cmos-static-ram.pdf", tech="CMOS",
      io="separate I/O, output disable, 2V data retention", rails="+5V",
      grades=[("P5101L", 650, "low power"), ("P5101L-1", 450, "low power"),
              ("P5101L-3", 650, "low power")],
      kw=["5101L", "battery backup", "2101A pinout"]),
    # ---- Motorola -------------------------------------------------------------------
    C(mfr="Motorola", value="MCM6810", words=128, bits=8, pins=24, width=0.6,
      symbol=f"{LIB}:MCM6810", ds="motorola/mcm6810-128x8-static-ram.pdf", tech="NMOS",
      io="common I/O, six chip selects", rails="+5V", link=NXP_OBSOLETE,
      grades=[("MC6810P", 450, "1.0 MHz"), ("MC68A10P", 360, "1.5 MHz"),
              ("MC68B10P", 250, "2.0 MHz")],
      kw=["MCM68A10", "MCM68B10", "6800", "6810"]),
    # ---- Texas Instruments ------------------------------------------------------
    C(mfr="Texas Instruments", value="7489", words=16, bits=4, pins=16, width=0.3,
      symbol=f"{LIB}:7489", ds="ti/sn7489-16x4-ttl-ram.pdf", tech="TTL",
      io="separate open-collector outputs, inverted data", rails="+5V",
      grades=[("SN7489N", 60, None)], kw=["SN7489", "scratchpad"]),
    C(mfr="Texas Instruments", value="74S189A", words=16, bits=4, pins=16, width=0.3,
      symbol=f"{LIB}:74S189A", ds="ti/sn74s189a-sn74s289a-16x4-ttl-ram.pdf",
      tech="Schottky TTL", io="separate 3-state outputs, inverted data", rails="+5V",
      grades=[("SN74S189AN", 35, None)], kw=["74S189", "SN74S189", "scratchpad"]),
    # ---- RCA ------------------------------------------------------------------------
    C(mfr="RCA", value="CDP1822", words=256, bits=4, pins=22, width=0.4,
      symbol=f"{LIB}:2101A", ds="rca/cdp1822-256x4-cmos-static-ram.pdf", tech="CMOS",
      io="separate I/O, output disable", temp=(-40, 85),
      grades=[("CDP1822E", 450, "4 to 10.5V", "+4V to +10.5V"),
              ("CDP1822CE", 450, "4 to 6.5V", "+4V to +6.5V")],
      kw=["1822", "1802", "COSMAC", "5101 pinout"]),
    C(mfr="RCA", value="CDP1824", words=32, bits=8, pins=18, width=0.3,
      symbol=f"{LIB}:CDP1824", ds="rca/cdp1824-32x8-cmos-static-ram.pdf", tech="CMOS",
      io="common I/O", temp=(-40, 85),
      grades=[("CDP1824E", 710, "4 to 10.5V", "+4V to +10.5V"),
              ("CDP1824CE", 710, "4 to 6.5V", "+4V to +6.5V")],
      kw=["1824", "1802", "COSMAC"]),
    # ---- Alliance Memory (modern drop-ins) ---------------------------------------
    C(mfr="Alliance Memory", value="AS6C6264", words=8192, bits=8, pins=28, width=0.6,
      symbol="Memory_RAM:HY6264AxP", ds="alliance/as6c6264-8kx8-cmos-sram.pdf",
      tech="CMOS", io="common I/O, 6264 pinout", rails="+2.7V to +5.5V",
      lifecycle="EOL", rohs="Yes", link="https://www.alliancememory.com/product/eol-lpsram/",
      note="discontinued (PDN#301020261, last-time buy 30-Apr-2027)",
      grades=[("AS6C6264-55PCN", 55, None)], kw=["6264", "HM6264"]),
    C(mfr="Alliance Memory", value="AS6C62256", words=32768, bits=8, pins=28, width=0.6,
      symbol="Memory_RAM:HM62256BLP", ds="alliance/as6c62256-32kx8-cmos-sram.pdf",
      tech="CMOS", io="common I/O, 62256 pinout", rails="+2.7V to +5.5V",
      lifecycle="EOL", rohs="Yes", link="https://www.alliancememory.com/product/eol-lpsram/",
      note="discontinued (PDN#301020262, last-time buy 30-Apr-2027)",
      grades=[("AS6C62256-55PCN", 55, None)], kw=["62256", "HM62256"]),
    C(mfr="Alliance Memory", value="AS6C1008", words=131072, bits=8, pins=32, width=0.6,
      symbol="Memory_RAM:AS6C1008-xxP", ds="alliance/as6c1008-128kx8-cmos-sram.pdf",
      tech="CMOS", io="common I/O, 628128 pinout", rails="+2.7V to +5.5V",
      lifecycle="Active", rohs="Yes", link="https://www.alliancememory.com/as6c1008/",
      grades=[("AS6C1008-55PCN", 55, None)], kw=["628128", "HM628128"]),
    C(mfr="Alliance Memory", value="AS6C4008", words=524288, bits=8, pins=32, width=0.6,
      symbol="Memory_RAM:AS6C4008-55PCN", ds="alliance/as6c4008-512kx8-cmos-sram.pdf",
      tech="CMOS", io="common I/O", rails="+2.7V to +5.5V",
      lifecycle="Active", rohs="Yes", link="https://www.alliancememory.com/as6c4008/",
      grades=[("AS6C4008-55PCN", 55, None)], kw=["628512", "4 Mbit"]),
]

# Hitachi CMOS byte-wide RAMs, 600 mil plastic DIP, each from the earliest data book
# that carries it: HM6116 and HM6264 from the IC Memory Data Book (Mar 1984,
# pp. 65-105 and 166-187), HM62256 from IC Memories Data Book M11 (1987,
# pp. 232-245), HM628128 from SRAM Data Book M18 (1990, pp. 261-268). L parts
# retain data down to 2.0V. Left out: the 0.3in skinny HM6116ASP/ALSP, ceramic and
# SOP packages, and the HM62256 SL grades the 1987 book marks preliminary.
LP = "low power, 2V data retention"
HITACHI = [
    C(mfr="Hitachi", value="HM6116", words=2048, bits=8, pins=24, width=0.6,
      symbol=f"{LIB}:HM6116", ds="hitachi/hm6116-2kx8-cmos-static-ram.pdf",
      tech="CMOS", io="common I/O, 2716-compatible pinout", rails="+5V",
      grades=[("HM6116P-2", 120, None), ("HM6116P-3", 150, None),
              ("HM6116P-4", 200, None),
              ("HM6116LP-2", 120, LP), ("HM6116LP-3", 150, LP), ("HM6116LP-4", 200, LP),
              ("HM6116AP-12", 120, "A version"), ("HM6116AP-15", 150, "A version"),
              ("HM6116AP-20", 200, "A version"),
              ("HM6116ALP-12", 120, f"A version, {LP}"),
              ("HM6116ALP-15", 150, f"A version, {LP}"),
              ("HM6116ALP-20", 200, f"A version, {LP}")],
      kw=["6116", "HM6116LP", "HM6116A"]),
    C(mfr="Hitachi", value="HM6264", words=8192, bits=8, pins=28, width=0.6,
      symbol="Memory_RAM:HY6264AxP", ds="hitachi/hm6264-8kx8-cmos-static-ram.pdf",
      tech="CMOS", io="common I/O, JEDEC 6264 pinout", rails="+5V",
      grades=[("HM6264P-10", 100, None), ("HM6264P-12", 120, None),
              ("HM6264P-15", 150, None),
              ("HM6264LP-10", 100, LP), ("HM6264LP-12", 120, LP), ("HM6264LP-15", 150, LP)],
      kw=["6264", "HM6264LP"]),
    C(mfr="Hitachi", value="HM62256", words=32768, bits=8, pins=28, width=0.6,
      symbol="Memory_RAM:HM62256BLP", ds="hitachi/hm62256-32kx8-cmos-static-ram.pdf",
      tech="CMOS", io="common I/O, JEDEC 62256 pinout", rails="+5V",
      grades=[("HM62256P-8", 85, None), ("HM62256P-10", 100, None),
              ("HM62256P-12", 120, None), ("HM62256P-15", 150, None),
              ("HM62256LP-8", 85, LP), ("HM62256LP-10", 100, LP),
              ("HM62256LP-12", 120, LP), ("HM62256LP-15", 150, LP)],
      kw=["62256", "HM62256LP"]),
    C(mfr="Hitachi", value="HM628128", words=131072, bits=8, pins=32, width=0.6,
      symbol="Memory_RAM:HM628128_DIP32_SOP32",
      ds="hitachi/hm628128-128kx8-cmos-static-ram.pdf",
      tech="CMOS", io="common I/O, JEDEC 128Kx8 pinout", rails="+5V",
      grades=[("HM628128P-7", 70, None), ("HM628128P-8", 85, None),
              ("HM628128P-10", 100, None), ("HM628128P-12", 120, None),
              ("HM628128LP-7", 70, LP), ("HM628128LP-8", 85, LP),
              ("HM628128LP-10", 100, LP), ("HM628128LP-12", 120, LP)],
      kw=["628128", "HM628128LP"]),
]


def records():
    for chip in CHIPS + HITACHI:
        o = org(chip["words"], chip["bits"])
        temp = chip.get("temp", (0, 70))
        for grade in chip["grades"]:
            mpn, ns, note = grade[:3]
            rails = grade[3] if len(grade) > 3 else chip["rails"]
            package = f"PDIP-{chip['pins']}"
            if chip["width"] != 0.6 and chip["pins"] >= 22:
                package += f" {int(chip['width'] * 1000)}mil"
            bits = [f"{chip['mfr']} {chip['value']} {o} {chip['tech']} static RAM",
                    chip["io"], f"{ns}ns"]
            if note:
                bits.append(note)
            if chip.get("note"):
                bits.append(chip["note"])
            if temp != (0, 70):
                bits.append(f"{temp[0]} to {temp[1]}C")
            bits.append(package)
            vintage = chip.get("lifecycle", "Obsolete") == "Obsolete"
            yield row(
                created_by=CREATED_BY, manufacturer=chip["mfr"], mpn=mpn,
                value=chip["value"], memory_type="SRAM",
                words=chip["words"], bits=chip["bits"], speed=f"{ns} ns",
                package=package, pins=chip["pins"], width_in=chip["width"],
                symbol=chip["symbol"], datasheet=chip["ds"],
                description=", ".join(bits),
                keywords=chip["kw"] + ["SRAM", "static RAM", chip["tech"]]
                + (["vintage"] if vintage else ["retro"]),
                supply_rails=rails, lifecycle=chip.get("lifecycle", "Obsolete"),
                rohs=chip.get("rohs", "No"), mfr_link=chip.get("link"), temp=temp)


def main():
    write(OUTPUT_FILE, "vintage and retro static RAMs", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
