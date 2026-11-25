"""Shared row builder and writer for the through-hole BJT generators (run_32x, run_33x).

Each generator lists its parts as `Part` records transcribed from the manufacturer's
data sheet; `rows()` turns them into bjt rows and `write()` emits the SQL.

Pinout is the trap with leaded BJTs: TO-92 lead order depends on the maker and even
the packaging (2N3904 is E-B-C, BC547 C-B-E, BC640 E-C-B). Every Part states the
lead order its own data sheet gives (`pinout`, pin 1 first), and `rows()` checks it
against the pin names of the KiCad symbol it names, read from the stock
Transistor_BJT library. A mismatch stops the build rather than shipping a row whose
symbol would swap collector and emitter.
"""
import re
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KICAD_SYMBOLS = Path("/usr/share/kicad/symbols")
KICAD_FOOTPRINTS = Path("/usr/share/kicad/footprints")

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count", "sim_device",
    "sim_pins", "transistor_type", "channels", "v_ce_ds_max", "i_c_d_max",
    "power_dissipation", "hfe_typ", "rds_on", "vgs_th", "transition_freq",
    "temp_junction_max",
]

MANUFACTURERS = {  # short (unique_id prefix) -> manufacturer name
    "onsemi": "onsemi",
    "Central": "Central Semiconductor",
    "Diotec": "Diotec Semiconductor",
}

# Package -> stock footprint. Lead form matters for TO-92: bulk parts have straight
# leads on the 1.27 mm JEDEC pitch (TO-92_Inline); ammo-packed onsemi "TA" and
# Diotec parts come lead-formed to 2.54 mm (onsemi case 135AR, Diotec "Raster 2.54"),
# which is TO-92_Inline_Wide. TO-225 (onsemi case 77) has the TO-126 outline and its
# 2.28 mm lead pitch.
FOOTPRINTS = {
    "TO-92": "Package_TO_SOT_THT:TO-92_Inline",
    "TO-92 formed": "Package_TO_SOT_THT:TO-92_Inline_Wide",
    "TO-18": "Package_TO_SOT_THT:TO-18-3",
    "TO-39": "Package_TO_SOT_THT:TO-39-3",
    "TO-225": "Package_TO_SOT_THT:TO-126-3_Vertical",
    "TO-220": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "TO-247": "Package_TO_SOT_THT:TO-247-3_Vertical",
    "TO-3": "Package_TO_SOT_THT:TO-3",
}


@dataclass
class Part:
    short: str          # MANUFACTURERS key
    mpn: str            # orderable code, packaging suffix included
    value: str          # schematic label (the type number)
    polarity: str       # "npn" | "pnp"
    package: str        # FOOTPRINTS key
    pinout: str         # lead order from the data sheet, pin 1 first ("EBC")
    symbol: str         # Transistor_BJT symbol name
    vceo: str           # "40V"; prefixed "VCES " where the sheet rates only VCES
    ic: str             # "200mA" continuous
    pd: str             # "625mW (Ta=25C)" / "40W (Tc=25C)"
    hfe: str            # "100-300 @ Ic=10mA, Vce=1V"
    ft: str | None      # "300MHz min" / "300MHz typ" / None when the sheet gives none
    tj: str             # "150C"
    datasheet: str      # path under datasheets/
    packing: str        # "bulk" / "ammo" / "rail" ...
    lifecycle: str = "Active"
    link: str | None = None
    darlington: bool = False
    note: str = ""      # extra description text (grade, family role)
    keywords: str = ""  # extra comma-separated keywords


def _symbol_pins():
    """Map symbol name -> pin-name string in pin-number order ("EBC"), with
    `extends` resolved, from the stock Transistor_BJT library."""
    lib = KICAD_SYMBOLS / "Transistor_BJT.kicad_sym"
    if not lib.is_file():
        return None
    text = lib.read_text()
    syms = {}
    for block in re.split(r'\n\t\(symbol "', text)[1:]:
        name = block.split('"', 1)[0]
        ext = re.search(r'\(extends "([^"]+)"\)', block)
        pins = re.findall(r'\(pin \w+ \w+.*?\(name "([^"]*)".*?\(number "([^"]*)"',
                          block, re.S)
        syms[name] = (ext.group(1) if ext else None, pins)
    out = {}
    for name in syms:
        ext, pins = syms[name]
        while not pins and ext:
            ext, pins = syms[ext]
        by_num = {num: nm for nm, num in pins}
        out[name] = "".join(by_num[n] for n in sorted(by_num, key=int))
    return out


def _token(v):
    return v.split()[-1].lower().replace(" ", "")


def rows(parts, created_by):
    sym_pins = _symbol_pins()
    if sym_pins is None:
        print("  warning: stock Transistor_BJT library not found; pinout check skipped")
    for p in parts:
        if p.short not in MANUFACTURERS:
            raise SystemExit(f"{p.mpn}: unknown manufacturer {p.short}")
        if sorted(p.pinout) != ["B", "C", "E"]:
            raise SystemExit(f"{p.mpn}: bad pinout {p.pinout}")
        if sym_pins is not None:
            if p.symbol not in sym_pins:
                raise SystemExit(f"{p.mpn}: no symbol Transistor_BJT:{p.symbol}")
            if sym_pins[p.symbol][:3] != p.pinout or len(sym_pins[p.symbol]) != 3:
                raise SystemExit(f"{p.mpn}: data sheet pinout {p.pinout} but "
                                 f"Transistor_BJT:{p.symbol} is {sym_pins[p.symbol]}")
            if p.symbol.startswith("Q_") and ("Darlington" in p.symbol) != p.darlington:
                raise SystemExit(f"{p.mpn}: Darlington flag disagrees with {p.symbol}")
        footprint = FOOTPRINTS[p.package]
        lib, fp = footprint.split(":")
        if KICAD_FOOTPRINTS.is_dir() and not (
                KICAD_FOOTPRINTS / f"{lib}.pretty" / f"{fp}.kicad_mod").is_file():
            raise SystemExit(f"{p.mpn}: missing footprint {footprint}")
        datasheet = REPO / "datasheets" / p.datasheet
        if not datasheet.is_file():
            raise SystemExit(f"{p.mpn}: missing datasheet {datasheet}")

        pkg = p.package.split()[0]
        kind = f"{p.polarity.upper()} {'Darlington' if p.darlington else 'BJT'}"
        leads = "-".join(p.pinout)
        desc = (f"{MANUFACTURERS[p.short]} {p.value} {kind}, {p.vceo} {p.ic}, "
                f"Pd {p.pd}, hFE {p.hfe}")
        if p.ft:
            desc += f", fT {p.ft}"
        desc += f", {pkg} {leads}"
        if p.package == "TO-92 formed":
            desc += " (leads formed to 2.54mm)"
        desc += f", {p.packing}"
        if p.note:
            desc += f"; {p.note}"
        darl = "-darlington" if p.darlington else ""
        kw = ["bjt", p.polarity, "transistor", "through-hole", pkg]
        if p.darlington:
            kw.append("darlington")
        kw += [k for k in p.keywords.split(",") if k]
        kw.append(p.value)
        yield {
            "unique_id": f"{p.short}-{p.mpn.replace(' ', '-')}",
            "part_locator": (f"bjt-{p.polarity}{darl}-{_token(p.vceo)}-{_token(p.ic)}-"
                             f"{pkg.lower().replace('-', '')}"),
            "mpn": p.mpn, "manufacturer": MANUFACTURERS[p.short], "package": pkg,
            "value": p.value, "description": desc,
            "datasheet": "${TERRA_EDA_LIB}/datasheets/" + p.datasheet,
            "manufacturer_link": p.link,
            "kicad_symbol": f"Transistor_BJT:{p.symbol}", "kicad_footprint": footprint,
            "lifecycle_status": p.lifecycle, "rohs": "Yes", "allow_substitution": "No",
            "tracking": "No", "source": None, "dump_priority": 0, "tier": 2,
            "keywords": ",".join(kw), "pin_count": "3",
            # Darlingtons have no built-in SPICE model; plain BJTs map the leads onto
            # ngspice's C/B/E in the data sheet's order (same as the stock symbol).
            "sim_device": None if p.darlington else p.polarity.upper(),
            "sim_pins": None if p.darlington else " ".join(
                f"{i + 1}={c}" for i, c in enumerate(p.pinout)),
            "transistor_type": p.polarity, "channels": 1,
            "v_ce_ds_max": p.vceo, "i_c_d_max": p.ic, "power_dissipation": p.pd,
            "hfe_typ": p.hfe, "rds_on": None, "vgs_th": None,
            "transition_freq": p.ft, "temp_junction_max": p.tj,
        }


def _sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def write(output_file, title, created_by, parts):
    recs = list(rows(parts, created_by))
    ids = [r["unique_id"] for r in recs]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"duplicate unique_id: {dupes}")
    lines = [
        f"-- Terra EDA Library - {title}",
        f"-- Generated by {created_by}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(_sql(r[c]) for c in COLS)
        lines.append(f"INSERT INTO bjt ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    output_file.write_text("\n".join(lines))
    print(f"Generated {output_file.name}: {len(recs)} parts")
    not_active = [r for r in recs if r["lifecycle_status"] != "Active"]
    for r in not_active:
        print(f"  {r['lifecycle_status']}: {r['mpn']}")
