#!/usr/bin/env python3
"""Standard (bipolar, no-letter) 7400-series TTL from TI: the plain SN74xx parts.

These are not the 74LS parts with a different name. Speed, input loading, output drive
and supply current all differ, and in timing circuits the difference shows: an SN74123
gives tw = 0.28 * RT * Cext * (1 + 0.7/RT), while an SN74LS123 gives about 0.45 * RT * Cext
with a 5-260 kohm Rext range instead of 5-50 kohm. A 7404 crystal oscillator biased for
standard TTL input current won't run the same on a 74LS04. So each part gets its own row,
value "7404" (not "74LS04"), data-sheet timing, and allow_substitution = 'No'.

Parts: what the OSI 470 board uses (7404, 7407, 7417, 7410, 7430, 7493A, 74123, 74390)
plus 7400, 7402 and 7454, which run_320_ttl_harvest.py used to emit from KiCad's only
three standard-TTL symbols. That harvest invented an SOIC row for each; here a package
gets a row only if TI's package-option addendum (in each data sheet, 2026 printing)
lists it:
  - Active: SN7400N/D, SN7402N, SN7404N/DR, SN7407N/DR, SN7417N/DR, SN74123N. The
    SOIC tube codes SN7404D/SN7407D/SN7417D are Obsolete there, so the reel code is used.
  - Gone from the addendum and from TI's product pages (404), Mouser lists them as
    obsolete or not at all (2026-11-24): SN7410N, SN7430N, SN7454N, SN7493AN, SN74390N.
    They are kept as Obsolete PDIP rows for restorations, which buy NOS/surplus.

Added 2026-11-24 from the OSI C1P, C2/C3 and C4P SAMS Computerfacts parts lists
(~/vsrc/osiweb): 7401, 7403, 7408, 7414, 7420, 7438, 7473, 7474, 7475, 7476, 7492A,
74125, 74148, 74151A, 74155, 74157, 74163, 74164, 74165, 74174, 74175, 74193, 74393,
and the Schottky 74S10, 74S20, 74S138A (logic_family '74S'). Only SN7414N/DR,
SN7438N/DR, SN74S10N, SN74S20N and SN74S138AN/D are still in TI's addenda (and have TI
product pages); the rest are Obsolete. The 74111, 74154 and 74S113A sheets
(sn74111.pdf SDLS038, sn74154.pdf SDLS056, sn74s113a.pdf D2661) are TI's, supplied by
Dave from datasheet-archive mirrors; all three are Obsolete. The C2/C3 list prints
"SN74113N", but TI's 113 exists only as 74S113/74LS113, so it is generated as the
SN74S113A. KiCad has no 74111 symbol; terra_symbols_ic_logic:74111 is KiCad's 74LS76
body with the pins renumbered to the 74111 pinout. The 7473 and 7476 are master-slave (pulse-triggered), unlike the
negative-edge-triggered 74LS73A/74LS76A, which matters on a schematic that relies on it.

Symbols: KiCad's 74xx library has standard-TTL symbols only for 7400, 7402 and 7454;
the rest use the 74LS symbol of the same pinout (74HC164 for the 74164), checked pin for
pin, including the 7401's outputs on 1/4/10/13 and the off-corner supply pins of the
7473 (4/11), 7475 (5/12), 7476 (5/13), 7492A and 7493A (5/10). 74xx_IEEE symbols are
added as variant 'IEEE' rows where one exists.

Data sheets (datasheets/ti/, TI's file names; several cover the LS part too):
  sn7400.pdf, sn7402.pdf, sn7404.pdf (SDLS029C), sn7407.pdf (7407 and 7417),
  sn74123.pdf (SDLS043), sn74ls10.pdf (SDLS035A), sn74ls30.pdf (SDLS099),
  sn54ls54.pdf (SDLS115), sn74ls90.pdf (SDLS940A, '92A/'93A columns),
  sn74ls390.pdf (SDLS107, '390/'393), sn54ls01.pdf (SDLS026), sn74ls03.pdf (SDLS028),
  sn74ls08.pdf (SDLS033), sn7414.pdf (SDLS049C), sn74ls20.pdf (SDLS079, 7420/74S20),
  sn7438.pdf (SDLS105), sn74ls73a.pdf (SDLS118), sn74ls74a.pdf (SDLS119),
  sn74ls75.pdf (SDLS120), sn54ls76a.pdf (SDLS121), sn74ls125a.pdf (SDLS044A),
  sn74ls174.pdf (SDLS068A, '174/'175), sn74s138a.pdf (SDLS014), sn74ls148.pdf
  (SDLS053B), sn74ls151.pdf (SDLS054), sn74ls155a.pdf (SDLS057), sn74ls157.pdf
  (SDLS058), sn74ls163a.pdf (SDLS060), sn74ls164.pdf, sn74ls165a.pdf (SDLS062D),
  sn74ls193.pdf (SDLS074).
Switching figures are at VCC = 5 V, TA = 25 C, RL = 400 ohm, CL = 15 pF unless noted.
Plan: plans/ic-logic-standard-ttl.md.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "ic_logic_generated_315_ttl_standard.sql"
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets/ti"

COLS = [
    "unique_id", "variant", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "standards_version", "source", "dump_priority", "tier", "lifecycle_status",
    "created_by", "keywords",
    "pin_count", "temp_operating_min", "temp_operating_max",
    "logic_family", "base_number", "gate_function", "function_category",
    "channels", "inputs_per_gate", "bit_width", "logic_polarity", "output_type",
    "schmitt_trigger", "supply_voltage_min", "supply_voltage_max",
    "vih_min", "vil_max", "voh_min", "vol_max", "propagation_delay",
    "max_frequency", "output_current", "supply_current",
]

# Standard-TTL recommended operating conditions (SN74 columns, every sheet here).
FAMILY = dict(
    manufacturer="Texas Instruments", logic_family="74", tracking="No",
    allow_substitution="No", standards_version="1.0", source=None, dump_priority=0,
    tier=2, created_by=CREATED_BY, temp_operating_min=0, temp_operating_max=70,
    schmitt_trigger="no", supply_voltage_min=4.75, supply_voltage_max=5.25,
    vih_min=2.0, vil_max=0.8, voh_min=2.4, vol_max=0.4, output_type="totem-pole",
    output_current="IOL 16mA / IOH -0.4mA",
)

FOOTPRINT = {
    ("PDIP", 14): "Package_DIP:DIP-14_W7.62mm",
    ("PDIP", 16): "Package_DIP:DIP-16_W7.62mm",
    ("PDIP", 24): "Package_DIP:DIP-24_W15.24mm",
    ("SOIC", 14): "Package_SO:SOIC-14_3.9x8.7mm_P1.27mm",
    ("SOIC", 16): "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
}
PKG_OF = {"N": "PDIP", "D": "SOIC", "DR": "SOIC"}


def tpd(*paths):
    """('A->Y', tplh_typ, tplh_max, tphl_typ, tphl_max) -> data-sheet text."""
    out = []
    for name, lt, lm, ht, hm in paths:
        pre = f"{name} " if name else ""
        if lt is None:
            out.append(f"{pre}tPHL {ht}/{hm} ns")
        elif ht is None:
            out.append(f"{pre}tPLH {lt}/{lm} ns")
        else:
            out.append(f"{pre}tPLH {lt}/{lm} ns, tPHL {ht}/{hm} ns")
    return "; ".join(out) + " (typ/max)"


def icc(h, l):
    return f"ICCH {h[0]}/{h[1]} mA, ICCL {l[0]}/{l[1]} mA (typ/max)"


def D(**kw):
    return kw


# codes: (MPN suffix, lifecycle). sym: the 74xx symbol used; ieee: 74xx_IEEE symbol or None.
DEVICES = [
    D(base="00", mpn="SN7400", codes=[("N", "Active"), ("D", "Active")], pins=14,
      sym="7400", ieee="7400", ds="sn7400.pdf", link=True,
      gate_function="Quadruple 2-input positive-NAND gate", function_category="gate",
      channels=4, inputs_per_gate=2, logic_polarity="inverting",
      propagation_delay=tpd(("", 11, 22, 7, 15)), supply_current=icc((4, 8), (12, 22)),
      kw="NAND,quad 2-input NAND"),
    D(base="02", mpn="SN7402", codes=[("N", "Active")], pins=14,
      sym="7402", ieee="7402", ds="sn7402.pdf", link=True,
      gate_function="Quadruple 2-input positive-NOR gate", function_category="gate",
      channels=4, inputs_per_gate=2, logic_polarity="inverting",
      propagation_delay=tpd(("", 12, 22, 8, 15)), supply_current=icc((8, 16), (14, 27)),
      kw="NOR,quad 2-input NOR"),
    D(base="04", mpn="SN7404", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS04", ieee="7404", ds="sn7404.pdf", link=True,
      gate_function="Hex inverter", function_category="gate",
      channels=6, inputs_per_gate=1, logic_polarity="inverting",
      propagation_delay=tpd(("", 12, 22, 8, 15)), supply_current=icc((6, 12), (18, 33)),
      kw="inverter,hex inverter,NOT,clock oscillator"),
    D(base="07", mpn="SN7407", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS07", ieee="7407", ds="sn7407.pdf", link=True,
      gate_function="Hex buffer/driver, open-collector high-voltage outputs (30 V)",
      function_category="buffer", channels=6, inputs_per_gate=1,
      logic_polarity="non-inverting", output_type="open-collector",
      voh_min=None, vol_max=0.7,
      output_current="IOL 40mA, VOH max 30V (VOL 0.7V at 40mA, 0.4V at 16mA)",
      propagation_delay=tpd(("", 6, 10, 20, 30)) + ", RL 110 ohm",
      supply_current=icc((29, 41), (21, 30)),
      kw="buffer,driver,open collector,open-collector,30V,hex buffer"),
    D(base="17", mpn="SN7417", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS07", ieee="7417", ds="sn7407.pdf", link=True,
      gate_function="Hex buffer/driver, open-collector high-voltage outputs (15 V)",
      function_category="buffer", channels=6, inputs_per_gate=1,
      logic_polarity="non-inverting", output_type="open-collector",
      voh_min=None, vol_max=0.7,
      output_current="IOL 40mA, VOH max 15V (VOL 0.7V at 40mA, 0.4V at 16mA)",
      propagation_delay=tpd(("", 6, 10, 20, 30)) + ", RL 110 ohm",
      supply_current=icc((29, 41), (21, 30)),
      kw="buffer,driver,open collector,open-collector,15V,hex buffer"),
    D(base="10", mpn="SN7410", codes=[("N", "Obsolete")], pins=14,
      sym="74LS10", ieee="7410", ds="sn74ls10.pdf", link=False,
      gate_function="Triple 3-input positive-NAND gate", function_category="gate",
      channels=3, inputs_per_gate=3, logic_polarity="inverting",
      propagation_delay=tpd(("", 11, 22, 7, 15)), supply_current=icc((3, 6), (9, 16.5)),
      kw="NAND,triple 3-input NAND"),
    D(base="30", mpn="SN7430", codes=[("N", "Obsolete")], pins=14,
      sym="74LS30", ieee="7430", ds="sn74ls30.pdf", link=False,
      gate_function="8-input positive-NAND gate", function_category="gate",
      channels=1, inputs_per_gate=8, logic_polarity="inverting",
      propagation_delay=tpd(("", 13, 22, 8, 15)), supply_current=icc((1, 2), (3, 6)),
      kw="NAND,8-input NAND"),
    D(base="54", mpn="SN7454", codes=[("N", "Obsolete")], pins=14,
      sym="7454", ieee="7454", ds="sn54ls54.pdf", link=False,
      gate_function="4-wide 2-2-2-2-input AND-OR-INVERT gate, Y = /(AB + CD + EF + GH)",
      function_category="gate", channels=1, inputs_per_gate=2,
      logic_polarity="inverting",
      propagation_delay=tpd(("", 13, 22, 8, 15)), supply_current=icc((4, 8), (5.1, 9.5)),
      kw="AND-OR-INVERT,AOI,and-nor"),
    D(base="93", mpn="SN7493A", codes=[("N", "Obsolete")], pins=14,
      sym="74LS93", ieee="7493", ds="sn74ls90.pdf", link=False,
      gate_function="4-bit binary counter (divide-by-2 and divide-by-8), VCC pin 5, GND pin 10",
      function_category="counter", channels=1, bit_width=4,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="CKA 32 MHz min / 42 MHz typ, CKB 16 MHz min",
      propagation_delay=tpd(("CKA->QA", 10, 16, 12, 18), ("CKA->QD", 46, 70, 46, 70),
                            ("R0->any", None, None, 26, 40)),
      supply_current="ICC 26/39 mA (typ/max)",
      kw="counter,binary counter,ripple counter,divide by 16"),
    D(base="123", mpn="SN74123", codes=[("N", "Active")], pins=16,
      sym="74LS123", ieee=None, ds="sn74123.pdf", link=True,
      gate_function="Dual retriggerable monostable multivibrator with clear",
      function_category="monostable", channels=2,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("A->Q", 22, 33, None, None), ("B->Q", 19, 28, None, None),
                            ("A->/Q", None, None, 30, 40), ("Clear->Q", None, None, 18, 27)),
      supply_current="ICC 46/66 mA (typ/max)",
      timing=("tw = 0.28 x RT x Cext x (1 + 0.7/RT) for Cext > 1000 pF (RT kohm, Cext pF, "
              "tw ns; 0.25 with the diode circuit); Rext 5-50 kohm external only; "
              "tw 3.03 us typ at 10 kohm / 1000 pF; tw(min) 45 ns typ. "
              "Not interchangeable with the 74LS123 (about 0.45 x RT x Cext)"),
      kw="monostable,one-shot,multivibrator,retriggerable,timer"),
    D(base="390", mpn="SN74390", codes=[("N", "Obsolete")], pins=16,
      sym="74LS390", ieee="74LS390", ds="sn74ls390.pdf", link=False,
      gate_function="Dual 4-bit decade counter (divide-by-2 and divide-by-5 sections)",
      function_category="counter", channels=2, bit_width=4,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="A 25 MHz min / 35 MHz typ, B 20 MHz min / 30 MHz typ",
      propagation_delay=tpd(("A->QA", 12, 20, 13, 20), ("A->QC", 37, 60, 39, 60),
                            ("Clear->any", None, None, 24, 39)),
      supply_current="ICC 42/69 mA (typ/max)",
      kw="counter,decade counter,BCD counter,divide by 10"),

    # --- added 2026-11-24 from the OSI C1P/C2/C3/C4P SAMS parts lists ---
    D(base="01", mpn="SN7401", codes=[("N", "Obsolete")], pins=14,
      sym="74LS01", ieee="7401", ds="sn54ls01.pdf", link=False,
      gate_function=("Quadruple 2-input positive-NAND gate, open-collector outputs "
                     "(7401 pinout: outputs on pins 1, 4, 10, 13)"),
      function_category="gate", channels=4, inputs_per_gate=2,
      logic_polarity="inverting", output_type="open-collector", voh_min=None,
      output_current="IOL 16mA, VOH max 5.5V (open collector)",
      propagation_delay="tPLH 35/55 ns (RL 4 kohm), tPHL 8/15 ns (RL 400 ohm) (typ/max)",
      supply_current=icc((4, 8), (12, 22)), kw="NAND,open collector,open-collector"),
    D(base="03", mpn="SN7403", codes=[("N", "Obsolete")], pins=14,
      sym="74LS03", ieee="7403", ds="sn74ls03.pdf", link=False,
      gate_function="Quadruple 2-input positive-NAND gate, open-collector outputs",
      function_category="gate", channels=4, inputs_per_gate=2,
      logic_polarity="inverting", output_type="open-collector", voh_min=None,
      output_current="IOL 16mA, VOH max 5.5V (open collector)",
      propagation_delay="tPLH 35/45 ns (RL 4 kohm), tPHL 8/15 ns (RL 400 ohm) (typ/max)",
      supply_current=icc((4, 8), (12, 22)), kw="NAND,open collector,open-collector"),
    D(base="08", mpn="SN7408", codes=[("N", "Obsolete")], pins=14,
      sym="74LS08", ieee="7408", ds="sn74ls08.pdf", link=False,
      gate_function="Quadruple 2-input positive-AND gate", function_category="gate",
      channels=4, inputs_per_gate=2, logic_polarity="non-inverting",
      output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("", 17.5, 27, 12, 19)), supply_current=icc((11, 21), (20, 33)),
      kw="AND,quad 2-input AND"),
    D(base="14", mpn="SN7414", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS14", ieee="7414", ds="sn7414.pdf", link=True,
      gate_function=("Hex Schmitt-trigger inverter (VT+ 1.7 V, VT- 0.9 V, "
                     "hysteresis 0.8 V typ)"),
      function_category="gate", channels=6, inputs_per_gate=1,
      logic_polarity="inverting", schmitt_trigger="yes",
      output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("", 15, 22, 15, 22)), supply_current=icc((22, 36), (39, 60)),
      kw="Schmitt trigger,inverter,hex inverter,oscillator"),
    D(base="20", mpn="SN7420", codes=[("N", "Obsolete")], pins=14,
      sym="74LS20", ieee="7420", ds="sn74ls20.pdf", link=False,
      gate_function="Dual 4-input positive-NAND gate", function_category="gate",
      channels=2, inputs_per_gate=4, logic_polarity="inverting",
      propagation_delay=tpd(("", 12, 22, 8, 15)), supply_current=icc((2, 4), (6, 11)),
      kw="NAND,dual 4-input NAND"),
    D(base="38", mpn="SN7438", codes=[("N", "Active"), ("DR", "Active")], pins=14,
      sym="74LS38", ieee="7438", ds="sn7438.pdf", link=True,
      gate_function="Quadruple 2-input positive-NAND buffer, open-collector outputs",
      function_category="buffer", channels=4, inputs_per_gate=2,
      logic_polarity="inverting", output_type="open-collector", voh_min=None,
      output_current="IOL 48mA, VOH max 5.5V (open collector)",
      propagation_delay="tPLH 14/22 ns, tPHL 11/18 ns (typ/max), RL 133 ohm, CL 45 pF",
      supply_current=icc((5, 8.5), (34, 54)),
      kw="NAND,buffer,driver,open collector,open-collector"),
    D(base="73", mpn="SN7473", codes=[("N", "Obsolete")], pins=14,
      sym="74LS73", ieee=None, ds="sn74ls73a.pdf", link=False,
      gate_function=("Dual J-K flip-flop with clear, master-slave (pulse-triggered; the "
                     "74LS73A is negative-edge-triggered), VCC pin 4, GND pin 11"),
      function_category="flip-flop", channels=2, logic_polarity="non-inverting",
      max_frequency="15 MHz min / 20 MHz typ",
      propagation_delay=("CLK->Q tPLH 16/25 ns, tPHL 25/40 ns; CLR->Q tPHL 25/40 ns "
                         "(typ/max)"),
      supply_current="ICC 10/20 mA per flip-flop (typ/max)",
      kw="flip-flop,JK,J-K,master-slave"),
    D(base="74", mpn="SN7474", codes=[("N", "Obsolete")], pins=14,
      sym="74LS74", ieee=None, ds="sn74ls74a.pdf", link=False,
      gate_function="Dual D-type positive-edge-triggered flip-flop with preset and clear",
      function_category="flip-flop", channels=2, logic_polarity="non-inverting",
      max_frequency="15 MHz min / 25 MHz typ",
      propagation_delay=("CLK->Q tPLH 14/25 ns, tPHL 20/40 ns (typ/max); PRE/CLR->Q "
                         "tPLH 25 ns max, tPHL 40 ns max"),
      supply_current="ICC 8.5/15 mA per flip-flop (typ/max)",
      kw="flip-flop,D flip-flop,D-type"),
    D(base="75", mpn="SN7475", codes=[("N", "Obsolete")], pins=16,
      sym="74LS75", ieee=None, ds="sn74ls75.pdf", link=False,
      gate_function="4-bit bistable latch, VCC pin 5, GND pin 12",
      function_category="latch", channels=4, bit_width=4,
      logic_polarity="non-inverting",
      propagation_delay=tpd(("D->Q", 16, 30, 14, 25), ("C->Q", 16, 30, 7, 15)),
      supply_current="ICC 32/53 mA (typ/max)", kw="latch,transparent latch,4-bit latch"),
    D(base="76", mpn="SN7476", codes=[("N", "Obsolete")], pins=16,
      sym="74LS76", ieee=None, ds="sn54ls76a.pdf", link=False,
      gate_function=("Dual J-K flip-flop with preset and clear, master-slave "
                     "(pulse-triggered; the 74LS76A is negative-edge-triggered), "
                     "VCC pin 5, GND pin 13"),
      function_category="flip-flop", channels=2, logic_polarity="non-inverting",
      max_frequency="15 MHz min / 20 MHz typ",
      propagation_delay=tpd(("CLK->Q", 16, 25, 25, 40), ("PRE/CLR->Q", 16, 25, 25, 40)),
      supply_current="ICC 10/20 mA per flip-flop (typ/max)",
      kw="flip-flop,JK,J-K,master-slave"),
    D(base="125", mpn="SN74125", codes=[("N", "Obsolete")], pins=14,
      sym="74LS125", ieee="74125", ds="sn74ls125a.pdf", link=False,
      gate_function="Quadruple bus buffer, 3-state outputs, active-low enables",
      function_category="buffer", channels=4, inputs_per_gate=1,
      logic_polarity="non-inverting", output_type="3-state",
      output_current="IOL 16mA / IOH -5.2mA",
      propagation_delay=("A->Y tPLH 8/13 ns, tPHL 12/18 ns; G->Y tPZH 11/17 ns, "
                         "tPZL 16/25 ns (typ/max), CL 50 pF"),
      supply_current="ICC 32/54 mA (typ/max)", kw="buffer,bus buffer,3-state,tri-state"),
    D(base="174", mpn="SN74174", codes=[("N", "Obsolete")], pins=16,
      sym="74LS174", ieee=None, ds="sn74ls174.pdf", link=False,
      gate_function="Hex D-type flip-flop with clear", function_category="flip-flop",
      channels=6, bit_width=6, logic_polarity="non-inverting",
      output_current="IOL 16mA / IOH -0.8mA", max_frequency="25 MHz min / 35 MHz typ",
      propagation_delay=tpd(("CLK->Q", 20, 30, 24, 35), ("CLR->Q", None, None, 23, 35)),
      supply_current="ICC 45/65 mA (typ/max)", kw="flip-flop,D flip-flop,register,hex"),
    D(base="175", mpn="SN74175", codes=[("N", "Obsolete")], pins=16,
      sym="74LS175", ieee=None, ds="sn74ls174.pdf", link=False,
      gate_function="Quadruple D-type flip-flop with clear, complementary outputs",
      function_category="flip-flop", channels=4, bit_width=4,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="25 MHz min / 35 MHz typ",
      propagation_delay=tpd(("CLK->Q", 20, 30, 24, 35), ("CLR->Q", None, None, 23, 35),
                            ("CLR->/Q", 16, 25, None, None)),
      supply_current="ICC 30/45 mA (typ/max)", kw="flip-flop,D flip-flop,register,quad"),
    D(base="92", mpn="SN7492A", codes=[("N", "Obsolete")], pins=14,
      sym="74LS92", ieee="7492", ds="sn74ls90.pdf", link=False,
      gate_function="Divide-by-12 counter (divide-by-2 and divide-by-6), VCC pin 5, GND pin 10",
      function_category="counter", channels=1, bit_width=4,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="CKA 32 MHz min / 42 MHz typ, CKB 16 MHz min",
      propagation_delay=tpd(("CKA->QA", 10, 16, 12, 18), ("CKA->QD", 32, 48, 34, 50),
                            ("R0->any", None, None, 26, 40)),
      supply_current="ICC 26/39 mA (typ/max)", kw="counter,divide by 12,ripple counter"),
    D(base="148", mpn="SN74148", codes=[("N", "Obsolete")], pins=16,
      sym="74LS148", ieee="74148", ds="sn74ls148.pdf", link=False,
      gate_function="8-line to 3-line priority encoder", function_category="encoder",
      channels=1, logic_polarity="inverting", output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("1-7->A", 13, 19, 12, 19), ("EI->A", 10, 15, 10, 15),
                            ("0-7->GS", 18, 30, 14, 25)),
      supply_current="ICC 40/60 mA (typ/max)", kw="encoder,priority encoder,8-to-3"),
    D(base="151", mpn="SN74151A", codes=[("N", "Obsolete")], pins=16,
      sym="74LS151", ieee="74151", ds="sn74ls151.pdf", link=False,
      gate_function="1-of-8 data selector/multiplexer, complementary outputs",
      function_category="mux", channels=1, logic_polarity="non-inverting",
      output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("select->Y", 25, 38, 25, 38), ("D->Y", 13, 20, 18, 27),
                            ("G->Y", 21, 33, 22, 33)),
      supply_current="ICC 29/48 mA (typ/max)", kw="multiplexer,data selector,8-to-1,mux"),
    D(base="155", mpn="SN74155", codes=[("N", "Obsolete")], pins=16,
      sym="74LS155", ieee="74155", ds="sn74ls155a.pdf", link=False,
      gate_function="Dual 2-line to 4-line decoder/demultiplexer, totem-pole outputs",
      function_category="decoder", channels=2, logic_polarity="inverting",
      output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("A/B->Y", 21, 32, 21, 32), ("G->Y", 13, 20, 18, 27)),
      supply_current="ICC 25/40 mA (typ/max)", kw="decoder,demultiplexer,2-to-4"),
    D(base="157", mpn="SN74157", codes=[("N", "Obsolete")], pins=16,
      sym="74LS157", ieee="74157", ds="sn74ls157.pdf", link=False,
      gate_function="Quadruple 2-line to 1-line data selector/multiplexer",
      function_category="mux", channels=4, logic_polarity="non-inverting",
      output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("data->Y", 9, 14, 9, 14), ("select->Y", 15, 23, 18, 27),
                            ("G->Y", 13, 20, 14, 21)),
      supply_current="ICC 30/48 mA (typ/max)", kw="multiplexer,data selector,2-to-1,mux"),
    D(base="163", mpn="SN74163", codes=[("N", "Obsolete")], pins=16,
      sym="74LS163", ieee=None, ds="sn74ls163a.pdf", link=False,
      gate_function="Synchronous 4-bit binary counter, synchronous clear",
      function_category="counter", channels=1, bit_width=4,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="25 MHz min / 32 MHz typ",
      propagation_delay=tpd(("CLK->Q", 13, 20, 15, 23), ("CLK->RCO", 23, 35, 23, 35),
                            ("ENT->RCO", 11, 16, 11, 16)),
      supply_current="ICCH 59/94 mA, ICCL 63/101 mA (typ/max)",
      kw="counter,binary counter,synchronous counter"),
    D(base="164", mpn="SN74164", codes=[("N", "Obsolete")], pins=14,
      sym="74HC164", ieee="74164", ds="sn74ls164.pdf", link=False,
      gate_function="8-bit serial-in, parallel-out shift register",
      function_category="shift-register", channels=1, bit_width=8,
      logic_polarity="non-inverting", output_current="IOL 8mA / IOH -0.4mA",
      max_frequency="25 MHz min / 36 MHz typ",
      propagation_delay=tpd(("CLK->Q", 17, 27, 21, 32), ("CLR->Q", None, None, 24, 36))
      + ", RL 800 ohm",
      supply_current="ICC 37/54 mA (typ/max)", kw="shift register,SIPO,serial to parallel"),
    D(base="165", mpn="SN74165", codes=[("N", "Obsolete")], pins=16,
      sym="74LS165", ieee="74165", ds="sn74ls165a.pdf", link=False,
      gate_function="8-bit parallel-load shift register, complementary outputs",
      function_category="shift-register", channels=1, bit_width=8,
      logic_polarity="non-inverting", output_current="IOL 16mA / IOH -0.8mA",
      max_frequency="20 MHz min / 26 MHz typ",
      propagation_delay=tpd(("LD->any", 21, 31, 27, 40), ("CLK->any", 16, 24, 21, 31)),
      supply_current="ICC 42/63 mA (typ/max)", kw="shift register,PISO,parallel to serial"),
    D(base="193", mpn="SN74193", codes=[("N", "Obsolete")], pins=16,
      sym="74LS193", ieee=None, ds="sn74ls193.pdf", link=False,
      gate_function="Synchronous 4-bit up/down binary counter, dual clock with clear",
      function_category="counter", channels=1, bit_width=4,
      logic_polarity="non-inverting",
      max_frequency="25 MHz min / 32 MHz typ",
      propagation_delay=tpd(("UP/DOWN->Q", 25, 38, 31, 47), ("UP->CO", 17, 26, 16, 24),
                            ("CLR->Q", None, None, 22, 35)),
      supply_current="ICC 65/102 mA (typ/max)", kw="counter,up/down counter,binary counter"),
    D(base="393", mpn="SN74393", codes=[("N", "Obsolete")], pins=14,
      sym="74LS393", ieee=None, ds="sn74ls390.pdf", link=False,
      gate_function="Dual 4-bit binary counter", function_category="counter",
      channels=2, bit_width=4, logic_polarity="non-inverting",
      output_current="IOL 16mA / IOH -0.8mA", max_frequency="25 MHz min / 35 MHz typ",
      propagation_delay=tpd(("A->QA", 12, 20, 13, 20), ("A->QD", 40, 60, 40, 60),
                            ("Clear->any", None, None, 24, 39)),
      supply_current="ICC 38/64 mA (typ/max)", kw="counter,binary counter,ripple counter"),
    D(base="111", mpn="SN74111", codes=[("N", "Obsolete")], pins=16,
      sym="terra_symbols_ic_logic:74111", ieee=None, ds="sn74111.pdf", link=False,
      gate_function=("Dual J-K master-slave flip-flop with data lockout, preset and clear "
                     "(J/K accepted for 30 ns after the rising clock edge, output on the "
                     "falling edge)"),
      function_category="flip-flop", channels=2, logic_polarity="non-inverting",
      output_current="IOL 16mA / IOH -0.8mA", max_frequency="20 MHz min / 25 MHz typ",
      propagation_delay=tpd(("CLK->Q", 12, 17, 20, 30), ("PRE/CLR->Q", 12, 18, 21, 30)),
      supply_current="ICC 14/20.5 mA per flip-flop (typ/max)",
      kw="flip-flop,JK,J-K,master-slave,data lockout"),
    D(base="154", mpn="SN74154", codes=[("N", "Obsolete")], pins=24,
      sym="74LS154", ieee="74154", ds="sn74154.pdf", link=False,
      gate_function="4-line to 16-line decoder/demultiplexer, 0.6 in DIP",
      function_category="decoder", channels=1, logic_polarity="inverting",
      output_current="IOL 16mA / IOH -0.8mA",
      propagation_delay=tpd(("A-D->Y", 24, 36, 22, 33), ("G->Y", 20, 30, 18, 27)),
      supply_current="ICC 34/56 mA (typ/max)", kw="decoder,demultiplexer,4-to-16"),

    # --- Schottky TTL (74S), same OSI lists ---
    D(fam="74S", base="10", mpn="SN74S10", codes=[("N", "Active")], pins=14,
      sym="74LS10", ieee="7410", ds="sn74ls10.pdf", link=True,
      gate_function="Triple 3-input positive-NAND gate", function_category="gate",
      channels=3, inputs_per_gate=3, logic_polarity="inverting",
      propagation_delay=tpd(("", 3, 4.5, 3, 5)) + ", RL 280 ohm",
      supply_current=icc((7.5, 12), (15, 27)), kw="NAND,triple 3-input NAND"),
    D(fam="74S", base="20", mpn="SN74S20", codes=[("N", "Active")], pins=14,
      sym="74LS20", ieee="7420", ds="sn74ls20.pdf", link=True,
      gate_function="Dual 4-input positive-NAND gate", function_category="gate",
      channels=2, inputs_per_gate=4, logic_polarity="inverting",
      propagation_delay=tpd(("", 3, 4.5, 3, 5)) + ", RL 280 ohm",
      supply_current=icc((5, 8), (10, 18)), kw="NAND,dual 4-input NAND"),
    D(fam="74S", base="138", mpn="SN74S138A", codes=[("N", "Active"), ("D", "Active")],
      pins=16, sym="74LS138", ieee=None, ds="sn74s138a.pdf", link=True,
      gate_function="3-line to 8-line decoder/demultiplexer", function_category="decoder",
      channels=1, logic_polarity="inverting",
      propagation_delay=(tpd(("select->Y", 7.5, 12, 8, 12), ("enable->Y", 5, 8, 7, 11))
                         + ", RL 280 ohm"),
      supply_current="ICC 49/74 mA (typ/max)", kw="decoder,demultiplexer,3-to-8"),
    D(fam="74S", base="113", mpn="SN74S113A", codes=[("N", "Obsolete")], pins=14,
      sym="74LS113", ieee=None, ds="sn74s113a.pdf", link=False,
      gate_function="Dual J-K negative-edge-triggered flip-flop with preset",
      function_category="flip-flop", channels=2, logic_polarity="non-inverting",
      max_frequency="80 MHz min / 125 MHz typ",
      propagation_delay=tpd(("CLK->Q", 4, 7, 5, 7), ("PRE->Q", 4, 7, 5, 7)) + ", RL 280 ohm",
      supply_current="ICC 15/25 mA per flip-flop (typ/max)",
      kw="flip-flop,JK,J-K,edge-triggered"),
]

# Schottky TTL (74S) recommended conditions, where they differ from standard TTL.
FAMILY_S = dict(logic_family="74S", voh_min=2.7, vol_max=0.5,
                output_current="IOL 20mA / IOH -1mA")
FAMILY_NAME = {"74": "standard TTL (not 74LS)", "74S": "Schottky TTL (74S, not 74LS)"}


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def rows():
    out = []
    for dev in DEVICES:
        fam = dev.get("fam", "74")
        value = f"{fam}{dev['base']}"
        for suffix, status in dev["codes"]:
            kind = PKG_OF[suffix]
            pkg = f"{kind}-{dev['pins']}"
            mpn = f"{dev['mpn']}{suffix}"
            desc = f"{dev['gate_function']}, {FAMILY_NAME[fam]}, {pkg}"
            if dev.get("timing"):
                desc += f". {dev['timing']}"
            r = {
                **FAMILY,
                **(FAMILY_S if fam == "74S" else {}),
                **{k: v for k, v in dev.items() if k in COLS},
                "unique_id": f"TI-{mpn}", "mpn": mpn, "value": value,
                "base_number": dev["base"], "package": pkg, "pin_count": str(dev["pins"]),
                "part_locator": f"IC_LOGIC {value} {pkg}",
                "description": desc,
                "datasheet": f"{DS}/{dev['ds']}",
                "manufacturer_link": (f"https://www.ti.com/product/{dev['mpn']}"
                                      if dev["link"] else None),
                "kicad_symbol": dev["sym"] if ":" in dev["sym"] else f"74xx:{dev['sym']}",
                "kicad_footprint": FOOTPRINT[(kind, dev["pins"])],
                "lifecycle_status": status,
                "rohs": "Yes" if status == "Active" else "No",
                "keywords": ",".join(dict.fromkeys(
                    ["TTL", "Schottky TTL" if fam == "74S" else "standard TTL",
                     "74 series", value, f"SN{value}", dev["mpn"],
                     mpn] + dev["kw"].split(","))),
            }
            out.append(r)
            if dev["ieee"]:
                out.append({**r, "variant": "IEEE", "unique_id": r["unique_id"] + "-IEEE",
                            "kicad_symbol": f"74xx_IEEE:{dev['ieee']}"})
    return out


def check(rs):
    for dev in DEVICES:
        p = ROOT / "datasheets" / "ti" / dev["ds"]
        if not p.exists():
            raise SystemExit(f"missing data sheet {p}")
    ids = [r["unique_id"] for r in rs]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit(f"duplicate unique_id: {sorted(dup)}")


def main():
    rs = rows()
    check(rs)
    lines = [
        "-- Terra EDA Library - standard (no-letter) 74xx TTL, Texas Instruments",
        f"-- Generated by {CREATED_BY}. dump_priority=0: not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in rs:
        vals = ", ".join(sql(r.get(c)) for c in COLS)
        lines.append(f"INSERT INTO ic_logic ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(rs)} rows across {len(DEVICES)} devices")


if __name__ == "__main__":
    main()
