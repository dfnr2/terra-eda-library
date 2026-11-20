#!/usr/bin/env python3
"""Bipolar fusible-link PROMs for vintage and arcade builds.

Programmable memories get every maker's sheet rather than one classic example (see
plans/vintage-computer-parts.md, "Manufacturer coverage"): programmers and arcade
documentation name parts by any of the five big makers, and they differ in fuse type
and in whether an unprogrammed bit reads high or low. Eight organizations (32x8,
256x4, 512x4, 1Kx4, 2Kx4, 512x8 in 20 and 24 pins, 1Kx8, 2Kx8), open-collector (OC)
and 3-state (TS), one row per speed grade, commercial temperature, plastic DIP where
the book offers it, ceramic where it doesn't. All Obsolete.

Every maker uses the same pinout for a given organization, so the symbols are shared:
one OC and one TS symbol per pinout in terra_symbols_ic_memory, named after the
Signetics part (Am27S28/29 for the 20-pin 512x8 and MMI 6340/41 for the 24-pin
512x8, which have no Signetics sheet). Pin tables in _pinouts.py (_PROMS).

Sources, each cut down to the PROM pages plus the DIP outlines in datasheets/<mfr>/:
  - Signetics 1977 Bipolar and MOS Memory Data Manual: 82S23/123 pp. 89-92,
    82S126/129 101-104, 82S130/131 114-117, 82S136/137 122-125, 82S180/181 126-129,
    82S184/185 134-137, 82S190/191 138-141 (OBJECTIVE SPECIFICATION).
  - AMD 1984 Bipolar/MOS Memories Data Book: Am27S12/13 2-13..2-17, Am27S18/19
    2-24..2-28, Am27S20/21 2-29..2-33, Am27S28/29 2-46..2-50, Am27S32/33 2-56..2-60,
    Am27S181/281 family 2-122..2-127, Am27S184/185 2-128..2-133, Am27S191/291 family
    2-134..2-139, with the programming guide (2-1..2-2).
  - MMI 1981 Bipolar LSI Databook, 4th ed.: NiCr 63xx family 3-4..3-12 with the -2
    sheets (3-13..3-27) and programming (3-28..3-30); Ti-W 63S/63LS 3-31..3-40.
  - TI 1981 Bipolar Microcomputer Components Data Book: Series 14/18 2-7..2-12,
    Series 24/28 2-13..2-34.
  - National 1983 Interface/Bipolar LSI/Bipolar Memory/Programmable Logic Data Book,
    section 21 (DM74S/DM87S PROMs, programming 21-38..21-39).

Ordering codes:
  - Signetics prints no full codes; each sheet says "specify N82S23/123, N or F" (N
    prefix = commercial, suffix N = plastic). The 82S184/185 and 82S190/191 come only
    in the I ceramic package. Commercial range is 0 to 75 C.
  - AMD prints valid combinations; the PC (plastic, commercial) codes are used. The
    Am27S28x/29x are the 300-mil versions of the Am27S18x/19x (ordering note).
    Am27LS184A/185A (no timing given) and the burn-in B codes are left out.
  - MMI prints a key (6 = commercial, -1/-2 grade, J ceramic DIP, JS 0.3" ceramic,
    N plastic). The NiCr 63xx parts come in ceramic only (J, and JS for the 24-pin
    skinny versions); the Ti-W 63S/63LS parts in plastic N. Commercial is 0 to 75 C.
  - TI prints a key (S = 3-state, SA = open collector; N = plastic); the N codes are
    used. Faster -55/-60 grades (no package combination shown) and "design goals"
    parts (TBP28S85, TBP28S45, TBP28L166) are left out.
  - National prints "DM74S188 N"-style order numbers; written without the space. The
    2Kx4 and 2Kx8 sheets list packages N,J but print no order numbers, so their N
    codes are built the same way. A/B speed grades never get an order number and are
    left out.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

from _memory import row, write

OUTPUT_FILE = Path(__file__).with_name("ic_memory_generated_350_bipolar_prom.sql")
CREATED_BY = Path(__file__).name
LIB = "terra_symbols_ic_memory"
NXP_OBSOLETE = "https://www.nxp.com/support/sample-and-buy/obsolete-products:WTOBUY_OBSOL"

# Organization -> (words, bits, pins, OC symbol, TS symbol).
ORG = {
    "32x8": (32, 8, 16, "82S23", "82S123"),
    "256x4": (256, 4, 16, "82S126", "82S129"),
    "512x4": (512, 4, 16, "82S130", "82S131"),
    "1Kx4": (1024, 4, 18, "82S136", "82S137"),
    "2Kx4": (2048, 4, 18, "82S184", "82S185"),
    "512x8": (512, 8, 20, "27S28", "27S29"),
    "512x8-24": (512, 8, 24, "6340", "6341"),
    "1Kx8": (1024, 8, 24, "82S180", "82S181"),
    "2Kx8": (2048, 8, 24, "82S190", "82S191"),
}

# Maker -> (datasheet folder, commercial temperature, manufacturer link).
MAKERS = {
    "Signetics": ("signetics", (0, 75), NXP_OBSOLETE),
    "AMD": ("amd", (0, 70), None),
    "MMI": ("mmi", (0, 75), None),
    "Texas Instruments": ("ti", (0, 70), None),
    "National Semiconductor": ("national", (0, 70), None),
}

FUSE = {"Signetics": "NiCr", "AMD": "PtSi", "Texas Instruments": "Ti-W",
        "National Semiconductor": "Ti-W"}


def P(mfr, value, org, out, codes, ds, unprog, package="PDIP", width=None, fuse=None,
      note=None, kw=()):
    """One data-sheet part: codes are [(ordering code, max access ns), ...]."""
    return dict(mfr=mfr, value=value, org=org, out=out, codes=codes, ds=ds,
                unprog=unprog, package=package, width=width, fuse=fuse or FUSE.get(mfr),
                note=note, kw=list(kw))


def sig(oc, ts, org, ns, ds, kw, pkg="N", note=None):
    """Signetics OC/TS pair: N + device + package letter (N plastic, I ceramic)."""
    package = "PDIP" if pkg == "N" else "ceramic DIP"
    return [P("Signetics", v, org, out, [(f"N{v}{pkg}", ns)], ds, "low", package,
              note=note, kw=kw)
            for v, out in ((oc, "OC"), (ts, "TS"))]


def amd(oc, ts, org, grades, ds, kw, width=None):
    """AMD OC/TS pair, PC codes; grades are [(speed select, ns), ...]."""
    out = []
    for v, o in ((oc, "OC"), (ts, "TS")):
        out.append(P("AMD", f"Am{v}", org, o,
                     [(f"AM{v}{g}PC", ns) for g, ns in grades], ds, "low",
                     width=width, kw=kw))
    return out


def nat(oc, ts, org, ns, ds, kw, width=None, note=None):
    """National OC/TS pair, N (plastic) order numbers."""
    return [P("National Semiconductor", v, org, o, [(f"{v}N", ns)], ds, "low",
              width=width, note=note, kw=kw)
            for v, o in ((oc, "OC"), (ts, "TS"))]


def ti(base, org, ns_ts, ns_oc, ds, unprog, kw):
    """TI TBP pair: TBPxxS.. = 3-state, TBPxxSA.. = open collector, N = plastic."""
    ts, oc = base, base[:5] + "SA" + base[6:]  # TBP18S030 -> TBP18SA030
    return [P("Texas Instruments", ts, org, "TS", [(f"{ts}N", ns_ts)], ds, unprog, kw=kw),
            P("Texas Instruments", oc, org, "OC", [(f"{oc}N", ns_oc)], ds, unprog, kw=kw)]


def mmi(oc, ts, org, grades, ds, kw, skinny=False):
    """MMI NiCr pair, ceramic J (and JS 0.3" for 24-pin): grades {suffix: (oc, ts) ns}."""
    out = []
    for v, o, i in ((oc, "OC", 0), (ts, "TS", 1)):
        for pkg, width in (("J", None), ("JS", 0.3)) if skinny else (("J", None),):
            codes = [(f"{v}{g}{pkg}", ns[i]) for g, ns in grades.items() if ns[i]]
            out.append(P("MMI", v, org, o, codes, ds, "high", "ceramic DIP", width,
                         "NiCr", kw=kw))
    return out


SIG = "signetics/"
CHIPS = (
    # ---- Signetics 1977 ----------------------------------------------------------------
    sig("82S23", "82S123", "32x8", 50, SIG + "82s123-82s23-32x8-bipolar-prom.pdf",
        ["74S188", "74S288", "27S18", "27S19", "6330", "6331"])
    + sig("82S126", "82S129", "256x4", 50, SIG + "82s129-82s126-256x4-bipolar-prom.pdf",
          ["74S387", "74S287", "27S20", "27S21", "6300", "6301", "93417", "93427"])
    + sig("82S130", "82S131", "512x4", 50, SIG + "82s131-82s130-512x4-bipolar-prom.pdf",
          ["74S570", "74S571", "27S12", "27S13", "6305", "6306"])
    + sig("82S136", "82S137", "1Kx4", 60, SIG + "82s137-82s136-1kx4-bipolar-prom.pdf",
          ["74S572", "74S573", "27S32", "27S33", "6352", "6353"])
    + sig("82S184", "82S185", "2Kx4", 100, SIG + "82s185-82s184-2kx4-bipolar-prom.pdf",
          ["87S184", "87S185", "27S184", "27S185"], pkg="I")
    + sig("82S180", "82S181", "1Kx8", 70, SIG + "82s181-82s180-1kx8-bipolar-prom.pdf",
          ["87S180", "87S181", "27S180", "27S181", "6380", "6381"])
    + sig("82S190", "82S191", "2Kx8", 80, SIG + "82s191-82s190-2kx8-bipolar-prom.pdf",
          ["87S190", "87S191", "27S190", "27S191"], pkg="I",
          note="from an OBJECTIVE SPECIFICATION sheet")
    # ---- AMD 1984 ----------------------------------------------------------------------
    + amd("27S18", "27S19", "32x8", [("SA", 15), ("A", 25), ("", 40)],
          "amd/am27s18-am27s19-32x8-bipolar-prom.pdf", ["82S23", "82S123", "74S288"])
    + [P("AMD", f"Am27LS{n}", "32x8", o, [(f"AM27LS{n}PC", 55)],
         "amd/am27s18-am27s19-32x8-bipolar-prom.pdf", "low", note="low power",
         kw=["27S18", "27S19", "82S123"]) for n, o in (("18", "OC"), ("19", "TS"))]
    + amd("27S20", "27S21", "256x4", [("A", 30), ("", 45)],
          "amd/am27s20-am27s21-256x4-bipolar-prom.pdf", ["82S126", "82S129", "74S287"])
    + amd("27S12", "27S13", "512x4", [("A", 30), ("", 50)],
          "amd/am27s12-am27s13-512x4-bipolar-prom.pdf", ["82S130", "82S131", "74S571"])
    + amd("27S32", "27S33", "1Kx4", [("A", 35), ("", 55)],
          "amd/am27s32-am27s33-1kx4-bipolar-prom.pdf", ["82S136", "82S137", "74S573"])
    + amd("27S184", "27S185", "2Kx4", [("A", 35), ("", 50)],
          "amd/am27s184-am27s185-2kx4-bipolar-prom.pdf", ["82S184", "82S185", "87S185"])
    + [P("AMD", "Am27PS185", "2Kx4", "TS", [("AM27PS185PC", 50)],
         "amd/am27s184-am27s185-2kx4-bipolar-prom.pdf", "low",
         note="power-switched (low standby power when deselected)",
         kw=["27S185", "82S185"])]
    + [P("AMD", f"Am27LS{n}", "2Kx4", o, [(f"AM27LS{n}PC", 60)],
         "amd/am27s184-am27s185-2kx4-bipolar-prom.pdf", "low", note="low power",
         kw=["27S184", "27S185", "82S185"]) for n, o in (("184", "OC"), ("185", "TS"))]
    + amd("27S28", "27S29", "512x8", [("A", 35), ("", 55)],
          "amd/am27s28-am27s29-512x8-bipolar-prom.pdf", ["74S472", "74S473", "6349"])
    + amd("27S180", "27S181", "1Kx8", [("A", 35), ("", 60)],
          "amd/am27s180-am27s181-am27s280-am27s281-1kx8-bipolar-prom.pdf",
          ["82S180", "82S181", "87S181", "6381"])
    + amd("27S280", "27S281", "1Kx8", [("A", 35), ("", 60)],
          "amd/am27s180-am27s181-am27s280-am27s281-1kx8-bipolar-prom.pdf",
          ["27S181", "82S181", "skinny"], width=0.3)
    + [P("AMD", f"Am27PS{n}", "1Kx8", "TS", [(f"AM27PS{n}PC", 65)],
         "amd/am27s180-am27s181-am27s280-am27s281-1kx8-bipolar-prom.pdf", "low",
         width=w, note="power-switched (low standby power when deselected)",
         kw=["27S181", "82S181"]) for n, w in (("181", None), ("281", 0.3))]
    + amd("27S190", "27S191", "2Kx8", [("A", 35), ("", 50)],
          "amd/am27s190-am27s191-am27s290-am27s291-2kx8-bipolar-prom.pdf",
          ["82S190", "82S191", "87S191"])
    + amd("27S290", "27S291", "2Kx8", [("A", 35), ("", 50)],
          "amd/am27s190-am27s191-am27s290-am27s291-2kx8-bipolar-prom.pdf",
          ["27S191", "82S191", "skinny"], width=0.3)
    + [P("AMD", f"Am27PS{n}", "2Kx8", "TS",
         [(f"AM27PS{n}APC", 50), (f"AM27PS{n}PC", 65)],
         "amd/am27s190-am27s191-am27s290-am27s291-2kx8-bipolar-prom.pdf", "low",
         width=w, note="power-switched (low standby power when deselected)",
         kw=["27S191", "82S191"]) for n, w in (("191", None), ("291", 0.3))]
    # ---- MMI 1981 (NiCr ceramic, Ti-W plastic) -----------------------------------------
    + mmi("6330", "6331", "32x8", {"-1": (50, 50)},
          "mmi/6330-6331-32x8-bipolar-prom.pdf", ["82S23", "82S123", "74S288"])
    + mmi("6300", "6301", "256x4", {"-1": (55, 55)},
          "mmi/6300-6301-256x4-bipolar-prom.pdf", ["82S126", "82S129", "74S287"])
    + mmi("6305", "6306", "512x4", {"-1": (60, 60)},
          "mmi/6305-6306-512x4-bipolar-prom.pdf", ["82S130", "82S131", "74S571"])
    + mmi("6352", "6353", "1Kx4", {"-1": (60, 60)},
          "mmi/6352-6353-1kx4-bipolar-prom.pdf", ["82S136", "82S137", "74S573"])
    + mmi("6388", "6389", "2Kx4", {"-1": (70, 70), "-2": (None, 55)},
          "mmi/6388-6389-2kx4-bipolar-prom.pdf", ["82S184", "82S185", "87S185"])
    + mmi("6348", "6349", "512x8", {"-1": (70, 70), "-2": (70, 55)},
          "mmi/6348-6349-512x8-bipolar-prom.pdf", ["27S28", "27S29", "74S472"])
    + mmi("6340", "6341", "512x8-24", {"-1": (70, 70)},
          "mmi/6340-6341-512x8-24pin-bipolar-prom.pdf", ["74S474", "74S475", "27S31"])
    + mmi("6340", "6341", "512x8-24", {"-2": (70, 55)},
          "mmi/6340-6341-512x8-24pin-bipolar-prom.pdf", ["74S474", "74S475", "27S31"],
          skinny=True)
    + mmi("6380", "6381", "1Kx8", {"-1": (90, 90), "-2": (70, 55)},
          "mmi/6380-6381-1kx8-bipolar-prom.pdf", ["82S180", "82S181", "87S181"],
          skinny=True)
    + [P("MMI", v, org, o, [(f"{v}N", ns)], ds, "low", fuse="Ti-W", kw=kw)
       for v, org, o, ns, ds, kw in (
           ("63S140", "256x4", "OC", 45,
            "mmi/63s140-63s141-63ls140-63ls141-256x4-bipolar-prom.pdf", ["6300", "82S126"]),
           ("63S141", "256x4", "TS", 45,
            "mmi/63s140-63s141-63ls140-63ls141-256x4-bipolar-prom.pdf", ["6301", "82S129"]),
           ("63LS140", "256x4", "OC", 55,
            "mmi/63s140-63s141-63ls140-63ls141-256x4-bipolar-prom.pdf", ["6300", "82S126"]),
           ("63LS141", "256x4", "TS", 55,
            "mmi/63s140-63s141-63ls140-63ls141-256x4-bipolar-prom.pdf", ["6301", "82S129"]),
           ("63S240", "512x4", "OC", 45,
            "mmi/63s240-63s241-63ls240-63ls241-512x4-bipolar-prom.pdf", ["6305", "82S130"]),
           ("63S241", "512x4", "TS", 45,
            "mmi/63s240-63s241-63ls240-63ls241-512x4-bipolar-prom.pdf", ["6306", "82S131"]),
           ("63LS240", "512x4", "OC", 60,
            "mmi/63s240-63s241-63ls240-63ls241-512x4-bipolar-prom.pdf", ["6305", "82S130"]),
           ("63LS241", "512x4", "TS", 60,
            "mmi/63s240-63s241-63ls240-63ls241-512x4-bipolar-prom.pdf", ["6306", "82S131"]),
       )]
    # ---- TI 1981 -----------------------------------------------------------------------
    + ti("TBP18S030", "32x8", 40, 40, "ti/tbp14-tbp18-series-bipolar-prom.pdf", "low",
         ["SN74S288", "SN74S188", "82S123", "82S23"])
    + ti("TBP14S10", "256x4", 65, 65, "ti/tbp14-tbp18-series-bipolar-prom.pdf", "high",
         ["SN74S287", "SN74S387", "82S129", "82S126"])
    + ti("TBP24S10", "256x4", 55, 65, "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high",
         ["82S129", "82S126", "74S287"])
    + ti("TBP24S41", "1Kx4", 60, 60, "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high",
         ["SN74S476", "SN74S477", "82S137", "82S136"])
    + ti("TBP24S81", "2Kx4", 70, 70, "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high",
         ["SN74S454", "SN74S455", "82S185", "82S184"])
    + ti("TBP18S42", "512x8", 75, 75, "ti/tbp14-tbp18-series-bipolar-prom.pdf", "low",
         ["SN74S472", "SN74S473", "27S29", "6349"])
    + ti("TBP28S42", "512x8", 60, 65, "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high",
         ["74S472", "27S29", "6349"])
    + ti("TBP18S46", "512x8-24", 75, 75, "ti/tbp14-tbp18-series-bipolar-prom.pdf", "low",
         ["SN74S474", "SN74S475", "6341", "82S141"])
    + ti("TBP28S46", "512x8-24", 60, 65, "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high",
         ["74S474", "6341", "82S141"])
    + ti("TBP28S86", "1Kx8", 70, 70, "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high",
         ["SN74S478", "SN74S479", "82S181", "82S180"])
    + [P("Texas Instruments", "TBP28L86", "1Kx8", "TS", [("TBP28L86N", 130)],
         "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high", note="low power",
         kw=["SN74LS478", "TBP28S86", "82LS181"])]
    + ti("TBP28S166", "2Kx8", 75, 80, "ti/tbp24-tbp28-series-bipolar-prom.pdf", "high",
         ["82S191", "82S190", "87S191"])
    # ---- National 1983 -----------------------------------------------------------------
    + nat("DM74S188", "DM74S288", "32x8", 35,
          "national/dm74s188-dm74s288-32x8-bipolar-prom.pdf", ["82S23", "82S123"])
    + nat("DM74S387", "DM74S287", "256x4", 50,
          "national/dm74s387-dm74s287-256x4-bipolar-prom.pdf", ["82S126", "82S129"])
    + nat("DM74S570", "DM74S571", "512x4", 55,
          "national/dm74s570-dm74s571-512x4-bipolar-prom.pdf", ["82S130", "82S131"])
    + nat("DM74S572", "DM74S573", "1Kx4", 60,
          "national/dm74s572-dm74s573-1kx4-bipolar-prom.pdf", ["82S136", "82S137"])
    + nat("DM87S184", "DM87S185", "2Kx4", 55,
          "national/dm87s184-dm87s185-2kx4-bipolar-prom.pdf", ["82S184", "82S185"])
    + nat("DM74S473", "DM74S472", "512x8", 60,
          "national/dm74s473-dm74s472-512x8-bipolar-prom.pdf", ["27S28", "27S29", "6349"])
    + nat("DM74S475", "DM74S474", "512x8-24", 65,
          "national/dm74s475-dm74s474-512x8-24pin-bipolar-prom.pdf", ["6340", "6341"])
    + nat("DM87S180", "DM87S181", "1Kx8", 55,
          "national/dm87s180-dm87s181-dm87s280-dm87s281-1kx8-bipolar-prom.pdf",
          ["82S180", "82S181"])
    + nat("DM87S280", "DM87S281", "1Kx8", 55,
          "national/dm87s180-dm87s181-dm87s280-dm87s281-1kx8-bipolar-prom.pdf",
          ["87S181", "82S181", "skinny"], width=0.3)
    + nat("DM87S190", "DM87S191", "2Kx8", 65,
          "national/dm87s190-dm87s191-dm87s290-dm87s291-2kx8-bipolar-prom.pdf",
          ["82S190", "82S191"], note="W fuses")
    + nat("DM87S290", "DM87S291", "2Kx8", 65,
          "national/dm87s190-dm87s191-dm87s290-dm87s291-2kx8-bipolar-prom.pdf",
          ["87S191", "82S191", "skinny"], width=0.3, note="W fuses")
)


def records():
    for chip in CHIPS:
        words, bits, pins, sym_oc, sym_ts = ORG[chip["org"]]
        org = chip["org"].split("-")[0]
        width = chip["width"] or (0.3 if pins < 24 else 0.6)
        package = f"{chip['package']}-{pins}" + (" 0.3in" if pins == 24 and width == 0.3
                                                  else "")
        folder, temp, link = MAKERS[chip["mfr"]]
        outputs = "open-collector" if chip["out"] == "OC" else "3-state"
        for mpn, ns in chip["codes"]:
            bits_ = [f"{chip['mfr']} {chip['value']} {org} bipolar fuse PROM", outputs,
                     f"{ns}ns"]
            if chip["note"]:
                bits_.append(chip["note"])
            bits_ += [f"{chip['fuse']} fuses, unprogrammed outputs {chip['unprog']}",
                      package]
            yield row(
                created_by=CREATED_BY, manufacturer=chip["mfr"], mpn=mpn,
                value=chip["value"], memory_type="PROM", words=words, bits=bits,
                speed=f"{ns} ns", package=package, pins=pins, width_in=width,
                symbol=f"{LIB}:{sym_oc if chip['out'] == 'OC' else sym_ts}",
                datasheet=chip["ds"], description=", ".join(bits_),
                keywords=[chip["value"]] + chip["kw"]
                + ["PROM", "bipolar PROM", "fuse PROM", outputs, "vintage"],
                supply_rails="+5V", mfr_link=link, temp=temp)


def main():
    write(OUTPUT_FILE, "bipolar fusible-link PROMs", CREATED_BY, list(records()))


if __name__ == "__main__":
    main()
