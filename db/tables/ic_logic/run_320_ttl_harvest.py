#!/usr/bin/env python3
"""Harvest the retro 7400-series TTL families from KiCad's stock 74xx symbol lib.

Parses /usr/share/kicad/symbols/74xx.kicad_sym and emits one ic_logic row per
(part, package) for the four retro families: 74 (standard TTL), 74LS, 74HC,
74HCT. Functional parametrics are derived from each symbol's Description /
keywords; electrical levels come from a per-family lookup. Per-part dynamics
(propagation delay, fmax, Icc) are NOT in the symbols and are left NULL to be
filled from datasheets later.

Key derivations:
  - family/base_number: longest-prefix match on the symbol name. base_number is
    the family-independent device number, giving cross-family equivalence.
  - package size: the MAX drawn pin number (VCC is always the top-corner pin and
    always drawn, so it equals the physical DIP size even when NC pins are omitted).
  - each part is emitted in PDIP + SOIC.

Excludes the five curated parts owned by run_310_ttl_canonical.py (which carry
hand-checked dynamics and local datasheets) and any part flagged obsolete.

Generated output (dump_priority=0) is not dumped back to static SQL.
"""
import re
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_logic_generated_320_ttl_harvest.sql")

LIB_CANDIDATES = [
    "/usr/share/kicad/symbols/74xx.kicad_sym",
    "/usr/local/share/kicad/symbols/74xx.kicad_sym",
]

# Longest prefix first so 74LS/74HCT win over 74.
FAMILIES = ("74LS", "74HCT", "74HC", "74")

# Curated by run_310 — skip here to avoid unique_id collisions.
EXCLUDE = {("74LS", "00"), ("74LS", "04"), ("74LS", "74"),
           ("74LS", "138"), ("74LS", "244")}

# Per-family recommended supply, guaranteed I/O levels, and output drive.
# HC levels are the @Vcc=4.5V values (inputs are Vcc-ratiometric); HCT inputs are
# TTL-compatible. Totem-pole for bipolar TTL, push-pull for CMOS.
FAMILY_EE = {
    "74":   dict(vmin=4.75, vmax=5.25, vih=2.0, vil=0.8,  voh=2.4, vol=0.4,
                 drive="IOL 16mA / IOH -0.4mA", default_out="totem-pole"),
    "74LS": dict(vmin=4.75, vmax=5.25, vih=2.0, vil=0.8,  voh=2.7, vol=0.5,
                 drive="IOL 8mA / IOH -0.4mA",  default_out="totem-pole"),
    "74HC": dict(vmin=2.0,  vmax=6.0,  vih=3.15, vil=1.35, voh=4.4, vol=0.1,
                 drive="IOL 4mA / IOH -4mA",    default_out="push-pull"),
    "74HCT": dict(vmin=4.5, vmax=5.5,  vih=2.0,  vil=0.8,  voh=4.4, vol=0.1,
                  drive="IOL 4mA / IOH -4mA",   default_out="push-pull"),
}

# package size (max pin) -> (PDIP footprint, SOIC footprint)
FOOTPRINTS = {
    14: ("Package_DIP:DIP-14_W7.62mm",  "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"),
    16: ("Package_DIP:DIP-16_W7.62mm",  "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"),
    20: ("Package_DIP:DIP-20_W7.62mm",  "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"),
    24: ("Package_DIP:DIP-24_W15.24mm", "Package_SO:SOIC-24W_7.5x15.4mm_P1.27mm"),
}

COUNT_WORDS = {"single": 1, "dual": 2, "double": 2, "triple": 3, "quad": 4,
               "quadruple": 4, "hex": 6, "octal": 8}

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "standards_version", "source", "dump_priority", "tier", "lifecycle_status",
    "pin_count", "temp_operating_min", "temp_operating_max",
    "logic_family", "base_number", "gate_function", "function_category",
    "channels", "inputs_per_gate", "bit_width", "logic_polarity", "output_type",
    "schmitt_trigger", "supply_voltage_min", "supply_voltage_max",
    "vih_min", "vil_max", "voh_min", "vol_max", "propagation_delay",
    "max_frequency", "output_current", "supply_current",
]


def load_blocks(text):
    blocks, cur, buf = {}, None, []
    for ln in text.split("\n"):
        m = re.match(r'\t\(symbol "([^"]+)"', ln)
        if m:
            if cur:
                blocks[cur] = "\n".join(buf)
            cur, buf = m.group(1), [ln]
        elif cur is not None:
            buf.append(ln)
    if cur:
        blocks[cur] = "\n".join(buf)
    return blocks


def prop(b, k):
    m = re.search(r'\(property "' + k + r'" "([^"]*)"', b)
    return m.group(1) if m else None


def extends(b):
    m = re.search(r'\(extends "([^"]+)"', b)
    return m.group(1) if m else None


def fam_base(name):
    for f in FAMILIES:
        rest = name[len(f):]
        if name.startswith(f) and rest[:1].isdigit():
            return f, re.match(r"\d+", rest).group(0)
    return None, None


def max_pin(blocks, name):
    b = blocks[name]
    nums = [int(x) for x in re.findall(r'\(number "(\d+)"', b)]
    if not nums and extends(b) in blocks:
        return max_pin(blocks, extends(b))
    return max(nums) if nums else 0


def categorize(desc, kw):
    # Match over description + keywords with word boundaries so gate types like a
    # trailing "AND"/"OR" classify correctly. Inverters are gates, not buffers.
    d = f"{desc} {kw}".lower()
    rules = [
        ("transceiver", r"transceiver"),
        ("shift-register", r"shift[- ]register"),
        ("register", r"register"),
        ("counter", r"counter"),
        ("decoder", r"decoder|demultiplex|demux"),
        ("encoder", r"encoder|priority"),
        ("mux", r"multiplex|selector|\bmux\b|data sel"),
        ("latch", r"latch"),
        ("flip-flop", r"flip[- ]flop"),
        ("monostable", r"monostable|multivibrator|one-shot"),
        ("arithmetic", r"arithmetic|\balu\b|adder|comparator|magnitude|parity"),
        ("buffer", r"buffer|line driver|\bdriver\b"),
        ("gate", r"\bnand\d?|\bnor\d?|\bxnor\d?|\bxor\d?|\band\d?\b|\bor\d?\b|inverter|\bgate\b|schmitt"),
    ]
    for cat, pat in rules:
        if re.search(pat, d):
            return cat
    return "other"


def derive(desc, kw, cat):
    text = f"{desc} {kw}".lower()
    channels = next((v for w, v in COUNT_WORDS.items()
                     if re.search(rf"\b{w}\b", text)), None)
    m = re.search(r"(\d+)\s*-?\s*input", text)
    inputs = int(m.group(1)) if m else None
    m = re.search(r"(\d+)\s*-?\s*bit", text)
    bit_width = int(m.group(1)) if m else None
    if channels is None:
        if cat == "gate" and inputs is not None:
            channels = 1                       # e.g. single 8-input NAND
        elif cat in ("buffer", "transceiver") and bit_width:
            channels = bit_width
    if "3-state" in text or "3 state" in text or "tri-state" in text or "tristate" in text:
        out = "3-state"
    elif "open collector" in text or "open-collector" in text:
        out = "open-collector"
    elif "open drain" in text or "open-drain" in text:
        out = "open-drain"
    else:
        out = None
    if "non-invert" in text or "noninvert" in text:
        pol = "non-inverting"
    elif any(k in text for k in ["nand", "nor", "inverter", "inverting",
                                 "active low", "active-low"]):
        pol = "inverting"
    elif any(k in text for k in [" and ", " or ", "buffer", "driver"]):
        pol = "non-inverting"
    else:
        pol = None
    schmitt = "yes" if "schmitt" in text else "no"
    return channels, inputs, bit_width, out, pol, schmitt


def clean_function(desc):
    # drop trailing package notes some descriptions carry ("..., DIP-14")
    return re.sub(r",?\s*(DIP|SO|SOIC|TSSOP)-?\d+\s*$", "", desc, flags=re.I).strip()


def gpn_from_ds(ds):
    m = re.search(r"/gpn/(\w+)", ds or "")
    return m.group(1).upper() if m else None


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lib = next((p for p in LIB_CANDIDATES if Path(p).exists()), None)
    if not lib:
        raise SystemExit("74xx.kicad_sym not found; install KiCad symbol libs")
    blocks = load_blocks(Path(lib).read_text())

    # One row-set per (family, base): prefer the exact "<fam><base>" symbol over
    # KiCad's _Split (schematic-convenience), revision (A), or package-leak (N)
    # variants, which are the same physical device.
    groups = {}
    for name in blocks:
        fam, base = fam_base(name)
        if fam:
            groups.setdefault((fam, base), []).append(name)
    chosen = {f"{fam}{base}" if f"{fam}{base}" in cands else min(cands, key=len)
              for (fam, base), cands in groups.items()}

    rows, skipped = [], {"obsolete": 0, "curated": 0, "variant": 0}
    for name in sorted(blocks):
        fam, base = fam_base(name)
        if not fam:
            continue
        if name not in chosen:
            skipped["variant"] += 1
            continue
        if (fam, base) in EXCLUDE:
            skipped["curated"] += 1
            continue
        b = blocks[name]
        desc_raw = prop(b, "Description") or prop(blocks.get(extends(b), ""), "Description") or ""
        if "obsolete" in desc_raw.lower():
            skipped["obsolete"] += 1
            continue
        kw = prop(b, "ki_keywords") or ""
        ds = prop(b, "Datasheet") or prop(blocks.get(extends(b), ""), "Datasheet")
        pins = max_pin(blocks, name)
        if pins not in FOOTPRINTS:
            continue
        ee = FAMILY_EE[fam]
        cat = categorize(desc_raw, kw)
        ch, inp, bw, out, pol, schmitt = derive(desc_raw, kw, cat)
        value = f"{fam}{base}"
        func = clean_function(desc_raw)
        gpn = gpn_from_ds(ds)
        common = dict(
            manufacturer="Texas Instruments",
            datasheet=ds, kicad_symbol=f"74xx:{name}",
            manufacturer_link=f"https://www.ti.com/product/{gpn}" if gpn else None,
            rohs="Yes", allow_substitution="Yes", tracking="No",
            standards_version="1.0", source="ti_74xx", dump_priority=0, tier=2,
            lifecycle_status="Active", temp_operating_min=0, temp_operating_max=70,
            logic_family=fam, base_number=base, gate_function=func,
            function_category=cat, channels=ch, inputs_per_gate=inp, bit_width=bw,
            logic_polarity=pol, output_type=out or ee["default_out"],
            schmitt_trigger=schmitt,
            supply_voltage_min=ee["vmin"], supply_voltage_max=ee["vmax"],
            vih_min=ee["vih"], vil_max=ee["vil"], voh_min=ee["voh"], vol_max=ee["vol"],
            propagation_delay=None, max_frequency=None,
            output_current=ee["drive"], supply_current=None,
        )
        for pkg, suffix, fp in (("PDIP", "N", FOOTPRINTS[pins][0]),
                                ("SOIC", "D", FOOTPRINTS[pins][1])):
            pkg_label = f"{pkg}-{pins}"
            mpn = f"SN{fam}{base}{suffix}"
            rows.append({**common,
                         "unique_id": f"TI-{mpn}",
                         "part_locator": f"IC_LOGIC {value} {pkg_label}",
                         "mpn": mpn, "package": pkg_label, "pin_count": str(pins),
                         "value": value,
                         "description": f"{func}, {fam}, {pkg_label}",
                         "kicad_footprint": fp})

    lines = [
        "-- Terra EDA Library - 74xx TTL harvest (74/74LS/74HC/74HCT)",
        f"-- Generated by {Path(__file__).name}. dump_priority=0: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in rows:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_logic ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} rows "
          f"({len(rows)//2} parts), skipped {skipped}")


if __name__ == "__main__":
    main()
