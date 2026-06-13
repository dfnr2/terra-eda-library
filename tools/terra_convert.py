#!/usr/bin/env python3
"""Match a KiCad project's parts against the terra library (read-only).

Stages 1-3 of the project-conversion pipeline: parse a ``.kicad_sch``, extract
each placed part, and classify it against ``db/terra.db`` into tiers:

  A       drop-in     -- an exact MPN already exists in terra
  B       substitute  -- terra has a spec-equivalent part (value + package)
  REVIEW  conflict    -- a passive whose Value field disagrees with its MPN
                         (copy/paste error); never substituted blindly
  C       gap         -- terra has nothing suitable; a candidate for new terra work

On the drop-in matches it also raises read-only recommendations that drive the
(future) write stage: when the schematic part carries datasheet/RoHS/link data
terra lacks (terra-update), when the match is a CERN part (promote to a native
table), and when a CERN match's footprint differs from the schematic's
(footprint-review). It NEVER modifies the schematic or the database.

Usage::

    python tools/terra_convert.py path/to/board.kicad_sch [--db db/terra.db] [--json]
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

# Categories whose Value field holds a comparable electrical spec (vs. an IC's
# Value, which is a part number/function and not comparable to terra's value).
VALUE_BEARING = ("Resistor", "Capacitor", "Ferrite", "Inductor")


# --------------------------------------------------------------------------- #
# Stage 1: extract parts from the schematic
# --------------------------------------------------------------------------- #

@dataclass
class Part:
    """One placed schematic symbol, reduced to the fields we match on."""

    ref: str
    lib_id: str
    value: str
    footprint: str
    mpn: str
    manufacturer: str
    datasheet: str
    mfr_link: str
    rohs_link: str
    tolerance: str = ""
    power: str = ""


def _prop(chunk: str, key: str) -> str:
    """Return the value of ``(property "key" "value" ...)`` in a symbol chunk."""
    m = re.search(r'\(property "%s" "((?:[^"\\]|\\.)*)"' % re.escape(key), chunk)
    return m.group(1) if m else ""


def parse_schematic(path: Path) -> list[Part]:
    """Extract the real (BOM-bearing) parts from a KiCad ``.kicad_sch`` file.

    Splits the s-expression text on each ``(lib_id "..."`` -- the properties of
    an instance follow its lib_id and precede the next one, so each split chunk
    is one symbol. Power/flag symbols (``power:*``) and unannotated references
    (``#PWR``...) carry no BOM and are dropped.

    Example::

        >>> from tools.terra_convert import parse_schematic
        >>> from pathlib import Path
        >>> parts = parse_schematic(Path("mainboard.kicad_sch"))
        >>> parts[0].ref, parts[0].mpn
        ('R13', 'RT0603FRE07130RL')
    """
    text = path.read_text(encoding="utf-8")
    parts: list[Part] = []
    for chunk in re.split(r'\(lib_id "', text)[1:]:
        lib_id = chunk.split('"', 1)[0]
        ref = _prop(chunk, "Reference")
        if lib_id.startswith("power:") or ref.startswith("#") or not ref:
            continue
        parts.append(
            Part(
                ref=ref,
                lib_id=lib_id,
                value=_prop(chunk, "Value"),
                footprint=_prop(chunk, "Footprint"),
                mpn=_prop(chunk, "Manufacturer PN"),
                manufacturer=_prop(chunk, "Manufacturer"),
                datasheet=_prop(chunk, "Datasheet"),
                mfr_link=_prop(chunk, "Manufacturer Link"),
                rohs_link=_prop(chunk, "RoHS Europe Document Link"),
                tolerance=_prop(chunk, "Tolerance"),
                power=_prop(chunk, "Power Rating"),
            )
        )
    return parts


# --------------------------------------------------------------------------- #
# Normalizers and value parsing (the matching keys)
# --------------------------------------------------------------------------- #

def norm_mpn(mpn: str) -> str:
    """Canonical MPN for equality: strip whitespace, upper-case."""
    return re.sub(r"\s+", "", mpn).upper()


def package_of(footprint: str) -> str:
    """Extract the imperial package code (e.g. ``0603``) from a footprint id."""
    m = re.search(r"_(\d{4})_", footprint)
    return m.group(1) if m else ""


def category_of(ref: str, lib_id: str) -> str:
    """Classify a part by reference-designator prefix (the reliable signal)."""
    prefix = re.match(r"[A-Za-z]+", ref)
    prefix = prefix.group(0).upper() if prefix else ""
    table = {
        "R": "Resistor", "C": "Capacitor", "FB": "Ferrite", "L": "Inductor",
        "D": "Diode/TVS", "LED": "LED", "U": "IC", "Q": "Transistor",
        "J": "Connector", "P": "Connector", "TP": "TestPoint",
        "BT": "Battery", "BAT": "Battery",
    }
    if lib_id.startswith("terra:"):
        return "Already terra"
    return table.get(prefix, "Other")


def parse_resistance(value: str) -> float | None:
    """Parse a resistance to ohms from a clean value or a descriptive string.

    Handles the EIA forms ``2.2k`` / ``2K2`` / ``130R`` / ``130`` and also pulls
    the value out of legacy descriptive fields such as
    ``"RES Yageo 300 ohm 1% 1/10 W 0603"``. The letter (R/K/M/G) is a multiplier;
    when digits follow it (``2K2``) it also stands in for the decimal point.
    """
    clean = re.sub(r"\s|ohm|Ω", "", value.strip(), flags=re.I).upper()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([RKMG])?(\d+)?", clean)
    if m:
        head, suffix, tail = m.groups()
    else:
        m = re.search(r"(\d+(?:\.\d+)?)\s*([RKMG])?\s*(?:ohm|Ω)", value, flags=re.I)
        if not m:
            return None
        head, suffix, tail = m.group(1), (m.group(2) or "").upper() or None, None
    mult = {"R": 1.0, "K": 1e3, "M": 1e6, "G": 1e9, None: 1.0}[suffix]
    magnitude = float(f"{head}.{tail}") if tail else float(head)
    return magnitude * mult


def parse_capacitance(value: str) -> float | None:
    """Parse a capacitance to farads (``0.1uF`` == ``100n`` == 1e-7).

    Accepts a clean value or a legacy descriptive field such as
    ``"CAP KEMET MLCC 1 uF X7R 10% 16V 0603"``.
    """
    clean = value.strip().lower().replace("µ", "u").replace(" ", "").replace("f", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([pnum]?)(\d+)?", clean)
    if m:
        head, suffix, tail = m.groups()
    else:
        m = re.search(r"(\d+(?:\.\d+)?)\s*([pnumµ])\s*f", value, flags=re.I)
        if not m:
            return None
        head, suffix, tail = m.group(1), m.group(2).lower().replace("µ", "u"), None
    mult = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1.0}[suffix or ""]
    magnitude = float(f"{head}.{tail}") if tail else float(head)
    return magnitude * mult


def resistance_from_mpn(mpn: str) -> float | None:
    """Decode the resistance a Yageo RC/RT MPN encodes (``RT0603FRE07130RL`` -> 130).

    Yageo chip-resistor part numbers carry the EIA value code between the ``07``
    process marker and the trailing packaging ``L``. Returns None for MPNs that
    don't follow this scheme (we then cannot cross-check the value).
    """
    m = re.search(r"07([0-9]+[RKM]?[0-9]*)L$", mpn.upper())
    return parse_resistance(m.group(1)) if m else None


def capacitance_from_mpn(mpn: str) -> float | None:
    """Decode the capacitance a KEMET C-series MPN encodes (``C0603C104...`` -> 1e-7).

    The three-digit EIA code after the second ``C`` is two significant figures
    times a power-of-ten exponent, in picofarads (``104`` = 10 x 10^4 pF = 100 nF).
    """
    m = re.search(r"^C\d{4}C(\d)(\d)(\d)", mpn.upper())
    if not m:
        return None
    significand = int(m.group(1) + m.group(2))
    exponent = int(m.group(3))
    return significand * (10 ** exponent) * 1e-12


def parse_tolerance(text: str) -> float | None:
    """Percent tolerance from ``1%`` / ``0.1%`` / a descriptive field; else None."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    return float(m.group(1)) if m else None


def parse_power(text: str) -> float | None:
    """Power rating in watts from ``1/10W`` / ``1/4 W`` / ``0.25W``; else None."""
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*W", text, flags=re.I)
    if m:
        return int(m.group(1)) / int(m.group(2))
    m = re.search(r"(\d+(?:\.\d+)?)\s*W", text, flags=re.I)
    return float(m.group(1)) if m else None


def dielectric_of(text: str) -> str:
    """Dielectric class (C0G/X7R/X5R/...) from a value/material string, upper-case."""
    m = re.search(r"\b(C0G|NP0|X7R|X7S|X6S|X5R|Y5V|Z5U)\b", text, flags=re.I)
    return m.group(1).upper() if m else ""


def voltage_of(text: str) -> float | None:
    """Working-voltage rating in volts from a ``16V`` token; else None.

    The leading word boundary avoids matching the ``5V`` glued inside a
    dielectric code like ``Y5V`` (only a standalone number meets ``\\b\\d``).
    """
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*V\b", text)
    return float(m.group(1)) if m else None


def composition_of_mpn(mpn: str) -> str:
    """Yageo resistor composition from MPN prefix (RT -> Thin Film, RC -> Thick Film)."""
    u = mpn.upper()
    return "Thin Film" if u.startswith("RT") else "Thick Film" if u.startswith("RC") else ""


def _close(a: float | None, b: float | None) -> bool:
    """True if two parsed magnitudes are the same E-series value."""
    return a is not None and b is not None and math.isclose(a, b, rel_tol=1e-3)


def _fmt(category: str, magnitude: float) -> str:
    """Human-readable magnitude for a conflict message."""
    return f"{magnitude:g} ohm" if category == "Resistor" else f"{magnitude:g} F"


def value_conflict(category: str, sch_value: str, terra_value: str) -> bool:
    """True if a part's schematic value disagrees with its matched terra part.

    Compares numerically for parametric passives (so ``0.1uF`` == ``100n``) and
    by normalized string otherwise -- which catches a legacy ferrite labelled
    120R whose MPN-matched terra part is 220R. Absent values never conflict.
    """
    if not sch_value or not terra_value:
        return False
    parse = (parse_resistance if category == "Resistor"
             else parse_capacitance if category == "Capacitor" else None)
    if parse:
        a, b = parse(sch_value), parse(terra_value)
        if a is not None and b is not None:
            return not _close(a, b)
    left = re.sub(r"\s+", " ", sch_value.strip().lower())
    right = re.sub(r"\s+", " ", terra_value.strip().lower())
    return left != right


# --------------------------------------------------------------------------- #
# Stage 2: terra index + matching
# --------------------------------------------------------------------------- #

@dataclass
class TerraIndex:
    """Lookup structures built once from terra.db."""

    # norm_mpn -> the matched terra row's relevant columns
    by_mpn: dict[str, dict[str, str]]
    # category -> list of candidate dicts (mag, package, mpn, tier + quality dims)
    passives: dict[str, list[dict]]


def load_terra(db_path: Path) -> TerraIndex:
    """Index every terra part by MPN, plus parametric passives by value+package.

    Reads the database read-only; the dumped/served DB is the source of truth a
    client matches against, via the shared core columns (``mpn``, ``value``,
    ``package``, ``tier``, plus the link columns used for richness checks).
    """
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    skip = {"tags", "user_tags", "terra_tier_config", "terra_tag_config",
            "active_tagged_ids"}
    tables = [
        r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%\\_v' ESCAPE '\\'"
        )
        if r[0] not in skip
    ]

    by_mpn: dict[str, dict[str, str]] = {}
    passives: dict[str, list[dict]] = {"Resistor": [], "Capacitor": []}
    for table in tables:
        cols = {r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')}
        if "mpn" not in cols:
            continue
        parser = (parse_resistance if table.startswith("resistors")
                  else parse_capacitance if table.startswith("capacitors") else None)
        cat = ("Resistor" if table.startswith("resistors")
               else "Capacitor" if table.startswith("capacitors") else None)
        for row in conn.execute(f'SELECT * FROM "{table}"'):
            mpn = (row["mpn"] or "").strip()
            if mpn:
                by_mpn.setdefault(norm_mpn(mpn), {
                    "table": table,
                    "uid": row["unique_id"],
                    "value": row["value"] or "",
                    "datasheet": row["datasheet"] or "",
                    "manufacturer_link": row["manufacturer_link"] or "",
                    "rohs_document_link": row["rohs_document_link"] or "",
                    "footprint": row["kicad_footprint"] or "",
                })
            if parser and cat:
                mag = parser(row["value"] or "")
                if mag is not None:
                    cand = {"mag": mag, "package": row["package"] or "", "mpn": mpn,
                            "tier": row["tier"] or 0, "tolerance": parse_tolerance(row["tolerance"] or "")}
                    if cat == "Capacitor":
                        cand["voltage"] = row["voltage_rating_v"]
                        cand["dielectric"] = (row["dielectric_class"] or "").upper()
                    else:  # Resistor
                        cand["power"] = parse_power(row["power_rating"] or "")
                        cand["composition"] = row["composition"] or ""
                    passives[cat].append(cand)
    conn.close()
    return TerraIndex(by_mpn=by_mpn, passives=passives)


@dataclass
class Match:
    """The outcome of matching one part."""

    tier: str                    # "A" | "B" | "REVIEW" | "C"
    target: str                  # "table:unique_id" (A), candidate mpn (B), or ""
    note: str = ""
    flags: list[str] = field(default_factory=list)


def _recommendations(part: Part, row: dict[str, str]) -> list[str]:
    """Read-only flags for an exact-MPN match that drive the (future) write stage.

    CERN entries are sparse, so a hand-curated schematic part that matches one is
    the better source: port it (params + hand-curated footprint) into a native
    table and DELETE the CERN entry, rather than trying to enrich CERN (notes
    #3, #4). For a match to a NATIVE table, if the schematic carries link data
    the terra part lacks, the native part should be updated from the schematic
    (note #2).
    """
    if row["table"].startswith("cern_"):
        return ["PORT curated schematic part -> native table, then DELETE this CERN entry"]
    missing = [
        name for name, sch_value, terra_value in (
            ("datasheet", part.datasheet, row["datasheet"]),
            ("manufacturer_link", part.mfr_link, row["manufacturer_link"]),
            ("rohs_link", part.rohs_link, row["rohs_document_link"]),
        )
        if sch_value.strip() and not terra_value.strip()
    ]
    return [f"update native terra part: schematic has {', '.join(missing)}"] if missing else []


def _best_passive(category: str, part: Part, cands: list[dict]) -> tuple[dict | None, str]:
    """Pick the safest spec-equivalent passive from same value+package candidates.

    Enforces meet-or-exceed on the quality dimensions so a substitute is never
    weaker than the original: capacitors must match dielectric and rate >= the
    required voltage; resistors must rate >= the required power and <= the
    required tolerance, preferring the same composition. Returns ``(None, why)``
    when terra has the value/package but nothing meets spec -- a real gap, not an
    unsafe substitution.
    """
    if category == "Capacitor":
        req_diel = dielectric_of(part.value)
        req_v = voltage_of(part.value)
        ok = [c for c in cands
              if (not req_diel or c.get("dielectric") == req_diel)
              and (req_v is None or (c.get("voltage") is not None and c["voltage"] >= req_v))]
        if not ok:
            return None, f"terra has this value/package but none meet {req_diel or 'dielectric'} >= {req_v or '?'}V"
        best = min(ok, key=lambda c: (c["voltage"] if c["voltage"] is not None else 1e9, c["tier"]))
        v = best["voltage"]
        label = f"{best.get('dielectric', '')} {f'{v:g}V' if v is not None else ''}".strip()
        return best, f"spec-equivalent: {label} ({len(ok)} meet spec)"

    # Resistor
    req_pow = parse_power(part.power) or parse_power(part.value)
    req_tol = parse_tolerance(part.tolerance) or parse_tolerance(part.value)
    req_comp = composition_of_mpn(part.mpn)
    ok = [c for c in cands
          if (req_pow is None or (c.get("power") is not None and c["power"] >= req_pow))
          and (req_tol is None or (c.get("tolerance") is not None and c["tolerance"] <= req_tol))]
    if not ok:
        return None, f"terra has this value/package but none meet {req_tol or '?'}% / {req_pow or '?'}W"
    best = min(ok, key=lambda c: (
        0 if req_comp and c.get("composition") == req_comp else 1,
        0 if req_tol is not None and c.get("tolerance") == req_tol else 1,
        c["tier"]))
    bits = [best.get("composition", ""),
            f"{best['tolerance']:g}%" if best.get("tolerance") is not None else "",
            f"{best['power']:g}W" if best.get("power") is not None else ""]
    return best, "spec-equivalent: " + " ".join(b for b in bits if b) + f" ({len(ok)} meet spec)"


def match_part(part: Part, idx: TerraIndex) -> Match:
    """Classify a part into tier A (MPN), B (spec), REVIEW (value/MPN), or C (gap)."""
    cat = category_of(part.ref, part.lib_id)
    nm = norm_mpn(part.mpn)
    terra_row = idx.by_mpn.get(nm) if nm else None

    # Note #1: for parametric passives the Value field and the MPN each encode the
    # value, so a disagreement is a copy/paste error -- route to REVIEW and never
    # substitute on an untrusted value. Checked first so it fires whether or not
    # the MPN is already in terra. The MPN's true value comes from the matched
    # terra row when known, else from decoding the MPN.
    encoded = displayed = None
    if cat in idx.passives:
        parse = parse_resistance if cat == "Resistor" else parse_capacitance
        from_mpn = resistance_from_mpn if cat == "Resistor" else capacitance_from_mpn
        displayed = parse(part.value)
        encoded = parse(terra_row["value"]) if terra_row else None
        if encoded is None and part.mpn:
            encoded = from_mpn(part.mpn)
        if encoded is not None and displayed is not None and not _close(encoded, displayed):
            source = "terra value" if terra_row else f"MPN {part.mpn}"
            return Match(
                "REVIEW", "",
                f"VALUE/MPN MISMATCH: Value field {part.value!r} but {source} encodes "
                f"{_fmt(cat, encoded)} -- fix the schematic before converting",
            )

    # Tier A: exact MPN already in terra. (For R/C any value/MPN conflict was
    # already routed to REVIEW above; the note here catches ferrites/inductors.)
    if terra_row:
        note = ""
        if cat in VALUE_BEARING and value_conflict(cat, part.value, terra_row["value"]):
            note = f"CONFLICT: schematic value {part.value!r} != terra value {terra_row['value']!r}"
        return Match("A", f"{terra_row['table']}:{terra_row['uid']}", note,
                     _recommendations(part, terra_row))

    # Tier B: spec-equivalent parametric passive. Restrict to same value+package,
    # then enforce meet-or-exceed on the quality dims so a substitute is never
    # weaker than the original. The MPN is authoritative for the value when
    # decodable.
    if cat in idx.passives:
        target = encoded if encoded is not None else displayed
        pkg = package_of(part.footprint)
        cands = [c for c in idx.passives[cat] if _close(c["mag"], target) and c["package"] == pkg]
        if cands:
            best, why = _best_passive(cat, part, cands)
            if best is not None:
                return Match("B", best["mpn"], why)
            return Match("C", "", why)  # value+package exist but no SAFE substitute

    return Match("C", "", "no terra equivalent")


# --------------------------------------------------------------------------- #
# Stage 3: report
# --------------------------------------------------------------------------- #

_TIER_LABEL = {
    "A": "DROP-IN (exact MPN)",
    "B": "SUBSTITUTE (spec-equivalent)",
    "REVIEW": "REVIEW (value/MPN mismatch -- do NOT auto-convert)",
    "C": "GAP (create in terra)",
}


def build_records(parts: list[Part], idx: TerraIndex) -> list[dict]:
    """Match every part and return one flat record per instance."""
    out: list[dict] = []
    for p in parts:
        m = match_part(p, idx)
        rec = asdict(p)
        rec.update(category=category_of(p.ref, p.lib_id), tier=m.tier,
                   target=m.target, note=m.note, flags=m.flags)
        out.append(rec)
    return out


def print_report(project: str, records: list[dict]) -> None:
    """Print the tiered conversion report, gap rollup, and write-stage candidates."""
    tiers: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        tiers[r["tier"]].append(r)

    print(f"\nterra conversion report: {project}")
    print(f"  {len(records)} parts  |  "
          f"A drop-in {len(tiers['A'])}  |  B substitute {len(tiers['B'])}  |  "
          f"REVIEW {len(tiers['REVIEW'])}  |  C gap {len(tiers['C'])}\n")

    for tier in ("A", "B", "REVIEW", "C"):
        rows = tiers[tier]
        if not rows:
            continue
        print(f"--- Tier {tier}: {_TIER_LABEL[tier]} ({len(rows)}) ---")
        for r in sorted(rows, key=lambda x: x["ref"]):
            arrow = f" -> {r['target']}" if r["target"] else ""
            print(f"  {r['ref']:<6} {r['category']:<14} {r['mpn'] or '(no mpn)':<22}{arrow}")
            if r["note"]:
                print(f"         {r['note']}")
            for fl in r["flags"]:
                print(f"         + {fl}")
        print()

    gaps = Counter((r["category"], r["mpn"] or r["lib_id"]) for r in tiers["C"])
    if gaps:
        print("--- gap rollup (what terra is missing, by use) ---")
        for (cat, ident), n in gaps.most_common():
            print(f"  x{n:<3} {cat:<14} {ident}")
        print()

    # Write-stage candidates (notes #2-#4) and conflicts (#1, ferrites), rolled up.
    rec_counts = Counter(fl.split(":")[0].split(" ")[0] for r in records for fl in r["flags"])
    if rec_counts:
        print("--- write-stage candidates (read-only; drive curation) ---")
        for kind, n in rec_counts.most_common():
            print(f"  x{n:<3} {kind}")
        print()


def main() -> None:
    """Parse arguments, run the read-only match, and emit the report."""
    ap = argparse.ArgumentParser(description="Match a KiCad project's parts against terra (read-only).")
    ap.add_argument("schematic", type=Path, help="path to a .kicad_sch file")
    ap.add_argument("--db", type=Path, default=Path("db/terra.db"), help="terra database")
    ap.add_argument("--json", action="store_true", help="emit a machine record instead of the report")
    args = ap.parse_args()

    parts = parse_schematic(args.schematic)
    idx = load_terra(args.db)
    records = build_records(parts, idx)

    if args.json:
        json.dump({"project": str(args.schematic), "parts": records}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print_report(str(args.schematic), records)


if __name__ == "__main__":
    main()
