"""Shared emit logic for Nexperia Zener (voltage-regulator) diode families.

Each `run_3NN_<family>.py` defines its family metadata plus a per-type table
(transcribed from the datasheet's "Characteristics per type" tables) and calls
`emit()`. Output is dump_priority=0 / source=NULL — generated, never dumped to
static SQL.

The per-type `types` dict is keyed by the datasheet voltage code (e.g. "5V1",
"10") and maps to:
    {
        "test_current": "5mA",        # Iz at which Vz is specified
        "impedance_max": 60,          # rdif max at that Iz (ohms)
        "capacitance": 300,           # Cd max (pF)
        "izsm": 6.0,                  # non-repetitive peak reverse current (A)
        "grades": {"B": [5.0, 5.2], "C": [4.8, 5.4]},  # grade -> [Vz_min, Vz_max]
    }
Only grades actually listed for a voltage code appear; rdif/Cd/Izsm are
per-voltage (shared across grades).
"""
from pathlib import Path

GRADE_TOL = {"A": "1%", "B": "2%", "C": "5%"}
SYMBOL = "Device:D_Zener"

# INSERT column order. Named/column-qualified inserts, so this is independent of
# the physical schema column order (required by the schema-drift guard).
COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "zener_voltage", "zener_voltage_min",
    "zener_voltage_max", "tolerance", "test_current", "power_rating",
    "forward_voltage", "impedance_max", "capacitance", "peak_reverse_current",
]


def _sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def _nominal(code):
    """'5V1' -> '5.1V', '3V0' -> '3V', '10' -> '10V'."""
    val = float(code.replace("V", ".")) if "V" in code else float(code)
    return f"{val:g}V"


def _slug(package):
    return package.lower().replace("-", "").replace(" ", "")


def emit(output_file, created_by, *, prefix, package, footprint, power_rating,
         forward_voltage, datasheet, types, manufacturer="Nexperia",
         temp_operating=(-65.0, 150.0), temp_storage=(-65.0, 150.0),
         extra_tags="", symbol=SYMBOL, pin_count="2", dash=True,
         manufacturer_link=None):
    # mpn: Nexperia type numbers carry a dash (BZV55-C5V1); Vishay's BZX584C
    # does not (BZX584C5V1) -> dash=False. manufacturer_link defaults to the
    # Nexperia per-part page; pass a fixed URL for other vendors.
    pkg_slug = _slug(package)
    tag_tail = ("," + extra_tags) if extra_tags else ""
    rows = []
    for code, d in types.items():
        vz = _nominal(code)
        for letter, (vmin, vmax) in d["grades"].items():
            tol = GRADE_TOL[letter]
            mpn = f"{prefix}-{letter}{code}" if dash else f"{prefix}{letter}{code}"
            cap = d.get("capacitance")
            izsm = d.get("izsm")
            imp = d.get("impedance_max")
            rec = {
                "unique_id": f"{manufacturer}-{mpn}",
                "part_locator": f"diode-zener-{code.lower()}-{pkg_slug}",
                "mpn": mpn, "manufacturer": manufacturer,
                "package": package, "value": f"{vz} {tol}",
                "description": (
                    f"{manufacturer} {mpn} {vz} +/-{tol} Zener voltage "
                    f"regulator diode, {power_rating}, {package}"
                ),
                "datasheet": datasheet,
                "manufacturer_link": manufacturer_link or f"https://www.nexperia.com/product/{mpn}",
                "kicad_symbol": symbol, "kicad_footprint": footprint,
                "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
                "source": None, "dump_priority": 0, "tier": 2,
                "keywords": f"zener,voltage-regulator,smd,{tol}{tag_tail}",
                "pin_count": pin_count,
                "temp_operating_min": float(temp_operating[0]),
                "temp_operating_max": float(temp_operating[1]),
                "temp_storage_min": float(temp_storage[0]),
                "temp_storage_max": float(temp_storage[1]),
                "zener_voltage": vz,
                "zener_voltage_min": float(vmin), "zener_voltage_max": float(vmax),
                "tolerance": tol, "test_current": d["test_current"],
                "power_rating": power_rating, "forward_voltage": forward_voltage,
                "impedance_max": float(imp) if imp is not None else None,
                "capacitance": f"{cap}pF" if cap is not None else None,
                "peak_reverse_current": f"{izsm:g}A" if izsm is not None else None,
            }
            vals = ", ".join(_sql(rec[c]) for c in COLS)
            rows.append(f"INSERT INTO diodes_zener ({', '.join(COLS)}) VALUES ({vals});")

    lines = [
        f"-- Terra EDA Library - {manufacturer} {prefix} Zener voltage-regulator diodes",
        f"-- {package}, {power_rating}. E24 voltages x tolerance grades. Generated by {created_by}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
        *rows,
        "",
        "COMMIT;",
        "",
    ]
    Path(output_file).write_text("\n".join(lines))
    print(f"Generated {Path(output_file).name}: {len(rows)} parts")
    return len(rows)
