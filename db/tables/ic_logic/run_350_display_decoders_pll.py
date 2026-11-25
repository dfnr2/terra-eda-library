#!/usr/bin/env python3
"""7-segment display decoder/drivers (decimal and hexadecimal) and HC/HCT PLLs.

Fills gaps beside the 74LS46-49, 74LS246-249, CD4543B, CD4056B, CD4033B, CD4046B and
74LS629 already in ic_logic (run_320 / run_330 derive those from KiCad's stock
libraries, which have no 4511, 4026, 74HC4046A, 7046A, 9368 or 14495 symbol).

Decimal (BCD) 7-segment:
  - CD4511B   BCD latch/decoder/driver, NPN emitter-follower source outputs (25 mA).
  - CD4026B   decade counter/divider with decoded 7-segment outputs, display enable.
  - CD74HC4511  HC version of the 4511, same pinout.
Hexadecimal (0-F) 7-segment, obsolete, kept for restorations (buy NOS/surplus):
  - DM9368    Fairchild TTL latch/decoder/driver, constant-current (16-22 mA) source
              outputs for common-cathode LEDs, ripple blanking.
  - MC14495-1 Motorola CMOS latch/decoder/driver, 290 ohm internal series resistors,
              open-drain "j" output for an A-F indicator.
PLLs:
  - CD74HC4046A / CD74HCT4046A  VCO + PC1 (XOR), PC2 (edge), PC3 (RS); pin 15 is
    PC3OUT, not the CD4046B's zener, so the stock 4xxx:4046 symbol is not reused.
  - CD74HC7046A / CD74HCT7046A  VCO + PC1, PC2 and a lock detector (LD pin 1, CLD 15).

Packages: one PDIP and one 1.27 mm SMD row per part, as in run_315/330. Lifecycle and
orderable codes come from TI's package-option addenda (printed 18-Sep-2026 in the data
sheets parked here). CD4511B and CD4026B have no D (SOIC) package; their SMD code is
the NS (5.3 mm SOP). CD74HC4511M (SOIC tube) is Obsolete there, so the M96 reel code is
used. CD74HCT4511E is NRND and is not generated. TI no longer has a CD74HC9046A (no
data sheet or product page), so none is generated.

DM9368N: Digi-Key lists it Obsolete. MC14495P1/DW1: Digi-Key has no listing at all
(2026-11-25). Both rows are lifecycle 'Obsolete'.

Symbols (terra_symbols_ic_logic, drawn from each data sheet's pin diagram):
4511 (also used by the 74HC4511: same pinout, D0-D3 = A-D), 4026, 74HC4046, 74HC7046,
9368, MC14495-1. Stock Driver_LED:MC14495P matches the pin numbers but calls pin 11 an
input (~VCR) and pin 7 ~CLK, while the MC14495-1's pin 11 is the open-drain j output,
so it is not used. The CD4511B / 74HC4511 rows also get a variant 'IEEE' row on the
stock 4xxx_IEEE:4511, whose pinout matches pin for pin.

Data sheets:
  datasheets/ti/cd4511b.pdf (SCHS072B), cd4026b.pdf (SCHS031B), cd74hc4511.pdf
  (SCHS279E), cd74hc4046a.pdf (SCHS204J), cd74hc7046a.pdf (SCHS218C);
  datasheets/fairchild/dm9368-7-segment-decoder-driver-latch.pdf (DS009796, Dec 2001);
  datasheets/motorola/mc14495-1-hex-7-segment-latch-decoder-driver.pdf.
Levels are at VDD = 5 V (4000B / MC14495-1) or VCC = 4.5 V (HC/HCT), TA = 25 C.
Plan: plans/ic-logic-display-decoders-pll.md.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT_FILE = HERE / "ic_logic_generated_350_display_decoders_pll.sql"
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets"
SYM = "terra_symbols_ic_logic"

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

# package kind -> (package label, KiCad footprint); all parts here are 16-pin.
PACKAGE = {
    "PDIP": ("PDIP-16", "Package_DIP:DIP-16_W7.62mm"),
    "SOIC": ("SOIC-16", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm"),
    "SOP": ("SOP-16", "Package_SO:SOIC-16W_5.3x10.2mm_P1.27mm"),      # TI NS0016A
    "SOIC-W": ("SOIC-16W", "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm"),  # Motorola 751G
}

COMMON = dict(tracking="No", standards_version="1.0", source=None, dump_priority=0,
              tier=2, created_by=CREATED_BY, schmitt_trigger="no", channels=1)

# Family recommended conditions (per data sheet; parts override what differs).
TI_4000B = dict(manufacturer="Texas Instruments", logic_family="4000B",
                temp_operating_min=-55, temp_operating_max=125,
                supply_voltage_min=3.0, supply_voltage_max=18.0,
                vih_min=3.5, vil_max=1.5, voh_min=4.95, vol_max=0.05)
TI_HC = dict(manufacturer="Texas Instruments", logic_family="74HC",
             temp_operating_min=-55, temp_operating_max=125,
             supply_voltage_min=2.0, supply_voltage_max=6.0,
             vih_min=3.15, vil_max=1.35, voh_min=4.4, vol_max=0.1,
             output_current="IOL 4mA / IOH -4mA (VCC 4.5V)")
TI_HCT = dict(TI_HC, logic_family="74HCT", supply_voltage_min=4.5,
              supply_voltage_max=5.5, vih_min=2.0, vil_max=0.8)


def D(**kw):
    return kw


PLL_FMAX = ("VCO fmax 38 MHz typ (C1 0pF, R1 9.1k), 24 MHz typ (C1 50pF, R1 3.5k); "
            "center frequency 12 MHz min / 17 MHz typ (C1 40pF, R1 3k, VCC 4.5V)")

# codes: (orderable MPN, package kind, lifecycle). value is what the schematic shows.
DEVICES = [
    # ---- decimal (BCD) 7-segment ----
    D(fam=TI_4000B, base="4511", value="CD4511B", ds="ti/cd4511b.pdf",
      link="https://www.ti.com/product/CD4511B", sym="4511", ieee="4xxx_IEEE:4511",
      codes=[("CD4511BE", "PDIP", "Active"), ("CD4511BNSR", "SOP", "Active")],
      subst="Yes",
      gate_function=("BCD to 7-segment latch/decoder/driver, active-high source outputs "
                     "up to 25 mA, lamp test and blanking, blank for codes > 9"),
      function_category="decoder", bit_width=4, logic_polarity="non-inverting",
      output_type="NPN emitter-follower (source)", voh_min=4.1,
      output_current=("IOH up to -25mA source (VOH 3.10V min at -25mA, VDD 5V); "
                      "IOL 0.51mA min at VOL 0.4V"),
      propagation_delay=("data->out tPLH 660/1320 ns, tPHL 520/1040 ns; BL->out tPLH "
                         "400/800 ns, tPHL 350/700 ns; LT->out tPLH 150/300 ns, tPHL "
                         "250/500 ns (typ/max, VDD 5V, CL 50pF)"),
      supply_current="IDD 0.04/5 µA (typ/max, VDD 5V)",
      kw="BCD to 7-segment,7-segment decoder,display driver,latch,LED driver,MC14511"),
    D(fam=TI_4000B, base="4026", value="CD4026B", ds="ti/cd4026b.pdf",
      link="https://www.ti.com/product/CD4026B", sym="4026", ieee=None,
      codes=[("CD4026BE", "PDIP", "Active"), ("CD4026BNSR", "SOP", "Active")],
      subst="Yes",
      gate_function=("Decade counter/divider with decoded 7-segment outputs, display "
                     "enable in/out, carry out and ungated c-segment output"),
      function_category="counter", logic_polarity="non-inverting",
      output_type="push-pull",
      output_current="IOL 0.51mA / IOH -0.51mA min (VDD 5V)",
      max_frequency="fCL 2.5 MHz min / 5 MHz typ (VDD 5V); 5.5/11 MHz (10V); 8/16 MHz (15V)",
      propagation_delay=("CLK->CO 250/500 ns, CLK->decoded outputs 350/700 ns, RESET->CO "
                         "275/550 ns, RESET->decoded outputs 300/600 ns (typ/max, VDD 5V, "
                         "CL 50pF)"),
      supply_current="IDD 0.04/5 µA (typ/max, VDD 5V)",
      kw="decade counter,7-segment,counter/divider,Johnson counter,display driver"),
    D(fam=TI_HC, base="4511", value="74HC4511", ds="ti/cd74hc4511.pdf",
      link="https://www.ti.com/product/CD74HC4511", sym="4511", ieee="4xxx_IEEE:4511",
      codes=[("CD74HC4511E", "PDIP", "Active"), ("CD74HC4511M96", "SOIC", "Active")],
      subst="Yes",
      gate_function=("BCD to 7-segment latch/decoder/driver, active-high outputs, lamp "
                     "test and blanking, blank for codes > 9"),
      function_category="decoder", bit_width=4, logic_polarity="non-inverting",
      output_type="push-pull",
      output_current=("IOH source up to -10mA at VCC 6V (-7.5mA at 4.5V); "
                      "IOL 4mA (VOL 0.26V max, VCC 4.5V)"),
      propagation_delay=("Dn->out 60 ns, LE->out 54 ns, BL->out 44 ns, LT->out 32 ns max "
                         "(VCC 4.5V, CL 50pF); Dn->out 25 ns typ (VCC 5V, CL 15pF)"),
      supply_current="ICC 8 µA max (VCC 6V)",
      kw="BCD to 7-segment,7-segment decoder,display driver,latch,LED driver,4511"),

    # ---- hexadecimal 7-segment (obsolete) ----
    D(fam=dict(manufacturer="Fairchild Semiconductor", logic_family="9300",
               temp_operating_min=0, temp_operating_max=70,
               supply_voltage_min=4.75, supply_voltage_max=5.25,
               vih_min=2.0, vil_max=0.8, voh_min=2.4, vol_max=0.4),
      uid="Fairchild", base="9368", value="DM9368",
      ds="fairchild/dm9368-7-segment-decoder-driver-latch.pdf", link=None, sym="9368",
      ieee=None, codes=[("DM9368N", "PDIP", "Obsolete")], subst="No",
      gate_function=("Hexadecimal (0-F) 7-segment decoder/driver/latch, constant-current "
                     "source outputs for common-cathode LEDs (no series resistors), "
                     "ripple blanking in/out, active-low latch enable"),
      function_category="decoder", bit_width=4, logic_polarity="non-inverting",
      output_type="constant-current source",
      output_current=("segment IOH -16 to -22mA (constant current, ~20mA at 1.7V LED); "
                      "RBO IOL 3.2mA / IOH -80µA"),
      propagation_delay=("An->a-g tPLH 50 ns, tPHL 75 ns max; LE->a-g tPLH 70 ns, "
                         "tPHL 90 ns max (VCC 5V, CL 15pF, RL 100 ohm)"),
      supply_current="ICC 67 mA max (VCC 5.25V, outputs open)",
      kw="hex to 7-segment,hexadecimal,7-segment decoder,display driver,latch,"
         "LED driver,TTL,9368,DM9368"),
    D(fam=dict(manufacturer="Motorola", logic_family="4000B",
               temp_operating_min=-40, temp_operating_max=85,
               supply_voltage_min=4.5, supply_voltage_max=18.0,
               vih_min=3.5, vil_max=1.5, voh_min=4.0, vol_max=0.05),
      uid="Motorola", base="4495", value="MC14495-1",
      ds="motorola/mc14495-1-hex-7-segment-latch-decoder-driver.pdf", link=None,
      sym="MC14495-1", ieee=None,
      codes=[("MC14495P1", "PDIP", "Obsolete"), ("MC14495DW1", "SOIC-W", "Obsolete")],
      subst="No",
      gate_function=("Hexadecimal (0-F) 7-segment latch/decoder LED driver, NPN "
                     "emitter-follower outputs with 290 ohm internal series resistors "
                     "(no external resistors at VDD 5V), h+i output and open-drain j "
                     "output for an A-F indicator"),
      function_category="decoder", bit_width=4, logic_polarity="non-inverting",
      output_type="NPN emitter-follower (source); j open-drain",
      output_current=("segment VOH 2.4V min at -5mA, 0.8V min at -10mA (VDD 5V), 290 ohm "
                      "internal; j IOL 0.3mA min at VOL 0.4V"),
      propagation_delay=("ABCD->a-g tPLH 935/2400 ns, tPHL 7.0/18.0 µs; LE->a-g tPLH "
                         "1300/3000 ns, tPHL 16/30 µs (typ/max, VDD 5V, CL 50pF)"),
      supply_current="IDD 0.08/0.25 mA quiescent (typ/max, VDD 5V)",
      kw="hex to 7-segment,hexadecimal,7-segment decoder,display driver,latch,"
         "LED driver,14495,MC14495"),

    # ---- PLLs ----
    D(fam=TI_HC, base="4046", value="74HC4046A", ds="ti/cd74hc4046a.pdf",
      link="https://www.ti.com/product/CD74HC4046A", sym="74HC4046", ieee=None,
      codes=[("CD74HC4046AE", "PDIP", "Active"), ("CD74HC4046AM", "SOIC", "Active")],
      subst="Yes", supply_voltage_min=3.0,
      gate_function=("Phase-locked loop with VCO and three phase comparators (PC1 XOR, "
                     "PC2 edge-triggered, PC3 RS flip-flop); VCO 3-6V, digital 2-6V"),
      function_category="pll", output_type="push-pull; PC2OUT 3-state",
      max_frequency=PLL_FMAX,
      propagation_delay=("SIGIN/COMPIN->PC1OUT 40 ns, ->PCPOUT 60 ns, ->PC3OUT 49 ns max "
                         "(VCC 4.5V, CL 50pF)"),
      supply_current="ICC 8 µA max quiescent (VCC 6V)",
      kw="PLL,phase-locked loop,VCO,phase comparator,frequency synthesis,4046"),
    D(fam=TI_HCT, base="4046", value="74HCT4046A", ds="ti/cd74hc4046a.pdf",
      link="https://www.ti.com/product/CD74HCT4046A", sym="74HC4046", ieee=None,
      codes=[("CD74HCT4046AE", "PDIP", "Active"), ("CD74HCT4046AM", "SOIC", "Active")],
      subst="Yes",
      gate_function=("Phase-locked loop with VCO and three phase comparators (PC1 XOR, "
                     "PC2 edge-triggered, PC3 RS flip-flop), TTL-level inputs"),
      function_category="pll", output_type="push-pull; PC2OUT 3-state",
      max_frequency=PLL_FMAX,
      propagation_delay=("SIGIN/COMPIN->PC1OUT 45 ns, ->PCPOUT 68 ns, ->PC3OUT 58 ns max "
                         "(VCC 4.5V, CL 50pF)"),
      supply_current="ICC 8 µA max quiescent (VCC 5.5V)",
      kw="PLL,phase-locked loop,VCO,phase comparator,frequency synthesis,4046"),
    D(fam=TI_HC, base="7046", value="74HC7046A", ds="ti/cd74hc7046a.pdf",
      link="https://www.ti.com/product/CD74HC7046A", sym="74HC7046", ieee=None,
      codes=[("CD74HC7046AE", "PDIP", "Active"), ("CD74HC7046AM", "SOIC", "Active")],
      subst="Yes", supply_voltage_min=3.0,
      gate_function=("Phase-locked loop with VCO, two phase comparators (PC1 XOR, PC2 "
                     "edge-triggered) and lock detector; VCO 3-6V, digital 2-6V"),
      function_category="pll", output_type="push-pull; PC2OUT 3-state",
      max_frequency=PLL_FMAX,
      propagation_delay="SIGIN/COMPIN->PC1OUT 40 ns max (VCC 4.5V, CL 50pF)",
      supply_current="ICC 8 µA max quiescent (VCC 6V)",
      kw="PLL,phase-locked loop,VCO,phase comparator,lock detector,7046"),
    D(fam=TI_HCT, base="7046", value="74HCT7046A", ds="ti/cd74hc7046a.pdf",
      link="https://www.ti.com/product/CD74HCT7046A", sym="74HC7046", ieee=None,
      codes=[("CD74HCT7046AE", "PDIP", "Active"), ("CD74HCT7046AM", "SOIC", "Active")],
      subst="Yes",
      gate_function=("Phase-locked loop with VCO, two phase comparators (PC1 XOR, PC2 "
                     "edge-triggered) and lock detector, TTL-level inputs"),
      function_category="pll", output_type="push-pull; PC2OUT 3-state",
      max_frequency=PLL_FMAX,
      propagation_delay="SIGIN/COMPIN->PC1OUT 45 ns max (VCC 4.5V, CL 50pF)",
      supply_current="ICC 8 µA max quiescent (VCC 5.5V)",
      kw="PLL,phase-locked loop,VCO,phase comparator,lock detector,7046"),
]

FAMILY_NAME = {"4000B": "4000B CMOS", "74HC": "74HC", "74HCT": "74HCT",
               "9300": "TTL"}


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def rows():
    out = []
    for dev in DEVICES:
        fam = dev["fam"]
        for mpn, kind, status in dev["codes"]:
            pkg, fp = PACKAGE[kind]
            uid_prefix = dev.get("uid", "TI")
            r = {
                **COMMON, **fam,
                **{k: v for k, v in dev.items() if k in COLS},
                "unique_id": f"{uid_prefix}-{mpn}", "mpn": mpn, "value": dev["value"],
                "base_number": dev["base"], "package": pkg, "pin_count": "16",
                "part_locator": f"IC_LOGIC {dev['value']} {pkg}",
                "description": (f"{dev['gate_function']}, "
                                f"{FAMILY_NAME[fam['logic_family']]}, {pkg}"),
                "datasheet": f"{DS}/{dev['ds']}",
                "manufacturer_link": dev["link"],
                "kicad_symbol": f"{SYM}:{dev['sym']}",
                "kicad_footprint": fp,
                "lifecycle_status": status,
                "rohs": "Yes" if status == "Active" else "No",
                "allow_substitution": dev["subst"],
                "keywords": ",".join(dict.fromkeys(
                    [dev["value"], mpn] + dev["kw"].split(","))),
            }
            out.append(r)
            if dev["ieee"]:
                out.append({**r, "variant": "IEEE", "unique_id": r["unique_id"] + "-IEEE",
                            "kicad_symbol": dev["ieee"]})
    return out


def check(rs):
    for dev in DEVICES:
        p = ROOT / "datasheets" / dev["ds"]
        if not p.exists():
            raise SystemExit(f"missing data sheet {p}")
    ids = [r["unique_id"] for r in rs]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise SystemExit(f"duplicate unique_id: {sorted(dup)}")
    # every terra symbol referenced must exist in the per-table library
    lib = (ROOT / "kicad_symbols" / f"{SYM}.kicad_sym").read_text()
    for r in rs:
        lib_name, _, name = r["kicad_symbol"].partition(":")
        if lib_name == SYM and f'\n\t(symbol "{name}"\n' not in lib:
            raise SystemExit(f"{r['unique_id']}: symbol {r['kicad_symbol']} not in {SYM}")


def main():
    rs = rows()
    check(rs)
    lines = [
        "-- Terra EDA Library - 7-segment display decoders and HC/HCT PLLs",
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
