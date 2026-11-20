#!/usr/bin/env python3
"""UV EPROMs, OTP EPROMs and 5V flash for vintage and retro builds.

One classic example per chip (see plans/vintage-computer-parts.md, "Manufacturer
coverage"), one row per speed grade the datasheet lists, commercial temperature,
windowed ceramic DIP for the UV parts. Vintage parts are Obsolete; the Microchip
AT27C/SST39SF rows are the modern parts, with lifecycle from Digi-Key and Mouser.

Sources, each cut down to the chip's pages in datasheets/<mfr>/:
  - Intel 1979 Component Data Catalog: 1702A pp. 4-5..4-8 (programming 4-60..4-61,
    order form 4-56, Type B outline 2-11), 2708/2704 4-20..4-22, with the
    programming pages, the ordering rule (2-3) and the Type D outline (2-8).
  - Intel 1981 Component Data Catalog: 2732 pp. 2-7..2-10, with the 1979
    programming pages (25V on ~OE/VPP) and ordering rule.
  - Intel 1983 Memory Components Handbook: 2716 pp. 4-5..4-11 (with the 1979
    programming pages), 2732A 4-12..4-18, 2764 4-19..4-28, 27128 4-29..4-38, each
    with the Express code page (4-41) and the Type D outline (7-4). The 1981 2732A
    and 2764 sheets are PRELIMINARY, so the 1983 ones are used.
  - Intel 1984 Memory Components Handbook: 2764A pp. 4-41..4-49 and 27256 4-72..4-81
    (PRELIMINARY on every page, the best sheet available), with the Type D outline
    (7-3). Its 27128A page is advance information only (no VPP or grades), and no
    book up to 1984 has the 27512, so neither is generated.
  - TI 1982 MOS Memory Data Book (LCC7061): TMS2516 pp. 137-144, TMS2532 145-151,
    TMS2716 167-171, each with the numbering key (257) and the 600-mil cerpak
    outline (260).
  - Motorola 1980 Memory Data Book: MCM68764 pp. 2-148..2-152, with the Part Number
    Guide (1-12) and the Case 623A/716 outlines (6-10, 6-12).
  - AMD 8-Bit EPROM Family (Am2764A, Am27128A, Am27256, Am27512), publication
    08005 Rev. A, May 1986, pp. 6-15..6-30 (scanned copy).
  - SGS-Thomson NMOS M27128A and M27512 datasheets (both NOT FOR NEW DESIGN).
  - ST datasheets (ST no longer hosts them; copies from Digi-Key): M27C64A (2006),
    M27C256B, M27C512, M27C1001, M27C2001 (2006), M27C4001, M27C801.
  - Microchip: AT27C256R (DS20006674A), AT27C512R (DS20006752), AT27C010 (0321N),
    AT27C020 (0570H), AT27C040 (0189), SST39SF010A/020A/040 (DS20005022F).

Ordering codes:
  - Intel prints no ordering table for commercial EPROMs. The codes follow the
    catalog's rule (1979 p. 2-3: package prefix + device + grade): D (Type D
    windowed CERDIP) for the 2704/2708 and later, B (Type B ceramic, transparent
    lid) for the 1702A, the only letter the order form (p. 4-56) prints for it.
  - TI's 1982 sheet titles print the full codes (TMS 2516-25 JL ...).
  - Motorola's selector guide (1980 p. 1-5) prints the C (frit-seal cerdip) codes;
    the side-braze L codes come only from a rule and are not generated.
  - AMD prints its valid combinations (p. 6-18); DC = ceramic DIP, 0 to 70 C. The
    sheet gives no package outline; the 28-pin ceramic DIP is taken as 0.6".
  - The ST NMOS M27128A/M27512 schemes list every speed/VCC-tolerance code, so only
    F (FDIP28W) and 1 (0 to 70 C) are added.
  - ST's M27C sheets print an ordering scheme, not a list. Codes are built from it: windowed
    FDIP (F), 0 to 70 C (1), VCC +/-10% (no X), one per speed column in the read
    AC tables. The "High Speed" columns (measured under different AC conditions)
    are left out.
  - Microchip prints its codes: the PDIP ones (-PU, -PHE) are used.

Symbols: stock Memory_EPROM where the pinout matches (2764/27128/27256/27512 and
27C64-27C080); custom DIP symbols in terra_symbols_ic_memory for the 24-pin parts
and the SST39SF flash (pin tables in _pinouts.py).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _memory import row, write

OUTPUT_FILE = Path(__file__).with_name("ic_memory_generated_330_eprom.sql")
CREATED_BY = Path(__file__).name
LIB = "terra_symbols_ic_memory"
NXP_OBSOLETE = "https://www.nxp.com/support/sample-and-buy/obsolete-products:WTOBUY_OBSOL"
MCHP = "https://www.microchip.com/en-us/product/"

WIN24, WIN28, WIN32 = "CERDIP-24 windowed", "CERDIP-28 windowed", "CERDIP-32 windowed"
TEN = "VCC +/-10%"


def C(**kw):
    return kw


# Each chip: grades as (ordering code, access time ns, grade note or None).
CHIPS = [
    # ---- Intel -------------------------------------------------------------------
    C(mfr="Intel", value="1702A", words=256, pins=24, package="ceramic DIP-24 windowed",
      symbol=f"{LIB}:1702A", ds="intel/1702a-256x8-uv-eprom.pdf", tech="silicon-gate",
      rails="+5V, -9V", vpp="-48V",
      note="VDD/VGG -9V, programmed with -48V pulses; erased state is all 0s",
      grades=[("B1702A-2", 650, None), ("B1702A", 1000, None), ("B1702A-6", 1500, None)],
      kw=["1702", "B1702A"]),
    C(mfr="Intel", value="2708", words=1024, pins=24, package=WIN24,
      symbol=f"{LIB}:2708", ds="intel/2708-2704-1kx8-512x8-uv-eprom.pdf", tech="NMOS",
      rails="+12V, +5V, -5V", vpp="26V",
      note="apply VBB (-5V) first and remove it last; PROGRAM (pin 18) grounded in read",
      grades=[("D2708-1", 350, None), ("D2708", 450, None),
              ("D2708L", 450, "low power, VCC/VDD +/-10%")],
      kw=["2708", "D2708", "TMS2708", "MCM2708"]),
    C(mfr="Intel", value="2704", words=512, pins=24, package=WIN24,
      symbol=f"{LIB}:2708", ds="intel/2708-2704-1kx8-512x8-uv-eprom.pdf", tech="NMOS",
      rails="+12V, +5V, -5V", vpp="26V",
      note="2708 pinout with pin 22 (A9) tied to VSS; apply VBB (-5V) first",
      grades=[("D2704", 450, None)], kw=["2704", "2708"]),
    C(mfr="Intel", value="2716", words=2048, pins=24, package=WIN24,
      symbol=f"{LIB}:2716", ds="intel/2716-2kx8-uv-eprom.pdf", tech="NMOS",
      rails="+5V", vpp="25V",
      note="VPP 25V on pin 21, active-high program pulse on ~CE; not the TMS2716 pinout",
      grades=[("D2716-1", 350, "VCC +/-10%"), ("D2716-2", 390, None), ("D2716", 450, None),
              ("D2716-5", 490, "490ns from ~CE, 450ns from address"),
              ("D2716-6", 650, "650ns from ~CE, 450ns from address")],
      kw=["2716", "D2716", "TMS2516", "MCM2716", "TMM323"]),
    C(mfr="Intel", value="2732", words=4096, pins=24, package=WIN24,
      symbol=f"{LIB}:2732", ds="intel/2732-4kx8-uv-eprom.pdf", tech="NMOS",
      rails="+5V", vpp="25V",
      note="25V on ~OE/VPP (pin 20); pin-identical to the 21V 2732A, so check VPP",
      grades=[("D2732-4", 390, None), ("D2732", 450, None), ("D2732-6", 550, None)],
      kw=["2732", "D2732"]),
    C(mfr="Intel", value="2732A", words=4096, pins=24, package=WIN24,
      symbol=f"{LIB}:2732", ds="intel/2732a-4kx8-uv-eprom.pdf", tech="HMOS-E",
      rails="+5V", vpp="21V",
      note="21V on ~OE/VPP (pin 20); over 22V destroys it, so never program as a 2732",
      grades=[("D2732A-2", 200, None), ("D2732A", 250, None), ("D2732A-3", 300, None),
              ("D2732A-4", 450, None), ("D2732A-20", 200, "VCC +/-10%"),
              ("D2732A-25", 250, "VCC +/-10%"), ("D2732A-30", 300, "VCC +/-10%")],
      kw=["2732A", "2732"]),
    C(mfr="Intel", value="2764", words=8192, pins=28, package=WIN28,
      symbol="Memory_EPROM:2764", ds="intel/2764-8kx8-uv-eprom.pdf", tech="HMOS",
      rails="+5V", vpp="21V",
      note="21V on VPP (pin 1); over 22V destroys it; the 2764A programs at 12.5V",
      grades=[("D2764-2", 200, None), ("D2764", 250, None), ("D2764-3", 300, None),
              ("D2764-4", 450, None), ("D2764-25", 250, "VCC +/-10%"),
              ("D2764-30", 300, "VCC +/-10%"), ("D2764-45", 450, "VCC +/-10%")],
      kw=["2764", "27C64"]),
    C(mfr="Intel", value="2764A", words=8192, pins=28, package=WIN28,
      symbol="Memory_EPROM:2764", ds="intel/2764a-8kx8-uv-eprom.pdf", tech="HMOS II-E",
      rails="+5V", vpp="12.5V",
      note="12.5V on VPP (pin 1); over 14V destroys it, so never program as a 21V 2764",
      grades=[("D2764A-1", 180, None), ("D2764A-2", 200, None), ("D2764A", 250, None),
              ("D2764A-3", 300, None), ("D2764A-4", 450, None),
              ("D2764A-20", 200, "VCC +/-10%"), ("D2764A-25", 250, "VCC +/-10%"),
              ("D2764A-30", 300, "VCC +/-10%"), ("D2764A-45", 450, "VCC +/-10%")],
      kw=["2764A", "2764", "27C64"]),
    C(mfr="Intel", value="27128", words=16384, pins=28, package=WIN28,
      symbol="Memory_EPROM:27128", ds="intel/27128-16kx8-uv-eprom.pdf", tech="HMOS",
      rails="+5V", vpp="21V", note="21V on VPP (pin 1); over 22V destroys it",
      grades=[("D27128", 250, None), ("D27128-3", 300, None), ("D27128-4", 450, None),
              ("D27128-25", 250, "VCC +/-10%"), ("D27128-30", 300, "VCC +/-10%"),
              ("D27128-45", 450, "VCC +/-10%")],
      kw=["27128", "27C128"]),
    C(mfr="Intel", value="27256", words=32768, pins=28, package=WIN28,
      symbol="Memory_EPROM:27256", ds="intel/27256-32kx8-uv-eprom.pdf", tech="HMOS II-E",
      rails="+5V", vpp="12.5V",
      note="12.5V on VPP (pin 1), over 14V destroys it; from the 1984 PRELIMINARY sheet",
      grades=[("D27256", 250, None), ("D27256-3", 300, None), ("D27256-4", 450, None),
              ("D27256-25", 250, "VCC +/-10%"), ("D27256-30", 300, "VCC +/-10%"),
              ("D27256-45", 450, "VCC +/-10%")],
      kw=["27256", "27C256"]),
    # ---- Texas Instruments --------------------------------------------------------
    C(mfr="Texas Instruments", value="TMS2716", words=2048, pins=24, package=WIN24,
      symbol=f"{LIB}:TMS2716", ds="ti/tms2716-2kx8-uv-eprom.pdf", tech="NMOS",
      rails="+12V, +5V, -5V", vpp="26V",
      note="three-supply TI pinout, not the Intel 2716 (VDD on pin 19, VBB on pin 21)",
      grades=[("TMS2716-30JL", 300, None), ("TMS2716-45JL", 450, None)],
      kw=["TMS2716", "MCM2716 (TI pinout)"]),
    C(mfr="Texas Instruments", value="TMS2516", words=2048, pins=24, package=WIN24,
      symbol=f"{LIB}:2716", ds="ti/tms2516-2kx8-uv-eprom.pdf", tech="NMOS",
      rails="+5V", vpp="25V", note="Intel 2716 pinout and programming (VPP 25V on pin 21)",
      grades=[("TMS2516-25JL", 250, None), ("TMS2516-35JL", 350, None),
              ("TMS2516-45JL", 450, None)],
      kw=["2516", "2716"]),
    C(mfr="Texas Instruments", value="TMS2532", words=4096, pins=24, package=WIN24,
      symbol=f"{LIB}:TMS2532", ds="ti/tms2532-4kx8-uv-eprom.pdf", tech="NMOS",
      rails="+5V", vpp="25V",
      note="not the Intel 2732 pinout (pins 18/20/21: A11, PD/~PGM, VPP)",
      grades=[("TMS2532-30JL", 300, None), ("TMS2532-35JL", 350, None),
              ("TMS2532-45JL", 450, None)],
      kw=["2532", "MCM2532", "HN462532", "Commodore"]),
    C(mfr="Texas Instruments", value="TMS25L32", words=4096, pins=24, package=WIN24,
      symbol=f"{LIB}:TMS2532", ds="ti/tms2532-4kx8-uv-eprom.pdf", tech="NMOS",
      rails="+5V", vpp="25V",
      note="low power; not the Intel 2732 pinout (pins 18/20/21: A11, PD/~PGM, VPP)",
      grades=[("TMS25L32-45JL", 450, None)], kw=["2532", "TMS2532", "Commodore"]),
    # ---- Motorola -------------------------------------------------------------------
    C(mfr="Motorola", value="MCM68764", words=8192, pins=24, package=WIN24,
      symbol=f"{LIB}:MCM68764", ds="motorola/mcm68764-8kx8-uv-eprom.pdf", tech="NMOS",
      rails="+5V", vpp="25V", link=NXP_OBSOLETE,
      note="8K in 24 pins for 2364 mask-ROM sockets; 25V program pulse on ~E/VPP (pin 20)",
      grades=[("MCM68764C", 450, None), ("MCM68764C35", 350, "VCC +/-10%")],
      kw=["68764", "MCM68A764", "2364"]),
    C(mfr="Motorola", value="MCM68L764", words=8192, pins=24, package=WIN24,
      symbol=f"{LIB}:MCM68764", ds="motorola/mcm68764-8kx8-uv-eprom.pdf", tech="NMOS",
      rails="+5V", vpp="25V", link=NXP_OBSOLETE,
      note="low power; 8K in 24 pins for 2364 mask-ROM sockets; 25V on ~E/VPP (pin 20)",
      grades=[("MCM68L764C", 450, None), ("MCM68L764C35", 350, "VCC +/-10%")],
      kw=["68764", "MCM68764", "2364"]),
]


def amd(value, words, symbol, five, ten, kw):
    """AMD 8-bit EPROM family valid combinations, DC = ceramic DIP, 0 to 70 C."""
    grades = [(f"AM{value[2:]}{s}DC", ns, None) for s, ns in five]
    grades += [(f"AM{value[2:]}{s}DC", ns, TEN) for s, ns in ten]
    return C(mfr="AMD", value=value, words=words, pins=28, package=WIN28,
             symbol=symbol, ds="amd/am2764a-am27128a-am27256-am27512-uv-eprom.pdf",
             tech="NMOS", rails="+5V", vpp="12.5V", grades=grades, kw=kw)


# AMD 8-Bit EPROM Family, publication 08005 Rev. A (May 1986), pp. 6-15..6-30:
# product selector guide (6-15) and valid combinations (6-18).
AMD = [
    amd("Am2764A", 8192, "Memory_EPROM:2764",
        [("-1", 150), ("-2", 200), ("", 250), ("-3", 300), ("-4", 450)],
        [("-15", 150), ("-20", 200), ("-25", 250), ("-30", 300), ("-45", 450)],
        ["2764A", "2764"]),
    amd("Am27128A", 16384, "Memory_EPROM:27128",
        [("-1", 150), ("-2", 200), ("", 250), ("-3", 300), ("-4", 450)],
        [("-15", 150), ("-20", 200), ("-25", 250), ("-30", 300), ("-45", 450)],
        ["27128A", "27128"]),
    amd("Am27256", 32768, "Memory_EPROM:27256",
        [("-1", 170), ("-2", 200), ("", 250), ("-3", 300), ("-4", 450)],
        [("-17", 170), ("-20", 200), ("-25", 250), ("-30", 300), ("-45", 450)],
        ["27256"]),
    amd("Am27512", 65536, "Memory_EPROM:27512",
        [("", 250), ("-3", 300), ("-4", 450)],
        [("-25", 250), ("-30", 300), ("-45", 450)],
        ["27512"]),
]


def st(value, words, pins, symbol, ds, vpp, speeds, kw, tech="CMOS", note=None):
    """ST windowed-FDIP, 0-70 C codes, one per speed: (suffix, ns[, note])."""
    grades = [(f"{value}{s[0]}F1", s[1], s[2] if len(s) > 2 else None) for s in speeds]
    return C(mfr="STMicroelectronics", value=value, words=words, pins=pins,
             package={28: WIN28, 32: WIN32}[pins], symbol=symbol, ds=ds, tech=tech,
             rails="+5V", vpp=vpp, grades=grades, kw=kw, note=note)


ST = [
    # SGS-Thomson NMOS parts, already "NOT FOR NEW DESIGN" in these sheets. Their
    # ordering schemes list every speed/VCC-tolerance code.
    st("M27128A", 16384, 28, "Memory_EPROM:27128", "st/m27128a-16kx8-uv-eprom.pdf",
       "12.5V",
       [("-2", 200), ("", 250), ("-3", 300), ("-4", 450), ("-20", 200, TEN),
        ("-25", 250, TEN), ("-30", 300, TEN)],
       ["27128A", "27128"], tech="NMOS"),
    st("M27512", 65536, 28, "Memory_EPROM:27512", "st/m27512-64kx8-uv-eprom.pdf",
       "12.5V",
       [("-2", 200), ("", 250), ("-3", 300), ("-20", 200, TEN), ("-25", 250, TEN)],
       ["27512"], tech="NMOS",
       note="12.5V fast or 12.75V PRESTO programming on ~G/VPP (pin 22)"),
    st("M27C64A", 8192, 28, "Memory_EPROM:27C64", "st/m27c64a-8kx8-uv-eprom.pdf", "12.5V",
       [("-10", 100), ("-15", 150), ("-20", 200), ("-25", 250), ("-30", 300)],
       ["27C64", "2764"]),
    st("M27C256B", 32768, 28, "Memory_EPROM:27C256", "st/m27c256b-32kx8-uv-eprom.pdf",
       "12.75V",
       [("-60", 60), ("-70", 70), ("-80", 80), ("-90", 90), ("-10", 100), ("-12", 120),
        ("-15", 150), ("-20", 200), ("-25", 250)],
       ["27C256", "27256"]),
    st("M27C512", 65536, 28, "Memory_EPROM:27C512", "st/m27c512-64kx8-uv-eprom.pdf",
       "12.75V",
       [("-70", 70), ("-90", 90), ("-10", 100), ("-12", 120), ("-15", 150)],
       ["27C512", "27512"]),
    st("M27C1001", 131072, 32, "Memory_EPROM:27C010", "st/m27c1001-128kx8-uv-eprom.pdf",
       "12.75V",
       [("-45", 45), ("-60", 60), ("-70", 70), ("-80", 80), ("-90", 90), ("-10", 100)],
       ["27C1001", "27C010"]),
    st("M27C2001", 262144, 32, "Memory_EPROM:27C020", "st/m27c2001-256kx8-uv-eprom.pdf",
       "12.75V",
       [("-70", 70), ("-80", 80), ("-90", 90), ("-10", 100), ("-12", 120), ("-15", 150),
        ("-20", 200), ("-25", 250)],
       ["27C2001", "27C020"]),
    st("M27C4001", 524288, 32, "Memory_EPROM:27C040", "st/m27c4001-512kx8-uv-eprom.pdf",
       "12.75V",
       [("-70", 70), ("-80", 80), ("-90", 90), ("-10", 100), ("-12", 120), ("-15", 150)],
       ["27C4001", "27C040"]),
    st("M27C801", 1048576, 32, "Memory_EPROM:27C080", "st/m27c801-1mx8-uv-eprom.pdf",
       "12.75V", [("-80", 80), ("-90", 90), ("-100", 100)],
       ["27C801", "27C080"]),
]

# Modern parts: (value, words, pins, symbol, datasheet, [(mpn, ns, lifecycle)], kw).
ATMEL_OTP = [
    ("AT27C256R", 32768, 28, "Memory_EPROM:27C256", "at27c256r-32kx8-otp-eprom.pdf",
     [("AT27C256R-45PU", 45, "Active"), ("AT27C256R-70PU", 70, "Active")],
     ["27C256", "27256"]),
    ("AT27C512R", 65536, 28, "Memory_EPROM:27C512", "at27c512r-64kx8-otp-eprom.pdf",
     [("AT27C512R-45PU", 45, "Active"), ("AT27C512R-70PU", 70, "Active")],
     ["27C512", "27512"]),
    ("AT27C010", 131072, 32, "Memory_EPROM:27C010", "at27c010-128kx8-otp-eprom.pdf",
     [("AT27C010-70PU", 70, "Obsolete")], ["27C010", "27C1001"]),
    ("AT27C020", 262144, 32, "Memory_EPROM:27C020", "at27c020-256kx8-otp-eprom.pdf",
     [("AT27C020-55PU", 55, "Obsolete"), ("AT27C020-90PU", 90, "Obsolete")],
     ["27C020", "27C2001"]),
    ("AT27C040", 524288, 32, "Memory_EPROM:27C040", "at27c040-512kx8-otp-eprom.pdf",
     [("AT27C040-70PU", 70, "Obsolete"), ("AT27C040-90PU", 90, "Obsolete")],
     ["27C040", "27C4001"]),
]
SST = [
    ("SST39SF010A", 131072, "SST39SF010A-70-4C-PHE", ["27C010"]),
    ("SST39SF020A", 262144, "SST39SF020A-70-4C-PHE", ["27C020"]),
    ("SST39SF040", 524288, "SST39SF040-70-4C-PHE", ["27C040"]),
]


def org(words):
    return f"{words // 1024}Kx8" if words >= 1024 else f"{words}x8"


def records():
    for chip in CHIPS + AMD + ST:
        o = org(chip["words"])
        for mpn, ns, note in chip["grades"]:
            speed = f"{ns}ns" if ns < 1000 else f"{ns / 1000:g}us"
            bits = [f"{chip['mfr']} {chip['value']} {o} {chip['tech']} UV EPROM",
                    speed]
            if note:
                bits.append(note)
            if chip["rails"] != "+5V":
                bits.append(chip["rails"].replace(", ", "/"))
            bits.append(f"VPP {chip['vpp']}")
            if chip.get("note"):
                bits.append(chip["note"])
            bits.append(chip["package"])
            vintage = chip["mfr"] != "STMicroelectronics" or chip["tech"] == "NMOS"
            yield row(
                created_by=CREATED_BY, manufacturer=chip["mfr"], mpn=mpn,
                value=chip["value"], memory_type="EPROM", words=chip["words"], bits=8,
                speed=f"{ns} ns", package=chip["package"], pins=chip["pins"],
                width_in=0.6, symbol=chip["symbol"], datasheet=chip["ds"],
                description=", ".join(bits),
                keywords=chip["kw"] + ["EPROM", "UV EPROM", chip["tech"]]
                + (["vintage"] if vintage else ["retro"]),
                supply_rails=chip["rails"], programming_voltage=chip["vpp"],
                mfr_link=chip.get("link"))
    for value, words, pins, symbol, ds, codes, kw in ATMEL_OTP:
        o = org(words)
        for mpn, ns, life in codes:
            desc = (f"Microchip (Atmel) {value} {o} CMOS one-time-programmable EPROM, "
                    f"{ns}ns, VPP 13V, -40 to 85C, PDIP-{pins}")
            yield row(
                created_by=CREATED_BY, manufacturer="Microchip", mpn=mpn, value=value,
                memory_type="OTP EPROM", words=words, bits=8, speed=f"{ns} ns",
                package=f"PDIP-{pins}", pins=pins, width_in=0.6, symbol=symbol,
                datasheet=f"microchip/{ds}", description=desc,
                keywords=kw + ["OTP", "EPROM", "CMOS", "retro"], supply_rails="+5V",
                programming_voltage="13V", lifecycle=life, rohs="Yes",
                mfr_link=MCHP + value, temp=(-40, 85), locator_type="otp-eprom")
    for value, words, mpn, kw in SST:
        o = org(words)
        desc = (f"Microchip (SST) {value} {o} 5V multi-purpose flash, 70ns, "
                f"4KB sectors, 10K cycles min, reads in {kw[0]} EPROM sockets, PDIP-32")
        yield row(
            created_by=CREATED_BY, manufacturer="Microchip", mpn=mpn, value=value,
            memory_type="flash", words=words, bits=8, speed="70 ns", package="PDIP-32",
            pins=32, width_in=0.6, symbol=f"{LIB}:{value}",
            datasheet="microchip/sst39sf010a-sst39sf020a-sst39sf040-flash.pdf",
            description=desc, keywords=kw + ["flash", "SST39SF", "39SF", "retro"],
            supply_rails="+5V", lifecycle="Obsolete", rohs="Yes", mfr_link=MCHP + value,
            cycles="10K", years="100 years")


def main():
    write(OUTPUT_FILE, "UV EPROMs, OTP EPROMs and 5V flash", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
