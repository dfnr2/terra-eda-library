"""Shared row builder, pinout check and writer for the optocoupler generators.

Each generator lists its parts as `Part` records transcribed from the maker's data
sheet; `write()` checks them and emits the SQL.

Pinout is checked in two steps, because most stock opto symbols leave their pins
unnamed and draw the function only in the graphics:

1. `SYMBOL_PINS` records the function behind every pin of each *root* symbol used
   (the symbol at the end of the `extends` chain), transcribed from its drawing in
   the KiCad 10 library. `check_symbol()` re-reads the library and holds that
   transcription to everything the file states directly: the pin-number set, which
   pins are no-connect, the pin names where the symbol has them, and which side of
   the body each pin sits on (LED pins left, output pins right/top/bottom).
2. Every `Part` carries the pin table from its own data sheet (`pinout`), which must
   equal the recorded functions of its symbol pin for pin.

A mismatch at either step stops the build, so a row never ships on a symbol whose
pins disagree with its data sheet.
"""
import re
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
KICAD_SYMBOLS = Path("/usr/share/kicad/symbols")
KICAD_FOOTPRINTS = Path("/usr/share/kicad/footprints")
CUSTOM_LIB = "terra_symbols_optocouplers"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "lifecycle_status", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "output_type", "channels", "isolation_voltage", "ctr", "led_forward_voltage",
    "led_operate_current", "output_voltage_max", "output_current_max",
    "turn_on_time", "turn_off_time",
]

OUTPUT_TYPES = {
    "phototransistor": "phototransistor output",
    "darlington": "photodarlington output",
    "logic": "logic-gate output",
    "transistor-high-speed": "high-speed transistor output",
    "schmitt": "Schmitt-trigger output",
    "triac-driver": "random-phase triac driver",
    "triac-driver-zc": "zero-cross triac driver",
}

# Pin functions: A/K LED anode/cathode, AK either LED terminal (AC input), C/E/B
# transistor collector/emitter/base, VB high-speed transistor base, VO/VO1/VO2
# output, EN enable, VCC/GND supply, MT triac main terminal, NC no connection.
# Suffix 1/2/3/4 numbers the channel on multi-channel parts.
INPUT_FUNCS = re.compile(r"^(A|K|AK)\d?$")

# Root symbol -> {pin: function}, read off each symbol's drawing.
SYMBOL_PINS = {
    # 4N25..4N37, TIL111, SFH601: LED 1-2 (bar at bottom, so 1 = anode), NC 3,
    # emitter (arrowed lead) 4, collector 5, base 6.
    "Isolator:4N25": {"1": "A", "2": "K", "3": "NC", "4": "E", "5": "C", "6": "B"},
    "Isolator:CNY17-1": {"1": "A", "2": "K", "3": "NC", "4": "E", "5": "C", "6": "B"},
    # Two anti-parallel LEDs on 1-2.
    "Isolator:H11AA1": {"1": "AK", "2": "AK", "3": "NC", "4": "E", "5": "C", "6": "B"},
    "Isolator:PC817": {"1": "A", "2": "K", "3": "E", "4": "C"},
    # Photodiode from VCC (8) to the base node (7); transistor collector 6, emitter 5.
    "Isolator:6N135": {"1": "NC", "2": "A", "3": "K", "4": "NC",
                       "5": "GND", "6": "VO", "7": "VB", "8": "VCC"},
    # Split Darlington: VCC 8 to first collector, 7 = first emitter / second base,
    # 6 = second collector, 5 = second emitter. The symbol *names* these pins
    # C1/C2/VO1/VO2 (see NAME_QUIRKS); the drawing is right.
    "Isolator:6N138": {"1": "NC", "2": "A", "3": "K", "4": "NC",
                       "5": "GND", "6": "VO", "7": "VB", "8": "VCC"},
    "Isolator:HCPL-261A": {"1": "NC", "2": "A", "3": "K", "4": "NC",
                           "5": "GND", "6": "VO", "7": "EN", "8": "VCC"},
    "Isolator:HCPL-2601": {"1": "NC", "2": "A", "3": "K", "4": "NC",
                           "5": "GND", "6": "VO", "7": "EN", "8": "VCC"},
    "Isolator:HCPL-263A": {"1": "A1", "2": "K1", "3": "K2", "4": "A2",
                           "5": "GND", "6": "VO2", "7": "VO1", "8": "VCC"},
    # Schmitt detector: VCC on the top pin (6), GND bottom (5), output right (4).
    "Isolator:H11L1": {"1": "A", "2": "K", "3": "NC", "4": "VO", "5": "GND", "6": "VCC"},
    # Triac drivers: 5 is the triac substrate, drawn as a hidden no-connect.
    "Relay_SolidState:MOC3010M": {"1": "A", "2": "K", "3": "NC", "4": "MT",
                                  "5": "NC", "6": "MT"},
    "Relay_SolidState:MOC3031M": {"1": "A", "2": "K", "3": "NC", "4": "MT",
                                  "5": "NC", "6": "MT"},
    # terra photodarlington (drawn from Isolator:4N25): base pin 6 enters from below.
    f"{CUSTOM_LIB}:4N32": {"1": "A", "2": "K", "3": "NC", "4": "E", "5": "C", "6": "B"},
}

# Symbol pin names that read as a different function than the drawing shows. Listed
# exactly, so a library change that renames them is noticed.
NAME_QUIRKS = {
    "Isolator:6N138": {"2": "C1", "3": "C2", "6": "VO2", "7": "VO1"},
}

# Pin names that state a function outright. "C" is only trusted on the LED side,
# where it means cathode (on the output side it would mean collector).
NAMED = {"A": "A", "K": "K", "A1": "A1", "A2": "A2", "GND": "GND", "VCC": "VCC",
         "VO": "VO", "VO1": "VO1", "VO2": "VO2", "EN": "EN", "VB": "VB", "NC": "NC"}
NAMED_LEFT = {"C": "K", "C1": "K1", "C2": "K2"}

FOOTPRINTS = {n: f"Package_DIP:DIP-{n}_W7.62mm" for n in (4, 6, 8, 16)}


@dataclass
class Part:
    manufacturer: str   # maker name, also the unique_id prefix
    mpn: str            # orderable code: plain DIP, tube/bulk
    value: str          # schematic label (bare type number)
    output_type: str    # OUTPUT_TYPES key
    channels: int
    pins: int           # DIP pin count
    symbol: str         # "Lib:Name"
    pinout: str         # data sheet pin table, "1A 2K 3NC 4E 5C 6B"
    isolation: str      # "5000Vrms"
    vf: str             # "1.2V typ, 1.5V max @ IF=10mA"
    vo_max: str         # VCEO / VDRM / max output voltage
    datasheet: str      # path under datasheets/
    ctr: str | None = None
    if_on: str | None = None     # led_operate_current
    io_max: str | None = None
    t_on: str | None = None
    t_off: str | None = None
    link: str | None = None
    lifecycle: str = "Active"
    note: str = ""      # extra description text
    keywords: str = ""  # extra comma-separated keywords


def _parse_lib(path):
    """name -> (extends, [(etype, name, number, x, y)]) for one .kicad_sym file."""
    text = path.read_text()
    syms = {}
    for block in re.split(r'\n\t\(symbol "', text)[1:]:
        name = block.split('"', 1)[0]
        ext = re.search(r'\(extends "([^"]+)"\)', block)
        pins = [(t, nm, num, float(x), float(y)) for t, x, y, nm, num in re.findall(
            r'\(pin (\w+) \w+\s*\(at ([-\d.]+) ([-\d.]+) \d+\).*?\(name "([^"]*)"'
            r'.*?\(number "([^"]*)"', block, re.S)]
        syms[name] = (ext.group(1) if ext else None, pins)
    return syms


_LIBS = {}


def _lib(libname):
    if libname not in _LIBS:
        path = (REPO / "kicad_symbols" / f"{libname}.kicad_sym" if libname == CUSTOM_LIB
                else KICAD_SYMBOLS / f"{libname}.kicad_sym")
        _LIBS[libname] = _parse_lib(path) if path.is_file() else None
    return _LIBS[libname]


def resolve(symbol):
    """'Lib:Name' -> ('Lib:Root', pins) following `extends`; None if the lib is absent."""
    libname, name = symbol.split(":", 1)
    syms = _lib(libname)
    if syms is None:
        return None
    if name not in syms:
        raise SystemExit(f"no symbol {symbol}")
    ext, pins = syms[name]
    while not pins and ext:
        name = ext
        ext, pins = syms[name]
    return f"{libname}:{name}", pins


def check_symbol(root, pins):
    """Hold the SYMBOL_PINS transcription for `root` to what the library file says."""
    if root not in SYMBOL_PINS:
        raise SystemExit(f"{root}: no pin-function transcription in SYMBOL_PINS")
    funcs = SYMBOL_PINS[root]
    nums = sorted({p[2] for p in pins}, key=int)
    if nums != sorted(funcs, key=int):
        raise SystemExit(f"{root}: symbol pins {nums} != transcribed {sorted(funcs, key=int)}")
    quirks = NAME_QUIRKS.get(root, {})
    for etype, name, num, x, y in pins:
        f = funcs[num]
        is_nc = etype == "no_connect" or name == "NC"
        if is_nc != (f == "NC"):
            raise SystemExit(f"{root} pin {num}: no-connect is {is_nc} but transcribed {f}")
        named = NAMED.get(name) or (NAMED_LEFT.get(name) if x < 0 else None)
        if num in quirks:
            if name != quirks[num]:
                raise SystemExit(f"{root} pin {num}: expected quirk name {quirks[num]!r}, "
                                 f"symbol now says {name!r}; review NAME_QUIRKS")
        elif named and named != f:
            raise SystemExit(f"{root} pin {num}: symbol names it {name!r}, transcribed {f}")
        if f == "NC":
            continue
        if INPUT_FUNCS.match(f):
            ok = x < 0
        elif f == "VCC":
            ok = y > 0 or x > 0
        elif f == "GND":
            ok = y < 0 or x > 0
        elif f == "B":
            ok = x > 0 or y < 0
        else:
            ok = x > 0
        if not ok:
            raise SystemExit(f"{root} pin {num} ({f}) sits at ({x}, {y}), wrong side")


def _pinout(text):
    out = {}
    for tok in text.split():
        m = re.fullmatch(r"(\d+)([A-Z][A-Z0-9]*)", tok)
        if not m:
            raise SystemExit(f"bad pinout token {tok!r}")
        out[m.group(1)] = m.group(2)
    return out


def rows(parts):
    for p in parts:
        if p.output_type not in OUTPUT_TYPES:
            raise SystemExit(f"{p.mpn}: unknown output_type {p.output_type}")
        pinout = _pinout(p.pinout)
        if sorted(pinout, key=int) != [str(i) for i in range(1, p.pins + 1)]:
            raise SystemExit(f"{p.mpn}: pinout {p.pinout} does not cover DIP-{p.pins}")
        anodes = sum(1 for f in pinout.values() if re.fullmatch(r"A\d?", f))
        if anodes and anodes != p.channels:
            raise SystemExit(f"{p.mpn}: {anodes} LED anodes but {p.channels} channels")
        res = resolve(p.symbol)
        if res is None:
            print(f"  warning: library for {p.symbol} not found; pinout check skipped")
        else:
            root, pins = res
            check_symbol(root, pins)
            if SYMBOL_PINS[root] != pinout:
                raise SystemExit(f"{p.mpn}: data sheet pinout {p.pinout} but {p.symbol} "
                                 f"(root {root}) is {SYMBOL_PINS[root]}")
        footprint = FOOTPRINTS[p.pins]
        lib, fp = footprint.split(":")
        if KICAD_FOOTPRINTS.is_dir() and not (
                KICAD_FOOTPRINTS / f"{lib}.pretty" / f"{fp}.kicad_mod").is_file():
            raise SystemExit(f"{p.mpn}: missing footprint {footprint}")
        if not (REPO / "datasheets" / p.datasheet).is_file():
            raise SystemExit(f"{p.mpn}: missing datasheet datasheets/{p.datasheet}")

        pkg = f"DIP-{p.pins}"
        kind = OUTPUT_TYPES[p.output_type]
        ch = {1: "single", 2: "dual", 4: "quad"}[p.channels]
        desc = f"{p.manufacturer} {p.value} {ch}-channel optocoupler, {kind}, Viso {p.isolation}"
        if p.ctr:
            desc += f", CTR {p.ctr}"
        if p.if_on and p.output_type != "darlington":
            desc += f", IF(on) {p.if_on}"
        if p.output_type.startswith("triac"):
            label = "VDRM"
        elif p.output_type in ("phototransistor", "darlington") and p.pins <= 6:
            label = "VCEO"  # bare transistor output; the 8-pin parts have VCC/VO
        else:
            label = "VO"
        desc += f", {label} {p.vo_max.split(' (')[0]} max, {pkg}"
        if p.note:
            desc += f"; {p.note}"
        kw = ["optocoupler", "optoisolator", "isolator", "through-hole", pkg.lower()]
        kw += {"phototransistor": ["phototransistor"],
               "darlington": ["photodarlington", "darlington"],
               "logic": ["high-speed", "logic-output", "digital"],
               "transistor-high-speed": ["high-speed", "phototransistor"],
               "schmitt": ["schmitt-trigger", "digital"],
               "triac-driver": ["triac-driver", "phototriac", "random-phase"],
               "triac-driver-zc": ["triac-driver", "phototriac", "zero-cross"]}[p.output_type]
        kw += [k for k in p.keywords.split(",") if k]
        kw.append(p.value)
        iso = p.isolation.lower()
        if " " in p.manufacturer + p.mpn:
            raise SystemExit(f"{p.mpn}: spaces in manufacturer/MPN break unique_id")
        yield {
            "unique_id": f"{p.manufacturer}-{p.mpn}",
            "part_locator": f"opto-{p.output_type}-{p.channels}ch-{iso}-dip{p.pins}",
            "mpn": p.mpn, "manufacturer": p.manufacturer, "package": pkg,
            "value": p.value, "description": desc,
            "datasheet": "${TERRA_EDA_LIB}/datasheets/" + p.datasheet,
            "manufacturer_link": p.link, "kicad_symbol": p.symbol,
            "kicad_footprint": footprint, "lifecycle_status": p.lifecycle,
            "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
            "source": None, "dump_priority": 0, "tier": 2,
            "keywords": ",".join(kw), "pin_count": str(p.pins),
            "output_type": p.output_type, "channels": p.channels,
            "isolation_voltage": p.isolation, "ctr": p.ctr,
            "led_forward_voltage": p.vf, "led_operate_current": p.if_on,
            "output_voltage_max": p.vo_max, "output_current_max": p.io_max,
            "turn_on_time": p.t_on, "turn_off_time": p.t_off,
        }


def _sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def write(output_file, title, created_by, parts):
    recs = list(rows(parts))
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
        lines.append(f"INSERT INTO optocouplers ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    output_file.write_text("\n".join(lines))
    print(f"Generated {output_file.name}: {len(recs)} parts")
    for r in recs:
        if r["lifecycle_status"] != "Active":
            print(f"  {r['lifecycle_status']}: {r['mpn']}")
