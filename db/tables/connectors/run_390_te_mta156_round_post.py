#!/usr/bin/env python3
"""TE Connectivity MTA-156 640384: plain straight header, 0.045" round post, 3.96 mm (0.156").

The motherboard/backplane side of the SWTPC SS-50/SS-30 buses (TE 1-640384-0, 10
positions, per the Corsham SS-50 specification) and, in 12 positions, a round-post
replacement for the OSI 48-line bus header (Molex 26-60-2120 in osiweb's replacement
list, a square-post KK 396 41771). Round posts are preferred over square for these
buses; the Molex KK 156 41815 receptacles (run_395) are drawn for 0.045" square or
round pins.

Customer drawing ENG_CD_640384 rev AB (datasheets/te/ENG_CD_640384_AB.pdf):
  - 2-24 positions; part number `<tens>-640384-<units>`, the tens prefix omitted below
    10 (640384-2 = 2, 1-640384-0 = 10, 1-640384-5 = 15). The drawing marks 22-24
    obsolete; TE's product pages (2026-11-21) also mark 16-21 OBSOLETE, so only
    2-15 are generated.
  - 0.045" (1.14 mm) round copper-alloy post, tin plated; glass-filled thermoplastic
    polyester housing, UL94V-0, natural; housing 0.250" x 0.125", length n x 0.156";
    post 0.400" above the housing, 0.125" solder tail; no lock or polarizing wall.
  - recommended hole 0.060" +0.010/-0.000 for a 0.062" board. Footprint drill
    1.60 mm (inside that band), 2.40 mm pads.
Ratings from MTA-156 system product specification 108-1051 rev J sec. 3.3
(datasheets/te/te-108-1051-mta156-product-spec.pdf): 600 V AC, -55 to +105 C (posts
brass, tin; headers UL94V-0). Current is left blank: the spec gives only a
single-circuit base curve for the whole MTA-156 IDC system (14.24 A for a 30 C rise at
18 AWG, falling to zero at 105 C) with wire-size and loading derating factors, no
per-contact figure for the header alone.

Lifecycle: 2-15 are ACTIVE on TE's product pages and listed at Mouser (7, 10, 11, 13
and 15 non-stocked) on 2026-11-21. Symbol Connector_Generic:Conn_01xNN. KiCad ships no
MTA-156 footprints, so this script writes them to terra_footprints_connectors.
Plan: plans/connectors-0156-bus.md. Generated output (dump_priority=0, source=NULL) is
not dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _conn156 import FP_LIB, PITCH, check_datasheets, footprint, write, write_footprint  # noqa: E402

OUTPUT_FILE = HERE / "connectors_generated_390_te_mta156_round_post.sql"
CREATED_BY = Path(__file__).name

POSITIONS = range(2, 16)
DATASHEET = "${TERRA_EDA_LIB}/datasheets/te/ENG_CD_640384_AB.pdf"
SPEC = "${TERRA_EDA_LIB}/datasheets/te/te-108-1051-mta156-product-spec.pdf"
BODY_HALF_DEPTH = 0.250 * 25.4 / 2     # housing 0.250" deep, posts on its centreline
END = 0.078 * 25.4                     # housing end to first post centre

FAMILY = {
    "connector_category": "wire-to-board", "connector_family": "TE MTA-156",
    "connector_series": "640384", "connector_type": "header",
    "rows": 1, "pitch_mm": PITCH, "orientation": "vertical",
    "termination_type": "Through Hole", "gender": "male",
    "polarized": "no", "keying_detail": "none (plain header; pull a post to key)",
    "locking_mechanism": "none", "shielding": "unshielded", "color": "natural",
    "signal_type": "mixed", "flammability_rating": "UL94-V0",
    "voltage_rating": 600.0, "temp_operating_min": -55.0, "temp_operating_max": 105.0,
    "mating_family": ("0.156in (3.96mm) receptacles for 0.045in round or square pins: "
                      "Molex KK 156 PCB receptacles 41815, TE MTA-156 IDC and SL-156 "
                      "connector assemblies"),
    "mates_with": "Molex 41815 PCB receptacle or TE MTA-156 receptacle, same position count",
}


def mpn_for(n):
    tens, units = divmod(n, 10)
    return f"{tens}-640384-{units}" if tens else f"640384-{units}"


def fp_name(n):
    return f"TE_MTA-156_{mpn_for(n)}_1x{n:02d}_P3.96mm_Vertical"


def footprint_text(n):
    x1 = (n - 1) * PITCH + END
    body = (-END, -BODY_HALF_DEPTH, x1, BODY_HALF_DEPTH)
    court = (-END - 0.5, -BODY_HALF_DEPTH - 0.5, x1 + 0.5, BODY_HALF_DEPTH + 0.5)
    return footprint(
        fp_name(n),
        f"TE MTA-156 header {mpn_for(n)}, plain, straight, 0.045in round post, "
        f"1x{n:02d}, 3.96mm pitch (TE customer drawing 640384)",
        "connector TE MTA-156 640384 round post header 3.96mm 0.156in",
        n, pad_size=2.4, drill=1.6, body=body, courtyard=court)


def parts():
    for n in POSITIONS:
        mpn = mpn_for(n)
        yield {
            **FAMILY,
            "unique_id": f"TE-{mpn}",
            "part_locator": f"conn-header-{n}pos-3.96mm-1row-th-vertical-round-post-tin",
            "mpn": mpn, "manufacturer": "TE Connectivity", "value": mpn,
            "description": (
                f"TE Connectivity MTA-156 header {mpn}, 3.96mm pitch, 1x{n:02d}, vertical, "
                "plain (no lock), 0.045in round post, 10.16mm post above housing, "
                "3.18mm tail, tin plating, through-hole"),
            "datasheet": DATASHEET,
            "manufacturer_link": f"https://www.te.com/en/product-{mpn}.html",
            "kicad_symbol": f"Connector_Generic:Conn_01x{n:02d}",
            "kicad_footprint": f"{FP_LIB}:{fp_name(n)}",
            "lifecycle_status": "Active", "rohs": "Yes",
            "allow_substitution": "No", "tracking": "No",
            "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
            "keywords": (
                f"connector,header,te,amp,mta-156,mta156,640384,{mpn},3.96mm,0.156in,"
                f"round post,round pin,vertical,{n}-pin,bus,SWTPC,SS-50,SS-30,OSI,vintage"),
            "pin_count": str(n), "positions": n,
        }


def main():
    check_datasheets([DATASHEET, SPEC])
    for n in POSITIONS:
        write_footprint(fp_name(n), footprint_text(n))
    write(OUTPUT_FILE, "TE MTA-156 640384 round-post headers", CREATED_BY, list(parts()))


if __name__ == "__main__":
    main()
