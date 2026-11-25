#!/usr/bin/env python3
"""Through-hole TO-220AB power MOSFETs: the Infineon (IR HEXFET) N-suffix classics,
the Vishay Siliconix third-generation originals, and onsemi FQP27P06.

The Vishay IRF520/IRF540/IRF9540 are distinct dies from Infineon's IRF520N/IRF540N/
IRF9540N (different RDS(on), current and power ratings), so each gets its own row.

Every number is transcribed from the parked datasheet named in each row
(datasheets/infineon/, datasheets/vishay/, datasheets/onsemi/): Vds, Id at Tc=25C,
Pd at Tc=25C, RDS(on) max with its Vgs/Id condition, Vgs(th) min/max, Tj max and the
lead soldering limit (300C for 10 s, 1.6 mm from case). The operating/storage range
is the datasheets' combined "TJ, TSTG" rating.

mpn is the manufacturer's orderable part number: Infineon's "Orderable Part Number"
(IRF540NPBF ...), Vishay's lead (Pb)-free ordering code (IRF540PbF, written IRF540PBF
as distributors list it; the halogen-free -BE3 option is not recorded), and onsemi's
FQP27P06 (its datasheet's ordering table misprints FCP380N60; the marking and product
page give FQP27P06).

Pinout: every datasheet gives TO-220AB pin 1 = G, 2 = D (and tab), 3 = S, matching the
stock KiCad symbols used (all G-D-S; checked by _th_fets.check()). Parts with an exact
stock symbol use it (IRF540N, IRF9540N, IRLZ44N, IRF3205, IRF4905, IRLB8721PBF, IRF740,
FQP27P06); the rest use the generic Q_NMOS_GDS / Q_PMOS_GDS. Footprint is
Package_TO_SOT_THT:TO-220-3_Vertical throughout.

Lifecycle: Infineon product pages (2026-11-25): all Active except IRF520N "not for new
design" (kept as NRND: a very common classic) and IRLB8721 "discontinued" (kept as
Obsolete: a very common logic-level classic). Vishay: no status on product pages and
Digi-Key/Mouser refused scripted fetches; Active per Future Electronics listings and
Vishay's 2025-2026 process PCNs naming these parts. FQP27P06: onsemi product page Active.
FQP30N06L was dropped (onsemi product page: Obsolete).

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

from _th_fets import write

HERE = Path(__file__).resolve().parent
OUTPUT_FILE = HERE / "mosfet_generated_340_th_power.sql"
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets"

COMMON = {
    "package": "TO-220AB", "kicad_footprint": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "allow_substitution": "No", "tracking": "No",
    "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
    "pin_count": "3", "channels": 1, "pinout": "GDS", "temp_soldering": 300.0,
}

MFR = {
    "Infineon": {"short": "Infineon", "family": "HEXFET"},
    "Vishay": {"short": "Vishay", "family": "Siliconix third-generation"},
    "onsemi": {"short": "onsemi", "family": "QFET"},
}

# (manufacturer, mpn, value, type, Vds V, Id A, Pd W, rds_on text, rds max for the
#  description, Vgs(th) text, Tj max C, logic_level, symbol, datasheet slug,
#  manufacturer_link, lifecycle, extra description note)
CATALOG = [
    # --- Infineon (International Rectifier) HEXFET, TO-220AB ---
    ("Infineon", "IRF540NPBF", "IRF540N", "nmos", 100, "33", 130,
     "44mOhm max @ Vgs=10V, Id=16A", "44 mOhm @ 10V", "2.0V min / 4.0V max", 175, False,
     "IRF540N", "infineon/irf540npbf.pdf", "https://www.infineon.com/part/IRF540N",
     "Active", ""),
    ("Infineon", "IRF9540NPBF", "IRF9540N", "pmos", 100, "23", 140,
     "117mOhm max @ Vgs=-10V, Id=-11A", "117 mOhm @ -10V", "-2.0V min / -4.0V max", 175,
     False, "IRF9540N", "infineon/irf9540npbf.pdf", "https://www.infineon.com/part/IRF9540N",
     "Active", ""),
    ("Infineon", "IRLZ44NPBF", "IRLZ44N", "nmos", 55, "47", 110,
     "22mOhm max @ Vgs=10V, Id=25A; 25mOhm max @ Vgs=5V, Id=25A; "
     "35mOhm max @ Vgs=4V, Id=21A", "25 mOhm @ 5V", "1.0V min / 2.0V max", 175, True,
     "IRLZ44N", "infineon/irlz44npbf.pdf", "https://www.infineon.com/part/IRLZ44N",
     "Active", ""),
    ("Infineon", "IRFZ44NPBF", "IRFZ44N", "nmos", 55, "49", 94,
     "17.5mOhm max @ Vgs=10V, Id=25A", "17.5 mOhm @ 10V", "2.0V min / 4.0V max", 175, False,
     "Q_NMOS_GDS", "infineon/irfz44npbf.pdf", "https://www.infineon.com/part/IRFZ44N",
     "Active", ""),
    ("Infineon", "IRF3205PBF", "IRF3205", "nmos", 55, "110 (package limit 75A)", 200,
     "8.0mOhm max @ Vgs=10V, Id=62A", "8 mOhm @ 10V", "2.0V min / 4.0V max", 175, False,
     "IRF3205", "infineon/irf3205pbf.pdf", "https://www.infineon.com/part/IRF3205",
     "Active", ""),
    ("Infineon", "IRF4905PBF", "IRF4905", "pmos", 55, "74", 200,
     "20mOhm max @ Vgs=-10V, Id=-38A", "20 mOhm @ -10V", "-2.0V min / -4.0V max", 175,
     False, "IRF4905", "infineon/irf4905pbf.pdf", "https://www.infineon.com/part/IRF4905",
     "Active", ""),
    ("Infineon", "IRLB8721PBF", "IRLB8721", "nmos", 30, "62", 65,
     "8.7mOhm max @ Vgs=10V, Id=31A; 16mOhm max @ Vgs=4.5V, Id=25A", "16 mOhm @ 4.5V",
     "1.35V min / 2.35V max", 175, True,
     "IRLB8721PBF", "infineon/irlb8721pbf.pdf", "https://www.infineon.com/part/IRLB8721",
     "Obsolete", "discontinued"),
    ("Infineon", "IRF520NPBF", "IRF520N", "nmos", 100, "9.7", 48,
     "200mOhm max @ Vgs=10V, Id=5.7A", "200 mOhm @ 10V", "2.0V min / 4.0V max", 175, False,
     "Q_NMOS_GDS", "infineon/irf520npbf.pdf", "https://www.infineon.com/part/IRF520N",
     "NRND", "not for new designs"),
    ("Infineon", "IRF530NPBF", "IRF530N", "nmos", 100, "17", 70,
     "90mOhm max @ Vgs=10V, Id=9.0A", "90 mOhm @ 10V", "2.0V min / 4.0V max", 175, False,
     "Q_NMOS_GDS", "infineon/irf530npbf.pdf", "https://www.infineon.com/part/IRF530N",
     "Active", ""),
    # --- Vishay Siliconix third-generation power MOSFETs, TO-220AB ---
    ("Vishay", "IRF520PBF", "IRF520", "nmos", 100, "9.2", 60,
     "0.27ohm max @ Vgs=10V, Id=5.5A", "0.27 ohm @ 10V", "2.0V min / 4.0V max", 175, False,
     "Q_NMOS_GDS", "vishay/irf520.pdf", "https://www.vishay.com/en/product/91017/",
     "Active", ""),
    ("Vishay", "IRF540PBF", "IRF540", "nmos", 100, "28", 150,
     "0.077ohm max @ Vgs=10V, Id=17A", "77 mOhm @ 10V", "2.0V min / 4.0V max", 175, False,
     "Q_NMOS_GDS", "vishay/irf540.pdf", "https://www.vishay.com/en/product/91021/",
     "Active", ""),
    ("Vishay", "IRF740PBF", "IRF740", "nmos", 400, "10", 125,
     "0.55ohm max @ Vgs=10V, Id=6.0A", "0.55 ohm @ 10V", "2.0V min / 4.0V max", 150, False,
     "IRF740", "vishay/irf740.pdf", "https://www.vishay.com/en/product/91054/",
     "Active", ""),
    ("Vishay", "IRF840PBF", "IRF840", "nmos", 500, "8.0", 125,
     "0.85ohm max @ Vgs=10V, Id=4.8A", "0.85 ohm @ 10V", "2.0V min / 4.0V max", 150, False,
     "Q_NMOS_GDS", "vishay/irf840.pdf", "https://www.vishay.com/en/product/91070/",
     "Active", ""),
    ("Vishay", "IRF9530PBF", "IRF9530", "pmos", 100, "12", 88,
     "0.30ohm max @ Vgs=-10V, Id=-7.2A", "0.30 ohm @ -10V", "-2.0V min / -4.0V max", 175,
     False, "Q_PMOS_GDS", "vishay/irf9530.pdf", "https://www.vishay.com/en/product/91076/",
     "Active", ""),
    ("Vishay", "IRF9540PBF", "IRF9540", "pmos", 100, "19", 150,
     "0.20ohm max @ Vgs=-10V, Id=-11A", "0.20 ohm @ -10V", "-2.0V min / -4.0V max", 175,
     False, "Q_PMOS_GDS", "vishay/irf9540.pdf", "https://www.vishay.com/en/product/91078/",
     "Active", ""),
    # --- onsemi (Fairchild) QFET, TO-220-3LD ---
    ("onsemi", "FQP27P06", "FQP27P06", "pmos", 60, "27", 120,
     "70mOhm max @ Vgs=-10V, Id=-13.5A", "70 mOhm @ -10V", "-2.0V min / -4.0V max", 175,
     False, "FQP27P06", "onsemi/fqp27p06-d.pdf",
     "https://www.onsemi.com/products/discrete-power-modules/mosfets/"
     "low-medium-voltage-mosfets/fqp27p06",
     "Active", ""),
]


def num(s):
    """Leading number of a rating string ('110 (package limit 75A)' -> '110')."""
    return s.split()[0]


def build(row):
    (mfr, mpn, value, ttype, vds, idc, pd, rds, rds_short, vth, tj, logic,
     sym, ds, link, lifecycle, note) = row
    sign = "-" if ttype == "pmos" else ""
    ch = "N" if ttype == "nmos" else "P"
    i_disp = f"{sign}{num(idc)}A"
    desc = (f"{MFR[mfr]['short']} {value} {ch}-channel {MFR[mfr]['family']} power MOSFET, "
            f"{sign}{vds}V {i_disp}, RDS(on) {rds_short.replace(' @ ', ' max @ ')}"
            f"{', logic-level' if logic else ''}, TO-220AB")
    if note:
        desc += f" ({note})"
    kw = ["mosfet", "transistor", f"{ch.lower()}-channel", ttype, "power"]
    if logic:
        kw.append("logic-level")
    kw += ["through-hole", "to-220", f"{vds}V", value]
    if mpn != value:
        kw.append(mpn)
    return {
        **COMMON,
        "manufacturer": mfr, "unique_id": f"{mfr}-{mpn}", "mpn": mpn, "value": value,
        "part_locator": f"mosfet-{ch.lower()}ch-{vds}v-{num(idc)}a-to220",
        "description": desc,
        "datasheet": f"{DS}/{ds}",
        "manufacturer_link": link,
        "kicad_symbol": f"Transistor_FET:{sym}",
        "keywords": ",".join(kw),
        "lifecycle_status": lifecycle,
        "transistor_type": ttype, "v_ce_ds_max": f"{vds}V",
        # magnitudes, as the table's existing P-channel rows record them
        "i_c_d_max": f"{idc}A" if "(" not in idc
                     else f"{num(idc)}A ({idc.split('(', 1)[1]}",
        "power_dissipation": f"{pd}W (Tc=25C)",
        "rds_on": rds, "vgs_th": vth,
        "temp_operating_min": -55, "temp_operating_max": tj,
        "temp_storage_min": -55, "temp_storage_max": tj,
        "temp_junction_max": f"{tj}C",
    }


PARTS = [build(r) for r in CATALOG]


def main():
    write(OUTPUT_FILE, CREATED_BY, PARTS, "through-hole TO-220AB power MOSFETs")


if __name__ == "__main__":
    main()
