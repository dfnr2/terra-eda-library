"""Shared row builder, spec decoders and SQL writer for the crystals_th and
crystals_smt generators.

Each ``run_3x0_*.py`` script lists one crystal family's orderable codes, decodes
each code with that family's part-numbering key (transcribed into the script from
the datasheet) and calls ``row()`` once per code, then ``write()``. The column list,
value formats and the frequency-use keywords live here so every family formats
alike.

Value formats: frequency ``3.579545MHz`` / ``32.768kHz`` (also the schematic value);
load_capacitance ``18pF`` / ``12.5pF`` / ``series``; tolerance and stability
``±20ppm`` (tuning forks: stability is the parabolic coefficient
``-0.034ppm/°C²``); esr_ohm ``200Ω`` / ``35kΩ`` (maximum, same name and sign as
capacitors_electrolytic_th); drive_level ``1000µW max``; oscillation_mode
``fundamental`` / ``3rd overtone`` / ``tuning fork``.
"""
from pathlib import Path

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking", "standards_version",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "frequency", "load_capacitance", "frequency_tolerance", "frequency_stability",
    "esr_ohm", "oscillation_mode", "drive_level",
]

DS_ROOT = "${TERRA_EDA_LIB}/datasheets"

# Where a frequency turns up, for search. Machine uses are from the original
# service manuals and schematics (plans/vintage-computer-parts.md, phase 6 results).
FREQ_USES = {
    1.0: ["KIM-1", "SYM-1", "6502 1MHz"],
    1.8432: ["UART baud", "MC14411"],
    2.0: ["Altair 8800"],
    2.4576: ["UART baud", "Altair 88-2SIO"],
    3.579545: ["NTSC colorburst", "color burst", "Netronics Elf II", "OSI C4P"],
    3.6864: ["UART baud"],
    3.93216: ["OSI C1P", "Ohio Scientific"],
    4.0: ["AIM-65", "OSI C2", "North Star"],
    4.194304: ["2^22", "clock divider"],
    4.433618: ["PAL colorburst", "color burst", "VIC-20 PAL"],
    4.433619: ["PAL colorburst", "color burst", "VIC-20 PAL"],
    4.9152: ["UART baud"],
    7.3728: ["UART baud"],
    8.0: ["Cromemco ZPU", "North Star ZPB-A", "OSI 510"],
    9.8304: ["UART baud"],
    10.738635: ["3x NTSC colorburst", "TMS9918", "TI-99/4A"],
    11.0592: ["UART baud", "8051"],
    12.0: ["OSI C4P"],
    14.31818: ["4x NTSC colorburst", "Apple II", "Apple 1", "IBM PC", "8284"],
    14.7456: ["UART baud"],
    17.734475: ["4x PAL colorburst", "C64 PAL"],
    18.0: ["8224", "8080 2MHz", "IMSAI"],
    18.432: ["8224", "Heathkit H8", "UART baud"],
    19.6608: ["UART baud"],
    22.1184: ["UART baud"],
    48.0: ["TIM9904", "TI-99/4A"],
}


def fmt_freq(mhz):
    """3.579545 -> '3.579545MHz', 4.0 -> '4MHz', 0.032768 -> '32.768kHz'."""
    if mhz < 1:
        return f"{mhz * 1000:f}".rstrip("0").rstrip(".") + "kHz"
    return f"{mhz:f}".rstrip("0").rstrip(".") + "MHz"


def fmt_cl(cl):
    return "series" if cl == "S" else f"{cl:g}pF"


def fmt_esr(ohm):
    return f"{ohm / 1000:g}kΩ" if ohm >= 1000 else f"{ohm:g}Ω"


def band(table, mhz):
    """First value whose (lo, hi) band holds mhz; table is [((lo, hi), value), ...]."""
    for (lo, hi), v in table:
        if lo <= mhz <= hi:
            return v
    raise ValueError(f"{mhz} MHz outside the datasheet table")


# Abracon option letters, common to the AB, ABL, ABLS, ABM3, ABM3B and ABM8G keys
# (each datasheet's "Options and Part Identification" table).
ABR_TEMP = {"A": (-10, 60), "B": (-20, 70), "C": (-30, 70), "N": (-30, 85),
            "D": (-40, 85), "E": (0, 70), "J": (-40, 105), "K": (-40, 125),
            "L": (-55, 125)}
ABR_TOL = {"1": 10, "7": 15, "2": 20, "3": 25, "4": 30}
ABR_STAB = {"U": 10, "G": 15, "X": 20, "W": 25, "Y": 30, "H": 35, "Q": 100, "R": 150}


def abracon_options(opts, std):
    """Decode an Abracon option string such as 'B2', 'B2F', 'B4' or '18-D2Y'.

    std holds the family's blank-means-standard values: cl, temp, tol, stab.
    Returns (cl, temp, tol, stab, fund) where fund is True for the F option
    (fundamental AT above 24 MHz)."""
    cl = std["cl"]
    parts = opts.split("-")
    if parts[0].replace(".", "").isdigit():
        cl = float(parts.pop(0))
    code = "-".join(parts)
    fund = code.endswith("F")
    code = code[:-1] if fund else code
    temp, tol, stab = std["temp"], std["tol"], std["stab"]
    if code[:1] in ABR_TEMP:
        temp, code = ABR_TEMP[code[0]], code[1:]
    if code[:1] in ABR_TOL:
        tol, code = ABR_TOL[code[0]], code[1:]
    if code[:1] in ABR_STAB:
        stab, code = ABR_STAB[code[0]], code[1:]
    if code:
        raise ValueError(f"undecoded Abracon option {opts!r}")
    return cl, temp, tol, stab, fund


def row(*, created_by, manufacturer, series, mpn, mhz, cl, tolerance, stability, esr,
        mode, drive, temp, package, pins, footprint, symbol, datasheet, mfr_link=None,
        extra_keywords=()):
    """One crystal row. tolerance/stability are ppm numbers (stability may be a
    preformatted tuning-fork coefficient string); esr is the max in ohms."""
    value = fmt_freq(mhz)
    cl_s = fmt_cl(cl)
    tol_s = f"±{tolerance:g}ppm"
    stab_s = stability if isinstance(stability, str) else f"±{stability:g}ppm"
    pkg_slug = package.lower().replace("/", "").replace(" ", "-").replace(".", "")
    uses = FREQ_USES.get(round(mhz, 6), [])
    kw = [value, "crystal", "xtal", "quartz", package, manufacturer, series,
          cl_s if cl == "S" else f"{cl_s} load", *uses, *extra_keywords]
    return {
        "unique_id": f"{manufacturer}-{mpn}",
        "part_locator": f"xtal-{value.lower()}-{cl_s.lower()}-{pkg_slug}",
        "mpn": mpn, "manufacturer": manufacturer, "package": package, "value": value,
        "description": (f"Crystal {manufacturer} {series} {value} {tol_s} {cl_s}"
                        f"{'' if cl == 'S' else ' load'} {package}"),
        "datasheet": f"{DS_ROOT}/{datasheet}", "manufacturer_link": mfr_link,
        "kicad_symbol": symbol, "kicad_footprint": footprint,
        "lifecycle_status": "Active", "rohs": "Yes",
        "allow_substitution": "No", "tracking": "No", "standards_version": "1.0",
        "created_by": created_by, "source": None, "dump_priority": 0, "tier": 2,
        "keywords": ", ".join(dict.fromkeys(kw)),
        "pin_count": str(pins),
        "temp_operating_min": temp[0], "temp_operating_max": temp[1],
        "frequency": value, "load_capacitance": cl_s, "frequency_tolerance": tol_s,
        "frequency_stability": stab_s, "esr_ohm": fmt_esr(esr),
        "oscillation_mode": mode, "drive_level": drive,
    }


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def write(output_file, table, title, created_by, recs):
    """Write the INSERTs, failing on a duplicate unique_id rather than dropping rows."""
    ids = [r["unique_id"] for r in recs]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"duplicate unique_id: {dupes}")
    lines = [
        f"-- Terra EDA Library - {table} {title}",
        f"-- Generated by {created_by}. dump_priority=0, source=NULL: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO {table} ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    Path(output_file).write_text("\n".join(lines))
    print(f"Generated {Path(output_file).name}: {len(recs)} parts")
