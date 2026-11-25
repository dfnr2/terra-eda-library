#!/usr/bin/env python3
"""Classic through-hole power BJTs from onsemi: TO-220, TO-225, TO-247 and TO-3.

All onsemi "G" (Pb-free) ordering codes, each on its data sheet's ordering table
and checked on onsemi's product pages (plans/bjt-through-hole-classics.md):

  - TIP31C/TIP32C, TIP41C/TIP42C, MJE3055T/MJE2955T, D44H11/D45H11 (TO-220, rail)
  - TIP120/TIP122/TIP127 Darlingtons (TO-220, rail). TIP125G is Obsolete at onsemi
    and Central's TIP125 is end-of-life (PDN01250), so it is left out.
  - TIP3055/TIP2955 (TO-247, rail). onsemi shows TIP2955G as "Last Shipments";
    it stays in as EOL because it is the TIP3055's only complement.
  - BD139/BD140 and MJE340/MJE350 (TO-225, box). TO-225 is the TO-126 outline,
    so the TO-126-3_Vertical footprint (2.28 mm pitch) fits.
  - 2N3055/MJ2955 (TO-204AA = TO-3, tray), collector on the case.

Lead orders (all from the sheets): TO-220 style 1 is B-C-E, TO-247 B-C-E, TO-225
style 1 is E-C-B, TO-3 style 1 is pin 1 base, pin 2 emitter, case collector.
MJE350G has no onsemi TO-225 sheet of its own: the product page links the
Fairchild MJE350 sheet (TO-126, 1 emitter 2 collector 3 base), used here.

Pd is at Tc = 25 C. hFE is the headline min-max at the stated Ic; fT is the
guaranteed minimum unless marked typ, and NULL where the sheet gives none (the
TIP12x Darlingtons, BD139/BD140, MJE340/MJE350).

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _bjt import Part, write  # noqa: E402

OUTPUT_FILE = HERE / "bjt_generated_330_power_th.sql"
CREATED_BY = Path(__file__).name


def on(mpn):
    return f"https://www.onsemi.com/PowerSolutions/product.do?id={mpn}"


def P(mpn, value, pol, pkg, pinout, sym, vceo, ic, pd, hfe, ft, tj, ds, packing,
      **kw):
    return Part("onsemi", mpn, value, pol, pkg, pinout, sym, vceo, ic, pd, hfe, ft,
                tj, f"onsemi/{ds}", packing, link=on(mpn), **kw)


PARTS = [
    # --- TO-220, B-C-E -------------------------------------------------------------
    P("TIP31CG", "TIP31C", "npn", "TO-220", "BCE", "Q_NPN_BCE", "100V", "3A",
      "40W (Tc=25C)", "10-50 @ Ic=3A, Vce=4V", "3MHz min", "150C", "tip31a-d.pdf",
      "rail", keywords="power,TIP31", note="complement TIP32C"),
    P("TIP32CG", "TIP32C", "pnp", "TO-220", "BCE", "Q_PNP_BCE", "100V", "3A",
      "40W (Tc=25C)", "10-50 @ Ic=-3A, Vce=-4V", "3MHz min", "150C", "tip31a-d.pdf",
      "rail", keywords="power,TIP32", note="complement TIP31C"),
    P("TIP41CG", "TIP41C", "npn", "TO-220", "BCE", "TIP41C", "100V", "6A",
      "65W (Tc=25C)", "15-75 @ Ic=3A, Vce=4V", "3MHz min", "150C", "tip41a-d.pdf",
      "rail", keywords="power,TIP41", note="complement TIP42C"),
    P("TIP42CG", "TIP42C", "pnp", "TO-220", "BCE", "TIP42C", "100V", "6A",
      "65W (Tc=25C)", "15-75 @ Ic=-3A, Vce=-4V", "3MHz min", "150C", "tip41a-d.pdf",
      "rail", keywords="power,TIP42", note="complement TIP41C"),
    P("TIP120G", "TIP120", "npn", "TO-220", "BCE", "TIP120", "60V", "5A",
      "65W (Tc=25C)", "1000 min @ Ic=0.5A and 3A, Vce=3V", None, "150C",
      "tip120-d.pdf", "rail", darlington=True, keywords="power,TIP120",
      note="Darlington with B-E shunt resistors; complement TIP125"),
    P("TIP122G", "TIP122", "npn", "TO-220", "BCE", "TIP122", "100V", "5A",
      "65W (Tc=25C)", "1000 min @ Ic=0.5A and 3A, Vce=3V", None, "150C",
      "tip120-d.pdf", "rail", darlington=True, keywords="power,TIP122",
      note="Darlington with B-E shunt resistors; complement TIP127"),
    P("TIP127G", "TIP127", "pnp", "TO-220", "BCE", "TIP127", "100V", "5A",
      "65W (Tc=25C)", "1000 min @ Ic=-0.5A and -3A, Vce=-3V", None, "150C",
      "tip120-d.pdf", "rail", darlington=True, keywords="power,TIP127",
      note="Darlington with B-E shunt resistors; complement TIP122"),
    P("MJE3055TG", "MJE3055T", "npn", "TO-220", "BCE", "Q_NPN_BCE", "60V", "10A",
      "75W (Tc=25C)", "20-100 @ Ic=4A, Vce=4V", "2MHz min", "150C",
      "mje2955t-d.pdf", "rail", keywords="power,MJE3055", note="complement MJE2955T"),
    P("MJE2955TG", "MJE2955T", "pnp", "TO-220", "BCE", "Q_PNP_BCE", "60V", "10A",
      "75W (Tc=25C)", "20-100 @ Ic=-4A, Vce=-4V", "2MHz min", "150C",
      "mje2955t-d.pdf", "rail", keywords="power,MJE2955", note="complement MJE3055T"),
    P("D44H11G", "D44H11", "npn", "TO-220", "BCE", "Q_NPN_BCE", "80V", "10A",
      "70W (Tc=25C)", "60 min @ Ic=2A, 40 min @ Ic=4A, Vce=1V", "50MHz typ", "150C",
      "d44h-d.pdf", "rail", keywords="power,low-vcesat,D44H",
      note="low VCE(sat), fast switching; complement D45H11"),
    P("D45H11G", "D45H11", "pnp", "TO-220", "BCE", "Q_PNP_BCE", "80V", "10A",
      "70W (Tc=25C)", "60 min @ Ic=-2A, 40 min @ Ic=-4A, Vce=-1V", "40MHz typ",
      "150C", "d44h-d.pdf", "rail", keywords="power,low-vcesat,D45H",
      note="low VCE(sat), fast switching; complement D44H11"),

    # --- TO-247, B-C-E ---------------------------------------------------------------
    P("TIP3055G", "TIP3055", "npn", "TO-247", "BCE", "TIP3055G", "60V", "15A",
      "90W (Tc=25C)", "20-70 @ Ic=4A, Vce=4V", "2.5MHz min", "150C",
      "tip3055-d.pdf", "rail", keywords="power,TIP3055", note="complement TIP2955"),
    P("TIP2955G", "TIP2955", "pnp", "TO-247", "BCE", "TIP2955G", "60V", "15A",
      "90W (Tc=25C)", "20-70 @ Ic=-4A, Vce=-4V", "2.5MHz min", "150C",
      "tip3055-d.pdf", "rail", lifecycle="EOL", keywords="power,TIP2955",
      note="complement TIP3055; onsemi last shipments"),

    # --- TO-225 (TO-126 outline), E-C-B ---------------------------------------------
    P("BD139G", "BD139", "npn", "TO-225", "ECB", "BD139", "80V", "1.5A",
      "12.5W (Tc=25C)", "40-250 @ Ic=150mA, Vce=2V", None, "150C", "bd135-d.pdf",
      "box", keywords="medium-power,audio,BD139", note="complement BD140"),
    P("BD140G", "BD140", "pnp", "TO-225", "ECB", "BD140", "80V", "1.5A",
      "12.5W (Tc=25C)", "40-250 @ Ic=-150mA, Vce=-2V", None, "150C",
      "bd136g-d.pdf", "box", keywords="medium-power,audio,BD140",
      note="complement BD139"),
    P("MJE340G", "MJE340", "npn", "TO-225", "ECB", "Q_NPN_ECB", "300V", "500mA",
      "20W (Tc=25C)", "30-240 @ Ic=50mA, Vce=10V", None, "150C", "mje340-d.pdf",
      "box", keywords="high-voltage,medium-power,MJE340", note="complement MJE350"),
    P("MJE350G", "MJE350", "pnp", "TO-225", "ECB", "Q_PNP_ECB", "300V", "500mA",
      "20W (Tc=25C)", "30-240 @ Ic=-50mA, Vce=-10V", None, "150C", "mje350-d.pdf",
      "box", keywords="high-voltage,medium-power,MJE350", note="complement MJE340"),

    # --- TO-3 (TO-204AA): pin 1 base, pin 2 emitter, case collector -----------------
    P("2N3055G", "2N3055", "npn", "TO-3", "BEC", "2N3055", "60V", "15A",
      "115W (Tc=25C)", "20-70 @ Ic=4A, Vce=4V", "2.5MHz min", "200C",
      "2n3055-d.pdf", "tray", keywords="power,metal-can,2N3055",
      note="collector on case; complement MJ2955"),
    P("MJ2955G", "MJ2955", "pnp", "TO-3", "BEC", "MJ2955", "60V", "15A",
      "115W (Tc=25C)", "20-70 @ Ic=-4A, Vce=-4V", "2.5MHz min", "200C",
      "2n3055-d.pdf", "tray", keywords="power,metal-can,MJ2955",
      note="collector on case; complement 2N3055"),
]


if __name__ == "__main__":
    write(OUTPUT_FILE, "through-hole power BJTs (TO-220, TO-225, TO-247, TO-3)",
          CREATED_BY, PARTS)
