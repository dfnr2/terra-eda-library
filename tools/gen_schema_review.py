#!/usr/bin/env python3
"""Generate the Phase 0 schema-review org file: a proposed canonical parametric tail
per part type, diffed against what each table currently has, with keep/add/drop marks.

The proposals come from CLAUDE.md's component-type specs + the existing CERN tails +
the bjt/connectors quality bar. The reviewer edits the Decision column; apply happens
later via gen_schema.py once approved.

Output: schema-review.org
"""
from __future__ import annotations
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db/terra.db"
ORG = ROOT / "schema-review.org"

# type -> (native tables, cern tables)
TYPES = {
    "diodes": (["diodes"], ["cern_diodes"]),
    "transistors": (["bjt", "mosfet"], ["cern_transistors"]),
    "op_amps": (["ic_opamp"], ["cern_op_amps"]),
    "logic": (["ic_logic"], ["cern_logic", "cern_standard_logic"]),
    "analog": (["ic_analog"], ["cern_analog_interface"]),
    "leds": (["leds"], ["cern_leds_displays"]),
    "switches": (["switches"], ["cern_switches"]),
    "inductors": (["inductors"], []),
    "ferrites": (["ferrites"], []),
    "ic_drivers": (["ic_drivers"], []),
    "ic_memory": (["ic_memory"], []),
    "ic_microcontrollers": (["ic_microcontrollers"], []),
    "connectors": (["connectors"], ["cern_molex", "cern_samtec"]),  # full vendor set shares this
}

# Proposed canonical tail per type: (column, sqltype, rationale)
PROPOSALS = {
    "diodes": [
        ("diode_type", "TEXT", "Type: rectifier/schottky/zener/tvs/small-signal (CLAUDE.md, CERN)"),
        ("voltage_rating", "TEXT", "Vr reverse standoff/working (CLAUDE.md, CERN)"),
        ("forward_voltage", "TEXT", "Vf (CLAUDE.md)"),
        ("forward_current", "TEXT", "If (CLAUDE.md)"),
        ("current_rating", "TEXT", "Io rectifier average (CLAUDE.md)"),
        ("power_rating", "TEXT", "Pd for TVS/zener (CERN)"),
    ],
    "transistors": [
        ("transistor_type", "TEXT", "npn/pnp/nmos/pmos/igbt/jfet (CLAUDE.md, CERN)"),
        ("channels", "INTEGER", "dual/single packages"),
        ("v_ce_ds_max", "TEXT", "Vce(BJT)/Vds(FET) (CLAUDE.md)"),
        ("i_c_d_max", "TEXT", "Ic/Id (CLAUDE.md)"),
        ("power_dissipation", "TEXT", "Pd (bjt schema)"),
        ("hfe_typ", "TEXT", "BJT gain; null for FET (bjt schema)"),
        ("rds_on", "TEXT", "FET on-resistance; null for BJT"),
        ("vgs_th", "TEXT", "FET threshold; null for BJT"),
        ("transition_freq", "TEXT", "ft (bjt schema)"),
        ("temp_junction_max", "TEXT", "Tj max (bjt schema)"),
    ],
    "op_amps": [
        ("amplifier_type", "TEXT", "voltage-fb/current-fb/instrumentation (CERN)"),
        ("channels", "INTEGER", "channel count (CLAUDE.md, CERN)"),
        ("gain_bandwidth", "TEXT", "GBW (CLAUDE.md)"),
        ("slew_rate", "TEXT", "slew rate (CLAUDE.md)"),
        ("input_offset", "TEXT", "input offset (CLAUDE.md)"),
        ("input_noise", "TEXT", "noise (CLAUDE.md)"),
        ("supply_voltage", "TEXT", "supply range"),
    ],
    "logic": [
        ("logic_family", "TEXT", "74HC/74LVC/4000 (CLAUDE.md)"),
        ("gate_function", "TEXT", "and/or/nand/mux/ff/buffer (CLAUDE.md)"),
        ("channels", "INTEGER", "gates/bits per package"),
        ("propagation_delay", "TEXT", "tpd (CLAUDE.md)"),
        ("supply_voltage", "TEXT", "voltage (CLAUDE.md)"),
    ],
    "analog": [
        ("function_type", "TEXT", "adc/dac/comparator/mux/vref/interface (CLAUDE.md)"),
        ("channels", "INTEGER", "channel count"),
        ("resolution_bits", "TEXT", "ADC/DAC resolution"),
        ("interface", "TEXT", "spi/i2c/parallel"),
        ("supply_voltage", "TEXT", "supply range"),
    ],
    "leds": [
        ("color", "TEXT", "color (CLAUDE.md, CERN)"),
        ("wavelength_nm", "TEXT", "wavelength (CLAUDE.md, CERN)"),
        ("forward_voltage_v", "TEXT", "Vf (CLAUDE.md, CERN)"),
        ("current_max_ma", "TEXT", "If max (CERN)"),
        ("luminous_intensity", "TEXT", "intensity (CLAUDE.md, CERN)"),
        ("viewing_angle", "TEXT", "viewing angle (CLAUDE.md)"),
    ],
    "switches": [
        ("switch_type", "TEXT", "tactile/toggle/dip/rotary/slide (CLAUDE.md, CERN)"),
        ("poles", "INTEGER", "poles (CLAUDE.md)"),
        ("throws", "INTEGER", "throws (CLAUDE.md)"),
        ("current_rating", "TEXT", "contact current"),
        ("voltage_rating", "TEXT", "contact voltage"),
        ("actuation_force", "TEXT", "actuation force (CLAUDE.md)"),
    ],
    "inductors": [
        ("inductance", "TEXT", "inductance (CLAUDE.md)"),
        ("tolerance", "TEXT", "tolerance (CLAUDE.md)"),
        ("current_rating", "TEXT", "rated current (CLAUDE.md)"),
        ("saturation_current", "TEXT", "Isat (CLAUDE.md)"),
        ("dcr", "TEXT", "DC resistance"),
        ("srf", "TEXT", "self-resonant freq"),
    ],
    "ferrites": [
        ("impedance_at_freq", "TEXT", "impedance @ freq (CLAUDE.md)"),
        ("dc_resistance", "TEXT", "DCR (CLAUDE.md)"),
        ("current_rating", "TEXT", "rated current (CLAUDE.md)"),
    ],
    "ic_drivers": [
        ("driver_type", "TEXT", "gate/motor/led/line driver"),
        ("output_current", "TEXT", "output current (CLAUDE.md)"),
        ("channels", "INTEGER", "channels (CLAUDE.md)"),
        ("logic_level", "TEXT", "logic level (CLAUDE.md)"),
    ],
    "ic_memory": [
        ("memory_type", "TEXT", "sram/dram/flash/eeprom (CLAUDE.md)"),
        ("capacity", "TEXT", "capacity (CLAUDE.md)"),
        ("speed", "TEXT", "speed (CLAUDE.md)"),
        ("interface", "TEXT", "spi/i2c/parallel (CLAUDE.md)"),
    ],
    "ic_microcontrollers": [
        ("family", "TEXT", "family (CLAUDE.md)"),
        ("flash_size", "TEXT", "flash (CLAUDE.md)"),
        ("ram_size", "TEXT", "RAM (CLAUDE.md)"),
        ("gpio_count", "INTEGER", "GPIO count (CLAUDE.md)"),
        ("core", "TEXT", "CPU core"),
    ],
    "connectors": None,   # adopt the existing native 38-col schema verbatim (special-cased)
}

# Legacy flat-`symbols` columns dropped from ALL native non-passive tables (universal
# cruft; shown once globally instead of repeated per type).
LEGACY_CRUFT = {"class", "component_type", "component_value", "composition",
                "number_of_pins", "reference", "sim_library", "sim_type",
                "temp_coeff", "temp_operating", "temp_soldering", "temp_storage"}

CERN_ONLY = ["cern_regulators", "cern_optocouplers", "cern_dc_dc_converters",
             "cern_crystals_oscillators", "cern_relays", "cern_fuses", "cern_sensors",
             "cern_transformers", "cern_power_supplies", "cern_thermistors_varistors",
             "cern_batteries"]


def cols(con, t):
    try:
        return [r[1] for r in con.execute(f'PRAGMA table_info("{t}")')]
    except sqlite3.OperationalError:
        return []


def main():
    con = sqlite3.connect(DB)
    cern_tabs = [n for (n,) in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cern_%' "
        "AND name NOT LIKE '%\\_v' ESCAPE '\\'")]
    core = None
    for t in cern_tabs:
        c = set(cols(con, t))
        core = c if core is None else (core & c)
    core -= {"tags"}

    def tail(t):
        return [c for c in cols(con, t) if c not in core and c != "tags"]

    out = ["#+TITLE: Phase 0 — Part-Type Schema Review",
           "",
           "* RESUME BRIEFING (read first — full context to continue cold)",
           "  :STATUS: Awaiting Dave's review of THIS file. He is editing the Decision cells below.",
           "  When he says \"done\", parse his marks and execute Phase 0 (plan:",
           "  2026-06-10-phase0-schema-consolidation.md): build db/schema/core.sql (the 34",
           "  shared core cols) + db/schema/types/<type>.sql fragments from the APPROVED columns",
           "  here, write tools/gen_schema.py (generates each table's _0_schema.sql = core +",
           "  fragment), add the equivalence + drift tests, regenerate so cern_<type> and the",
           "  native <type> share one tail. This file's marks ARE the Task 5-12 column lists.",
           "",
           "  HOW DAVE MARKS THIS FILE:",
           "  - Universal drop section: DROP-ALL yes/no (drop the 12 legacy symbols cols everywhere).",
           "  - Each type table: edit Decision = keep|add|drop; resolve every 'drop?' row",
           "    (drop / rename / keep). Transistors is the one with real judgment (7 existing",
           "    bjt params being consolidated; vce_max->v_ce_ds_max, ic_max->i_c_d_max renames).",
           "  - connectors: ADOPT yes/no (reuse native 38-col schema for all 17 connector tables).",
           "  - CERN-only table: Confirm yes (bless existing tail). Passives are deferred.",
           "",
           "  PROJECT STATE (where the whole effort stands):",
           "  - CERN import COMPLETE: 35 cern_* tables, ~15.4k parts (skill: skills/port-cern-library).",
           "  - Datasheets: ~1,556 matched/equivalent banked via cheap tiers (TI template ~1253,",
           "    commodity Diodes/TI ~290, open-CDN search). Resumable system: skills/fetch-cern-",
           "    datasheets/SKILL.md, tools/datasheets/*, log = assets/datasheets/acquisition.jsonl,",
           "    browse = assets/datasheets/by-name/. ~8.8k remain = EXPENSIVE LONG TAIL, DEFERRED",
           "    (bot-blocked majors like onsemi 403; revisit later w/ Playwright or leave partial).",
           "  - STRATEGY (memory: terra-library-direction): go-forward terra lib is KiCad-symbol-",
           "    derived; source from EASIEST MAJOR manufacturer; datasheets MUST match the part",
           "    (keep original manufacturer, don't switch to a 2nd source); CERN = reuse cache;",
           "    prefer parts we can match. Phase 0 (this) is the bridge to the terra PASSIVE",
           "    generators (the real high-ROI work: resistors/caps/inductors via per-series",
           "    generators, like the existing resistors_smt 22k / capacitors_smt 4.8k).",
           "  - Manufacturer-switch idea was SCRAPPED (all switch candidates were major originals;",
           "    DB never changed). open-CDN majors (Microchip/PowerIntegrations/Nexperia/TI/Diodes/",
           "    Wurth) are curl-friendly; onsemi/ADI/ST bot-block.",
           "",
           "  KEY FILES: this review + 2026-06-10-phase0-schema-consolidation.md (the plan) +",
           "  2026-06-10-datasheet-param-resolver-design.md (resolver spec). Tools: gen_schema_",
           "  review.py (this), tools/datasheets/{build_worklist,remaining,ingest,audit,",
           "  link_by_name,template_sweep,propose_switches}.py, tools/fetch_datasheets.workflow.js.",
           "  Branch: feat/tier-tag-system. Specs go at REPO ROOT (not docs/superpowers/), per Dave.",
           "",
           "#+NOTE: Decision = keep | drop | add (edit cells). 'In' shows which tables already have the column.",
           "#+NOTE: Proposed canonical tail per type. Core = the 34 shared columns (not shown).",
           "",
           "* Universal drop (applies to ALL native non-passive tables) — confirm once",
           "  These legacy flat-`symbols` columns are dropped everywhere (duplicates of core "
           "fields or dead SPICE/temp placeholders). Object here if you want any kept globally:",
           "  " + ", ".join(sorted(LEGACY_CRUFT)),
           "  Decision: DROP-ALL (yes/no)",
           ""]

    for typ, (nat, crn) in TYPES.items():
        present = {}  # column -> set of tables having it
        for t in nat + crn:
            for c in tail(t):
                present.setdefault(c, set()).add("native" if t in nat else "cern")
        out.append(f"* {typ}   (tables: {', '.join(nat + crn)})")
        if typ == "connectors":
            out.append("  Adopt the existing native `connectors` 38-column schema verbatim "
                       "for all 17 connector tables. Decision: ADOPT (yes/no).")
            out.append(f"  current native tail columns: {len(tail('connectors'))}")
            out.append("")
            continue
        prop = {c: (st, why) for c, st, why in PROPOSALS[typ]}
        out.append("| Decision | Column | Type | In | Rationale |")
        out.append("|----------+--------+------+----+-----------|")
        for c, st, why in PROPOSALS[typ]:
            inn = "+".join(sorted(present.get(c, []))) or "NEW"
            dec = "keep" if c in present else "add"
            out.append(f"| {dec} | {c} | {st} | {inn} | {why} |")
        # type-specific drops: current columns not in the proposal AND not universal cruft.
        # These are real existing columns being dropped/renamed — they need your eye.
        drops = [c for c in present if c not in prop and c not in LEGACY_CRUFT]
        for c in sorted(drops):
            out.append(f"| drop? | {c} | - | {'+'.join(sorted(present[c]))} | "
                       f"existing column not in proposal — drop, rename, or keep? |")
        out.append("")

    out.append("* CERN-only types — CONFIRM existing tail as canonical (light review)")
    out.append("| Confirm | Type | Current tail columns |")
    out.append("|---------+------+----------------------|")
    for t in CERN_ONLY:
        tl = tail(t)
        out.append(f"| yes | {t.replace('cern_', '')} | {', '.join(tl) if tl else '(none — grab-bag)'} |")
    out.append("")
    out.append("* Deferred: resistors, capacitors (populated passives; fragments defined later as supersets)")

    ORG.write_text("\n".join(out))
    print(f"wrote {ORG.relative_to(ROOT)}  ({len(TYPES)} review types + {len(CERN_ONLY)} CERN-only confirms)")


if __name__ == "__main__":
    main()
