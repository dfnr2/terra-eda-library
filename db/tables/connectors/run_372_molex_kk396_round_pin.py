#!/usr/bin/env python3
"""Molex KK 396 round-pin headers: vertical, 0.045" (1.14 mm) round pins, 3.96 mm (0.156").

The Molex round-post alternative to the TE MTA-156 640384 headers (run_390) on the male
side of the OSI 48-line and SWTPC SS-50/SS-30 buses; the KK 156 41815 PCB receptacles
(run_395) are drawn for 0.045" square or round pins.

  - series 3190, with polarizing wall: 26-19-2NN1 (engineering 3190-NNA), sales drawing
    SDAE-3190-NXX rev AD2 (datasheets/molex/kk-396-3190-round-pin-header-sd.pdf). Mating
    pin 11.43 mm above the housing, wall 9.12 mm high; over 5 circuits the wall is
    slotted.
  - series 3192, flat wafer, end-stackable: 26-20-2NNS (engineering 3192NNx), sales drawing
    SDAE-3192-NX rev L2 (datasheets/molex/kk-396-3192-round-pin-header-sd.pdf). Suffix S
    is the mating-pin length: 1 = 11.43 mm (NA), 2 = 16.18 mm (NB), 6 = 32.51 mm (NF).
    The drawing's 26-21 (NK, 17.47 mm) column is not listed at Mouser and not generated.
Both: nylon housing UL94V-2, natural; brass pins, matte tin over nickel; housing 6.9 mm
deep with the pins on its centreline, body n x 3.96 mm long (pins 1.98 mm from each end);
3.17 mm solder tail; recommended hole 1.52 mm (+0.05/-0.08) for a 1.6 mm board. The
voided-circuit 38-00-xxxx builds on sheet 2 of the 3190 drawing are not generated.

Ratings: 600 V from product specification PS-99020-0087 sec. 4.1 (cited by both drawings;
datasheets/molex/kk-396-round-pin-product-spec-ps-99020-0087.pdf), -40 to +80 C with
brass (sec. 4.3); 7.0 A per contact from Molex's part pages (the spec rates only the
crimp and PCB receptacles; the pages also give 250 V, the CSA figure).

Lifecycle (2026-11-22): every code below is Active on its Molex part page and listed at
Mouser (26-20-2072 under Mouser's typo "2620-2072"). Digi-Key shows 26-19-2121 Active
with a 16-week lead time; Mouser marks the 3190 codes (except 26-19-2041) "discontinued
with no replacement", i.e. Mouser is dropping stock, not an end of production.

Symbol Connector_Generic:Conn_01xNN, plus a per-pin symbol row (`-pins`, _connkit.py).
KiCad ships no KK 396 round-pin footprints, so this script writes them to
terra_footprints_connectors: one per series and size, and a separate one (suffix
`_Pin16.18mm` / `_Pin32.51mm`) for the long-pin 3192 builds, whose land pattern is the
same but whose 3D model is not. Generated 3D models: housing 4.45 mm high (drawing DIM C
- DIM D - 3.17 mm tail), 3190 wall 9.12 mm above the board. Plan: plans/connectors-0156-bus.md. Generated
output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _conn156 import FP_LIB, PITCH, check_datasheets, footprint, line, write, write_footprint  # noqa: E402
from _connkit import numeric_pins_id, numeric_pins_symbol, pin_row, with_pins, write_symbols  # noqa: E402

OUTPUT_FILE = HERE / "connectors_generated_372_molex_kk396_round_pin.sql"
CREATED_BY = Path(__file__).name

DS = "${TERRA_EDA_LIB}/datasheets/molex"
SPEC = f"{DS}/kk-396-round-pin-product-spec-ps-99020-0087.pdf"
PIN_LENGTH = {"1": 11.43, "2": 16.18, "6": 32.51}      # mating pin above housing, mm

# (series, circuits, suffix): only the codes Active at Molex and listed at Mouser.
PARTS = (
    [("3190", n, "1") for n in (3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18)]
    + [("3192", n, "1") for n in (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18)]
    + [("3192", n, "2") for n in (3, 4, 5, 7, 9, 10, 12, 17)]
    + [("3192", 9, "6")]
)

SERIES = {
    "3190": dict(prefix="26-19-2", datasheet=f"{DS}/kk-396-3190-round-pin-header-sd.pdf",
                 polarized="yes", keying="polarizing back wall (slotted over 5 circuits)",
                 word="with polarizing wall"),
    "3192": dict(prefix="26-20-2", datasheet=f"{DS}/kk-396-3192-round-pin-header-sd.pdf",
                 polarized="no", keying="none (flat wafer, end-stackable; pull a pin to key)",
                 word="flat wafer"),
}

FAMILY = {
    "connector_category": "wire-to-board", "connector_family": "Molex KK 396",
    "connector_type": "header", "rows": 1, "pitch_mm": PITCH, "orientation": "vertical",
    "termination_type": "Through Hole", "gender": "male", "locking_mechanism": "none",
    "shielding": "unshielded", "color": "natural",
    "current_rating": 7.0, "voltage_rating": 600.0, "signal_type": "mixed",
    "flammability_rating": "UL94-V2",
    "temp_operating_min": -40.0, "temp_operating_max": 80.0,
    "mating_family": ("0.156in (3.96mm) receptacles for 0.045in round pins: Molex KK 396 "
                      "crimp housings 3069 (Molex part pages), KK 156 PCB receptacles 41815, "
                      "TE MTA-156 connector assemblies"),
    "mates_with": "Molex 3069 crimp housing or 41815 PCB receptacle, same circuit count",
}

BODY_HALF_DEPTH = 6.9 / 2       # housing 6.9 mm deep, pins on its centreline
END = 1.98                      # housing end to the first/last pin centre
WALL = 1.6                      # 3190 back wall thickness, scaled from the side view
WALL_H = 9.12                   # 3190 wall height above the board
HOUSING_H = 19.05 - 11.43 - 3.17  # drawing DIM C - DIM D - tail = 4.45 mm
TAIL = 3.17
PIN_D = 1.14


def mpn_for(series, n, suffix):
    return f"{SERIES[series]['prefix']}{n:02d}{suffix}"          # 26-19-2121


def catalog(mpn):
    return "00" + mpn.replace("-", "")                            # 0026192121


def fp_name(series, n, suffix="1"):
    base = f"Molex_KK-396_{series}_1x{n:02d}_P3.96mm_Vertical"
    return base if suffix == "1" else f"{base}_Pin{PIN_LENGTH[suffix]:g}mm"


def footprint_text(series, n, suffix):
    x1 = (n - 1) * PITCH + END
    body = (-END, -BODY_HALF_DEPTH, x1, BODY_HALF_DEPTH)
    court = (-END - 0.5, -BODY_HALF_DEPTH - 0.5, x1 + 0.5, BODY_HALF_DEPTH + 0.5)
    extra = ""
    if series == "3190":   # polarizing back wall on the -y side, as KiCad draws KK 396 41791
        extra = line(-END, -BODY_HALF_DEPTH + WALL, x1, -BODY_HALF_DEPTH + WALL, "F.Fab", 0.1)
    kind = "with polarizing wall" if series == "3190" else "flat wafer"
    return footprint(
        fp_name(series, n, suffix),
        f"Molex KK 396 header series {series}, vertical, 0.045in round pin, {kind}, "
        f"{PIN_LENGTH[suffix]:g}mm mating pin, "
        f"1x{n:02d}, 3.96mm pitch (Molex drawing SDAE-{series})",
        f"connector Molex KK-396 {series} round pin header 3.96mm 0.156in",
        n, pad_size=2.4, drill=1.52, body=body, courtyard=court, extra=extra)


def model_specs():
    specs = {}
    for series, n, suffix in PARTS:
        x1 = (n - 1) * PITCH + END
        spec = [("box", "natural", -END, -BODY_HALF_DEPTH, 0, x1, BODY_HALF_DEPTH, HOUSING_H)]
        if series == "3190":
            spec.append(("box", "natural", -END, -BODY_HALF_DEPTH, 0,
                         x1, -BODY_HALF_DEPTH + WALL, WALL_H))
        spec += pin_row("tin", n, PITCH, 0, -TAIL, HOUSING_H + PIN_LENGTH[suffix], PIN_D,
                        round_=True)
        specs[fp_name(series, n, suffix)] = spec
    return specs


def parts():
    for series, n, suffix in PARTS:
        s = SERIES[series]
        mpn = mpn_for(series, n, suffix)
        pin = PIN_LENGTH[suffix]
        yield {
            **FAMILY,
            "unique_id": f"Molex-{mpn}",
            "part_locator": (f"conn-header-{n}pos-3.96mm-1row-th-vertical-round-post-"
                             f"{pin:g}mm-tin" + ("-wall" if series == "3190" else "")),
            "mpn": mpn, "manufacturer": "Molex", "value": mpn,
            "description": (
                f"Molex KK 396 header {mpn}, 3.96mm pitch, 1x{n:02d}, vertical, {s['word']}, "
                f"0.045in round pin, {pin:g}mm mating pin, 3.17mm tail, tin plating, "
                "through-hole"),
            "datasheet": s["datasheet"],
            "manufacturer_link": f"https://www.molex.com/en-us/products/part-detail/{catalog(mpn)}",
            "kicad_symbol": f"Connector_Generic:Conn_01x{n:02d}",
            "kicad_footprint": f"{FP_LIB}:{fp_name(series, n, suffix)}",
            "lifecycle_status": "Active", "rohs": "Yes",
            "allow_substitution": "No", "tracking": "No",
            "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
            "keywords": (
                f"connector,header,molex,kk,kk396,kk-396,{series},{mpn},{catalog(mpn)},"
                f"3.96mm,0.156in,round pin,round post,vertical,{n}-pin,bus,SWTPC,SS-50,"
                "SS-30,OSI,vintage"),
            "pin_count": str(n), "positions": n,
            "connector_series": series,
            "polarized": s["polarized"], "keying_detail": s["keying"],
        }


def main():
    check_datasheets([SPEC] + [s["datasheet"] for s in SERIES.values()])
    for series, n, suffix in PARTS:
        write_footprint(fp_name(series, n, suffix), footprint_text(series, n, suffix))
    write_symbols([numeric_pins_symbol(n) for n in sorted({p[1] for p in PARTS})])
    rows = with_pins(list(parts()), lambda r: numeric_pins_id(r["positions"]))
    write(OUTPUT_FILE, "Molex KK 396 round-pin headers 3190/3192", CREATED_BY, rows)


if __name__ == "__main__":
    main()
