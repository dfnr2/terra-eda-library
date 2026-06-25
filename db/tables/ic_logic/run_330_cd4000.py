#!/usr/bin/env python3
"""Harvest the CD4000-series CMOS logic from KiCad's stock 4xxx symbol lib.

Same approach as run_320 (the 74xx TTL harvest) but for the 4000-series, which is
a single logic family (logic_family='4000B') rather than a set of speed grades.
Parses /usr/share/kicad/symbols/4xxx.kicad_sym, emits one ic_logic row per
(part, package) in PDIP + SOIC. Functional parametrics are derived from each
symbol's Description; electrical levels are the 4000B @Vcc=5V representative
values (real 4000B levels are Vcc-ratiometric over a 3-18V supply).

Differences from the 74xx harvest:
  - base_number is the device number itself (no family prefix); vendor prefixes
    (CD/HEF/MC) are stripped and 5-digit MC14xxx parts fold to 4xxx (14528->4528).
  - pin count comes from ki_fp_filters first (4049/4050 have a non-corner Vdd and
    an NC top pin, so max-pin undercounts), then max-pin, then a 15->16 round.
  - manufacturer/MPN/datasheet are normalized to the TI CD4000B line for a
    coherent orderable part, as the 74xx harvest did with TI.

Per-part dynamics (propagation delay, fmax, Icc) aren't in the symbols -> NULL.
Generated output (dump_priority=0) is not dumped back to static SQL.
"""
import re
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_logic_generated_330_cd4000.sql")

LIB_CANDIDATES = [
    "/usr/share/kicad/symbols/4xxx.kicad_sym",
    "/usr/local/share/kicad/symbols/4xxx.kicad_sym",
]

# 4000B @Vcc=5V representative levels; supply spans 3-18V, inputs Vcc-ratiometric.
FAMILY_EE = dict(vmin=3.0, vmax=18.0, vih=3.5, vil=1.5, voh=4.95, vol=0.05,
                 drive="IOL ~0.5mA / IOH ~-0.5mA @5V", default_out="push-pull")

FOOTPRINTS = {
    14: ("Package_DIP:DIP-14_W7.62mm",  "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm"),
    16: ("Package_DIP:DIP-16_W7.62mm",  "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"),
    20: ("Package_DIP:DIP-20_W7.62mm",  "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm"),
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


def base_of(name):
    d = re.search(r"\d+", name).group(0)
    return d[1:] if len(d) == 5 and d[0] == "1" else d   # MC14528 -> 4528


def max_pin(blocks, name):
    b = blocks[name]
    nums = [int(x) for x in re.findall(r'\(number "(\d+)"', b)]
    if not nums and extends(b) in blocks:
        return max_pin(blocks, extends(b))
    return max(nums) if nums else 0


def fp_pins(fpf):
    if not fpf:
        return 0
    m = re.search(r"DIP[*?-]?(\d{1,2})", fpf)
    if m:
        return int(m.group(1))
    for body, n in (("3.9x8.7", 14), ("3.9x9.9", 16), ("7.5x12.8", 20)):
        if body in fpf:
            return n
    return 0


def categorize(desc, kw):
    d = f"{desc} {kw}".lower()
    rules = [
        ("analog-switch", r"analog switch|bilateral|transmission gate"),
        ("transceiver", r"transceiver"),
        ("shift-register", r"shift[- ]register"),
        ("register", r"register"),
        ("counter", r"counter"),
        ("decoder", r"decoder|demultiplex|demux|7.?segment"),
        ("encoder", r"encoder|priority"),
        ("mux", r"multiplex|selector|\bmux\b|data sel"),
        ("latch", r"latch"),
        ("flip-flop", r"flip[- ]?flop"),
        ("monostable", r"monostable|multivibrator|one-shot|astable"),
        ("arithmetic", r"arithmetic|\balu\b|adder|comparator|magnitude|parity"),
        ("buffer", r"buffer|line driver|\bdriver\b|level.?shift"),
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
            channels = 1
        elif cat in ("buffer", "transceiver") and bit_width:
            channels = bit_width
    if any(s in text for s in ("3-state", "3 state", "tri-state", "tristate")):
        out = "3-state"
    elif "open drain" in text or "open-drain" in text:
        out = "open-drain"
    elif cat == "analog-switch":
        out = "bilateral"
    else:
        out = None
    if cat == "analog-switch":
        pol = None
    elif "non-invert" in text or "noninvert" in text:
        pol = "non-inverting"
    elif any(k in text for k in ["nand", "nor", "inverter", "inverting"]):
        pol = "inverting"
    elif any(k in text for k in [" and ", " or ", "buffer", "driver"]):
        pol = "non-inverting"
    else:
        pol = None
    schmitt = "yes" if "schmitt" in text else "no"
    return channels, inputs, bit_width, out, pol, schmitt


def clean_function(desc):
    # strip a trailing run of package notes ("..., DIP-16/SOIC-16/TSSOP-16")
    return re.sub(r"[,;]?\s*((PDIP|DIP|SOIC|SOP|SO|TSSOP|SSOP)[-\s]?\d+\s*[/,]?\s*)+$",
                  "", desc, flags=re.I).strip()


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    lib = next((p for p in LIB_CANDIDATES if Path(p).exists()), None)
    if not lib:
        raise SystemExit("4xxx.kicad_sym not found; install KiCad symbol libs")
    blocks = load_blocks(Path(lib).read_text())

    # One row-set per base (fold CD4033B/HEF4093B/MC14528 onto their device number).
    chosen = {}
    for name in blocks:
        chosen.setdefault(base_of(name), name)
        # prefer the bare-number symbol if both bare and prefixed exist
        if name == base_of(name):
            chosen[base_of(name)] = name

    rows = []
    for base, name in sorted(chosen.items()):
        b = blocks[name]
        desc_raw = prop(b, "Description") or ""
        if "obsolete" in desc_raw.lower():
            continue
        kw = prop(b, "ki_keywords") or ""
        ds = prop(b, "Datasheet") or prop(blocks.get(extends(b), ""), "Datasheet")
        pins = fp_pins(prop(b, "ki_fp_filters")) or max_pin(blocks, name)
        if pins == 15:
            pins = 16
        if pins not in FOOTPRINTS:
            continue
        ee = FAMILY_EE
        cat = categorize(desc_raw, kw)
        ch, inp, bw, out, pol, schmitt = derive(desc_raw, kw, cat)
        func = clean_function(desc_raw)
        value = f"CD{base}B"
        common = dict(
            manufacturer="Texas Instruments",
            datasheet=f"https://www.ti.com/lit/ds/symlink/cd{base.lower()}b.pdf",
            manufacturer_link=f"https://www.ti.com/product/CD{base}B",
            kicad_symbol=f"4xxx:{name}",
            rohs="Yes", allow_substitution="Yes", tracking="No",
            standards_version="1.0", source="cd4000", dump_priority=0, tier=2,
            lifecycle_status="Active", temp_operating_min=-55, temp_operating_max=125,
            logic_family="4000B", base_number=base, gate_function=func,
            function_category=cat, channels=ch, inputs_per_gate=inp, bit_width=bw,
            logic_polarity=pol, output_type=out or ee["default_out"],
            schmitt_trigger=schmitt,
            supply_voltage_min=ee["vmin"], supply_voltage_max=ee["vmax"],
            vih_min=ee["vih"], vil_max=ee["vil"], voh_min=ee["voh"], vol_max=ee["vol"],
            propagation_delay=None, max_frequency=None,
            output_current=ee["drive"], supply_current=None,
        )
        for pkg, suffix, fp in (("PDIP", "E", FOOTPRINTS[pins][0]),
                                ("SOIC", "M", FOOTPRINTS[pins][1])):
            pkg_label = f"{pkg}-{pins}"
            mpn = f"CD{base}B{suffix}"
            rows.append({**common,
                         "unique_id": f"TI-{mpn}",
                         "part_locator": f"IC_LOGIC {value} {pkg_label}",
                         "mpn": mpn, "package": pkg_label, "pin_count": str(pins),
                         "value": value,
                         "description": f"{func}, 4000B, {pkg_label}",
                         "kicad_footprint": fp})

    lines = [
        "-- Terra EDA Library - CD4000-series CMOS logic harvest",
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
    print(f"Generated {OUTPUT_FILE.name}: {len(rows)} rows ({len(rows)//2} parts)")


if __name__ == "__main__":
    main()
