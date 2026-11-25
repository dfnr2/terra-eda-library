#!/usr/bin/env python3
"""Classic through-hole small-signal BJTs: TO-92 and TO-18/TO-39 metal cans.

Sources, in order of preference (plans/bjt-through-hole-classics.md has the detail):

  - onsemi, Fairchild-heritage TO-92 line. Its ordering codes carry the packing:
    BU = bulk bag, straight leads (1.27 mm, TO-92_Inline); TA = fan-fold ammo, leads
    formed to 2.54 mm (case 135AR, TO-92_Inline_Wide). Bulk is used wherever onsemi
    still sells it; TA only where bulk is gone (BC549B/C, BC559C, BC640). MPSA06 and
    MPSA42 are sold bulk-only under the bare type number. onsemi's own older TO-92
    codes (G / RL / ZL suffixes: P2N2222AG, 2N3906G, MPSA92G, BC557BG ...) are all
    Obsolete and are not used.
  - Central Semiconductor for what onsemi no longer makes: 2N5088/2N5089, MPSA56,
    MPSA92, MPSA13/MPSA14, and the metal cans. Ordering code "<type> PBFREE"
    (bulk; the sheets say to add " PBFREE"); straight 1.27 mm leads.
  - Diotec for BC546B, BC548B/C, BC556B, BC557B/C and BC558B, which onsemi lists as
    discontinued. Diotec's standard code ships in ammo with leads formed to 2.54 mm
    ("Raster 2.54"; bulk is a "BK" special order).

Lead order is from each maker's own sheet; _bjt.rows() checks it against the named
Transistor_BJT symbol. PN2907A: onsemi's PN2907A-FSC sheet draws the leads without
naming them, so its E-B-C order is taken from onsemi's PN2907A/D (TO-92 case 29
style 1: 1 emitter, 2 base, 3 collector).

Pd is at Ta = 25 C (metal cans also give the Tc = 25 C rating); hFE is the data
sheet's headline min-max at the stated Ic; fT is the guaranteed minimum unless
marked typ.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _bjt import Part, write  # noqa: E402

OUTPUT_FILE = HERE / "bjt_generated_320_small_signal_th.sql"
CREATED_BY = Path(__file__).name


def on(mpn):
    return f"https://www.onsemi.com/PowerSolutions/product.do?id={mpn}"


def dio(mpn):
    return f"https://diotec.com/en/product/{mpn}.html"


TA = "625mW (Ta=25C)"
BC = "500mW (Ta=25C)"

PARTS = [
    # --- onsemi TO-92, general purpose -------------------------------------------
    Part("onsemi", "2N3904BU", "2N3904", "npn", "TO-92", "EBC", "2N3904",
         "40V", "200mA", TA, "100-300 @ Ic=10mA, Vce=1V", "300MHz min", "150C",
         "onsemi/2n3904-d.pdf", "bulk", link=on("2N3904BU"),
         keywords="general-purpose,switching", note="complement 2N3906"),
    Part("onsemi", "2N3906BU", "2N3906", "pnp", "TO-92", "EBC", "2N3906",
         "40V", "200mA", TA, "100-300 @ Ic=-10mA, Vce=-1V", "250MHz min", "150C",
         "onsemi/pzt3906-d.pdf", "bulk", link=on("2N3906BU"),
         keywords="general-purpose,switching", note="complement 2N3904"),
    Part("onsemi", "PN2222ABU", "PN2222A", "npn", "TO-92", "EBC", "PN2222A",
         "40V", "1A", TA, "100-300 @ Ic=150mA, Vce=10V", "300MHz min", "150C",
         "onsemi/pn2222a-d.pdf", "bulk", link=on("PN2222ABU"),
         keywords="general-purpose,switching,2N2222A", note="complement PN2907A"),
    Part("onsemi", "PN2907ABU", "PN2907A", "pnp", "TO-92", "EBC", "Q_PNP_EBC",
         "60V", "800mA", TA, "100-300 @ Ic=-150mA, Vce=-10V", "200MHz min", "150C",
         "onsemi/pn2907a-fsc-d.pdf", "bulk", link=on("PN2907ABU"),
         keywords="general-purpose,switching,2N2907A", note="complement PN2222A"),
    Part("onsemi", "2N4401BU", "2N4401", "npn", "TO-92", "EBC", "Q_NPN_EBC",
         "40V", "600mA", TA, "100-300 @ Ic=150mA, Vce=1V", "250MHz min", "150C",
         "onsemi/mmbt4401-d.pdf", "bulk", link=on("2N4401BU"),
         keywords="general-purpose,switching", note="complement 2N4403"),
    Part("onsemi", "2N4403BU", "2N4403", "pnp", "TO-92", "EBC", "Q_PNP_EBC",
         "40V", "600mA", TA, "100-300 @ Ic=-150mA, Vce=-2V", "200MHz min", "150C",
         "onsemi/2n4403t.pdf", "bulk", link=on("2N4403BU"),
         keywords="general-purpose,switching", note="complement 2N4401"),
    # Only the Y gain class (hFE 120-240) is still sold.
    Part("onsemi", "2N5401YBU", "2N5401", "pnp", "TO-92", "EBC", "Q_PNP_EBC",
         "150V", "600mA", TA, "120-240 @ Ic=-10mA, Vce=-5V", "100MHz min", "150C",
         "onsemi/2n5401-d.pdf", "bulk", link=on("2N5401YBU"),
         keywords="high-voltage", note="hFE class Y; complement 2N5551"),
    Part("onsemi", "2N5551BU", "2N5551", "npn", "TO-92", "EBC", "Q_NPN_EBC",
         "160V", "600mA", TA, "80-250 @ Ic=10mA, Vce=5V", "100MHz min", "150C",
         "onsemi/2n5551t-d.pdf", "bulk", link=on("2N5551BU"),
         keywords="high-voltage", note="complement 2N5401"),
    Part("onsemi", "MPSA06", "MPSA06", "npn", "TO-92", "EBC", "Q_NPN_EBC",
         "80V", "500mA", TA, "100 min @ Ic=10mA and 100mA, Vce=1V", "100MHz min",
         "150C", "onsemi/pzta06-d.pdf", "bulk", link=on("MPSA06"),
         keywords="driver", note="complement MPSA56"),
    Part("onsemi", "MPSA42", "MPSA42", "npn", "TO-92", "EBC", "MPSA42",
         "300V", "500mA", TA, "40 min @ Ic=10mA and 30mA, Vce=10V", "50MHz min",
         "150C", "onsemi/pzta42-d.pdf", "bulk", link=on("MPSA42"),
         keywords="high-voltage", note="complement MPSA92"),

    # --- onsemi TO-92, BC series (C-B-E) -----------------------------------------
    Part("onsemi", "BC547BBU", "BC547B", "npn", "TO-92", "CBE", "BC547",
         "45V", "100mA", BC, "200-450 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "onsemi/bc550-d.pdf", "bulk", link=on("BC547BBU"),
         keywords="general-purpose,BC547", note="hFE group B"),
    Part("onsemi", "BC547CBU", "BC547C", "npn", "TO-92", "CBE", "BC547",
         "45V", "100mA", BC, "420-800 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "onsemi/bc550-d.pdf", "bulk", link=on("BC547CBU"),
         keywords="general-purpose,BC547", note="hFE group C"),
    Part("onsemi", "BC549BTA", "BC549B", "npn", "TO-92 formed", "CBE", "BC549",
         "30V", "100mA", BC, "200-450 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "onsemi/bc550-d.pdf", "ammo", link=on("BC549BTA"),
         keywords="low-noise,BC549", note="hFE group B, low noise"),
    Part("onsemi", "BC549CTA", "BC549C", "npn", "TO-92 formed", "CBE", "BC549",
         "30V", "100mA", BC, "420-800 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "onsemi/bc550-d.pdf", "ammo", link=on("BC549CTA"),
         keywords="low-noise,BC549", note="hFE group C, low noise"),
    Part("onsemi", "BC550CBU", "BC550C", "npn", "TO-92", "CBE", "BC550",
         "45V", "100mA", BC, "420-800 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "onsemi/bc550-d.pdf", "bulk", link=on("BC550CBU"),
         keywords="low-noise,BC550", note="hFE group C, low noise"),
    Part("onsemi", "BC559CTA", "BC559C", "pnp", "TO-92 formed", "CBE", "BC559",
         "30V", "100mA", BC, "420-800 @ Ic=-2mA, Vce=-5V", "150MHz typ", "150C",
         "onsemi/bc556bta-d.pdf", "ammo", link=on("BC559CTA"),
         keywords="low-noise,BC559", note="hFE group C, low noise"),
    Part("onsemi", "BC33725BU", "BC337-25", "npn", "TO-92", "CBE", "BC337",
         "45V", "800mA", TA, "160-400 @ Ic=100mA, Vce=1V", "100MHz typ", "150C",
         "onsemi/bc337-fsc-d.pdf", "bulk", link=on("BC33725BU"),
         keywords="general-purpose,switching,BC337", note="hFE group 25; complement BC327-25"),
    Part("onsemi", "BC33740BU", "BC337-40", "npn", "TO-92", "CBE", "BC337",
         "45V", "800mA", TA, "250-630 @ Ic=100mA, Vce=1V", "100MHz typ", "150C",
         "onsemi/bc337-fsc-d.pdf", "bulk", link=on("BC33740BU"),
         keywords="general-purpose,switching,BC337", note="hFE group 40; complement BC327-40"),
    Part("onsemi", "BC32725BU", "BC327-25", "pnp", "TO-92", "CBE", "BC327",
         "45V", "800mA", TA, "160-400 @ Ic=-100mA, Vce=-1V", "100MHz typ", "150C",
         "onsemi/bc327-d.pdf", "bulk", link=on("BC32725BU"),
         keywords="general-purpose,switching,BC327", note="hFE group 25; complement BC337-25"),
    Part("onsemi", "BC32740BU", "BC327-40", "pnp", "TO-92", "CBE", "BC327",
         "45V", "800mA", TA, "250-630 @ Ic=-100mA, Vce=-1V", "100MHz typ", "150C",
         "onsemi/bc327-d.pdf", "bulk", link=on("BC32740BU"),
         keywords="general-purpose,switching,BC327", note="hFE group 40; complement BC337-40"),
    # BC640 is E-C-B like BC636; no stock BC640 symbol, so the generic one.
    Part("onsemi", "BC640TA", "BC640", "pnp", "TO-92 formed", "ECB", "Q_PNP_ECB",
         "80V", "1A", "1W (Ta=25C)", "40-160 @ Ic=-150mA, Vce=-2V", "100MHz typ",
         "150C", "onsemi/bc640-fcs-d.pdf", "ammo", link=on("BC640TA"),
         keywords="driver,medium-power,BC640", note="complement BC639"),

    # --- Diotec TO-92, BC series (C-B-E), ammo, leads formed to 2.54 mm ----------
    Part("Diotec", "BC546B", "BC546B", "npn", "TO-92 formed", "CBE", "BC546",
         "65V", "100mA", BC, "200-450 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "diotec/bc546-bc549.pdf", "ammo", link=dio("BC546B"),
         keywords="general-purpose,high-voltage,BC546", note="hFE group B"),
    Part("Diotec", "BC548B", "BC548B", "npn", "TO-92 formed", "CBE", "BC548",
         "30V", "100mA", BC, "200-450 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "diotec/bc546-bc549.pdf", "ammo", link=dio("BC548B"),
         keywords="general-purpose,BC548", note="hFE group B"),
    Part("Diotec", "BC548C", "BC548C", "npn", "TO-92 formed", "CBE", "BC548",
         "30V", "100mA", BC, "420-800 @ Ic=2mA, Vce=5V", "300MHz typ", "150C",
         "diotec/bc546-bc549.pdf", "ammo", link=dio("BC548C"),
         keywords="general-purpose,BC548", note="hFE group C"),
    Part("Diotec", "BC556B", "BC556B", "pnp", "TO-92 formed", "CBE", "BC556",
         "65V", "100mA", BC, "200-450 @ Ic=-2mA, Vce=-5V", "150MHz typ", "150C",
         "diotec/bc556-bc559.pdf", "ammo", link=dio("BC556B"),
         keywords="general-purpose,high-voltage,BC556", note="hFE group B"),
    Part("Diotec", "BC557B", "BC557B", "pnp", "TO-92 formed", "CBE", "BC557",
         "45V", "100mA", BC, "200-450 @ Ic=-2mA, Vce=-5V", "150MHz typ", "150C",
         "diotec/bc556-bc559.pdf", "ammo", link=dio("BC557B"),
         keywords="general-purpose,BC557", note="hFE group B"),
    Part("Diotec", "BC557C", "BC557C", "pnp", "TO-92 formed", "CBE", "BC557",
         "45V", "100mA", BC, "420-800 @ Ic=-2mA, Vce=-5V", "150MHz typ", "150C",
         "diotec/bc556-bc559.pdf", "ammo", link=dio("BC557C"),
         keywords="general-purpose,BC557", note="hFE group C"),
    Part("Diotec", "BC558B", "BC558B", "pnp", "TO-92 formed", "CBE", "BC558",
         "30V", "100mA", BC, "200-450 @ Ic=-2mA, Vce=-5V", "150MHz typ", "150C",
         "diotec/bc556-bc559.pdf", "ammo", link=dio("BC558B"),
         keywords="general-purpose,BC558", note="hFE group B"),

    # --- Central TO-92 (E-B-C), bulk ---------------------------------------------
    Part("Central", "2N5088 PBFREE", "2N5088", "npn", "TO-92", "EBC", "Q_NPN_EBC",
         "30V", "50mA", TA, "300-900 @ Ic=0.1mA, Vce=5V", "50MHz min", "150C",
         "central/2n5088-2n5089.pdf", "bulk",
         keywords="low-noise,high-gain", note="low-noise high-gain amplifier"),
    Part("Central", "2N5089 PBFREE", "2N5089", "npn", "TO-92", "EBC", "Q_NPN_EBC",
         "25V", "50mA", TA, "400-1200 @ Ic=0.1mA, Vce=5V", "50MHz min", "150C",
         "central/2n5088-2n5089.pdf", "bulk",
         keywords="low-noise,high-gain", note="low-noise high-gain amplifier"),
    Part("Central", "MPSA56 PBFREE", "MPSA56", "pnp", "TO-92", "EBC", "Q_PNP_EBC",
         "80V", "500mA", TA, "100 min @ Ic=-10mA and -100mA, Vce=-1V", "50MHz min",
         "150C", "central/mpsa05-mpsa56.pdf", "bulk",
         keywords="driver", note="complement MPSA06"),
    Part("Central", "MPSA92 PBFREE", "MPSA92", "pnp", "TO-92", "EBC", "MPSA92",
         "300V", "500mA", TA, "40 min @ Ic=-10mA, Vce=-10V", "50MHz min", "150C",
         "central/mpsa92-mpsa93.pdf", "bulk",
         keywords="high-voltage", note="complement MPSA42"),
    # The sheet rates the MPSA13/14 by VCES (base shorted); there is no VCEO line.
    Part("Central", "MPSA13 PBFREE", "MPSA13", "npn", "TO-92", "EBC",
         "Q_NPN_Darlington_EBC", "VCES 30V", "500mA", TA,
         "5000 min @ Ic=10mA, 10000 min @ Ic=100mA, Vce=5V", "125MHz min", "150C",
         "central/mpsa12-mpsa14.pdf", "bulk", darlington=True,
         keywords="high-gain", note="Darlington"),
    Part("Central", "MPSA14 PBFREE", "MPSA14", "npn", "TO-92", "EBC",
         "Q_NPN_Darlington_EBC", "VCES 30V", "500mA", TA,
         "10000 min @ Ic=10mA, 20000 min @ Ic=100mA, Vce=5V", "125MHz min", "150C",
         "central/mpsa12-mpsa14.pdf", "bulk", darlington=True,
         keywords="high-gain", note="Darlington"),

    # --- Central metal cans (E-B-C, collector on the case) -----------------------
    Part("Central", "2N2222A PBFREE", "2N2222A", "npn", "TO-18", "EBC", "Q_NPN_EBC",
         "40V", "800mA", "500mW (Ta=25C), 1.8W (Tc=25C)",
         "100-300 @ Ic=150mA, Vce=10V", "300MHz min", "200C",
         "central/2n2221a-2n2222a.pdf", "bulk",
         keywords="general-purpose,switching,metal-can", note="complement 2N2907A"),
    Part("Central", "2N2907A PBFREE", "2N2907A", "pnp", "TO-18", "EBC", "Q_PNP_EBC",
         "60V", "600mA", "400mW (Ta=25C), 1.8W (Tc=25C)",
         "100-300 @ Ic=-150mA, Vce=-10V", "200MHz min", "200C",
         "central/2n2906-2n2907a.pdf", "bulk",
         keywords="general-purpose,switching,metal-can", note="complement 2N2222A"),
    Part("Central", "2N2219A PBFREE", "2N2219A", "npn", "TO-39", "EBC", "2N2219",
         "40V", "800mA", "800mW (Ta=25C), 3W (Tc=25C)",
         "100-300 @ Ic=150mA, Vce=10V", "300MHz min", "200C",
         "central/2n2219-2n2219a.pdf", "bulk",
         keywords="general-purpose,switching,metal-can"),
    Part("Central", "2N3053 PBFREE", "2N3053", "npn", "TO-39", "EBC", "Q_NPN_EBC",
         "40V", "700mA", "5W (Tc=25C)", "50-250 @ Ic=150mA, Vce=10V", "100MHz min",
         "200C", "central/2n3053-2n3053a.pdf", "bulk",
         keywords="general-purpose,driver,metal-can"),
]


if __name__ == "__main__":
    write(OUTPUT_FILE, "through-hole small-signal BJTs (TO-92, TO-18, TO-39)",
          CREATED_BY, PARTS)
