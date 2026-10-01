"""Shared emit helpers for relays_ssr generators.

Each manufacturer generator loads its datasheet-harvested catalog
(`<mfr>_catalog.json`, one entry per package variant) and calls emit(), which
turns every entry into a column-qualified INSERT. Symbols and footprints are
KiCad stock parts; parts without a trusted symbol or footprint, or whose
footprint doesn't fit the package, are printed on every run for review.

Output is dump_priority=0 / source=NULL -- generated, never dumped to static SQL.
"""
import json
import re
from pathlib import Path

TABLE = "relays_ssr"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution",
    "tracking", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max", "temp_storage_min",
    "temp_storage_max", "contact_form", "channels", "load_type",
    "voltage_rating", "current_rating", "on_resistance", "off_capacitance",
    "led_operate_current", "led_forward_voltage", "control_voltage",
    "isolation_voltage", "turn_on_time", "turn_off_time",
]

TAIL = [
    "contact_form", "channels", "load_type", "voltage_rating", "current_rating",
    "on_resistance", "off_capacitance", "led_operate_current",
    "led_forward_voltage", "control_voltage", "isolation_voltage",
    "turn_on_time", "turn_off_time",
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def slug(s):
    return re.sub(r"[^a-z0-9.]+", "-", str(s).lower()).strip("-")


def _first(s):
    """Leading rating of a value string: '2.5Ohm max @ IF=5mA' -> '2.5Ohm'."""
    return str(s).split()[0] if s else None


def row(p, manufacturer, family, value):
    mpn = p["mpn"]
    form = p["contact_form"]
    rating = " ".join(x for x in (p.get("voltage_rating"), p.get("current_rating")) if x)
    ron = _first(p.get("on_resistance"))
    life = p.get("lifecycle_status") or "Active"
    desc = f"{manufacturer} {mpn} {form} {p.get('load_type') or ''} {family}"
    desc = " ".join(desc.split())
    desc += f", {rating}" if rating else ""
    desc += f", {ron} on" if ron else ""
    desc += f", {p['package']}"
    if p.get("replaces"):
        desc += f", replaces {p['replaces']}"
    if p.get("replaced_by"):
        desc += f", replaced by {p['replaced_by']}"
    if life != "Active":
        desc += f" ({life})"
    if not p.get("kicad_symbol") or not p.get("kicad_footprint"):
        desc += " -- REVIEW: missing symbol or footprint"
    rec = {
        "unique_id": f"{manufacturer}-{mpn}",
        "part_locator": "-".join(slug(x) for x in (
            "ssr", form, p.get("voltage_rating"), p.get("current_rating"),
            p["package"]) if x),
        "mpn": mpn, "manufacturer": manufacturer, "package": p["package"],
        "value": value, "description": desc,
        "datasheet": "${TERRA_EDA_LIB}/" + p["datasheet"],
        "manufacturer_link": p.get("manufacturer_link"),
        "kicad_symbol": p.get("kicad_symbol"),
        "kicad_footprint": p.get("kicad_footprint"),
        "lifecycle_status": life, "rohs": p.get("rohs"),
        "allow_substitution": "No", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
        "keywords": ",".join(k for k in (
            "ssr", "solid-state relay", family.lower(), slug(form),
            (p.get("mount") or "").lower(), manufacturer.lower()) if k),
        "pin_count": str(p["pin_count"]) if p.get("pin_count") else None,
        **{k: p.get(k) for k in ("temp_operating_min", "temp_operating_max",
                                  "temp_storage_min", "temp_storage_max")},
        **{k: p.get(k) for k in TAIL},
    }
    vals = ", ".join(sql(rec.get(c)) for c in COLS)
    return f"INSERT INTO {TABLE} ({', '.join(COLS)}) VALUES ({vals});"


def emit(script, catalogs, family, value_of, title):
    """Write <table>_generated_<NNN_name>.sql next to `script` from its catalogs."""
    script = Path(script)
    catalogs = [catalogs] if isinstance(catalogs, str) else list(catalogs)
    data = [json.loads(script.with_name(c).read_text()) for c in catalogs]
    manufacturer = data[0]["manufacturer"]
    catalog = ", ".join(catalogs)
    rows, seen, review = [], set(), []
    for p in (p for d in data for p in d["parts"]):
        uid = f"{manufacturer}-{p['mpn']}"
        if uid in seen:
            raise SystemExit(f"duplicate unique_id {uid} in {catalog}")
        seen.add(uid)
        rows.append(row(p, manufacturer, family, value_of(p)))
        if not p.get("kicad_symbol") or not p.get("kicad_footprint"):
            review.append(f"  REVIEW {p['mpn']}: symbol={p.get('kicad_symbol')} "
                          f"footprint={p.get('kicad_footprint')}")
        elif p.get("footprint_check") == "mismatch":
            # "close" is accepted: a stock IPC-style package footprint whose pads
            # differ slightly from the vendor's recommended land pattern.
            review.append(f"  footprint mismatch {p['mpn']}: {p['kicad_footprint']}")
    out = script.with_name(
        f"{TABLE}_generated_{script.stem.removeprefix('run_')}.sql")
    out.write_text("\n".join([
        f"-- Terra EDA Library - {title}",
        f"-- Generated by {script.name} from {catalog}. dump_priority=0, source=NULL.",
        "", "BEGIN TRANSACTION;", "", *rows, "", "COMMIT;", ""]))
    print(f"Generated {out.name}: {len(rows)} parts")
    for line in review:
        print(line)
    return len(rows)
