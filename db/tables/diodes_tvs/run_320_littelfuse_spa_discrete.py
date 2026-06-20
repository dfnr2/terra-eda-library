#!/usr/bin/env python3
"""Littelfuse SPA(R) single-channel ESD-protection TVS diodes (discretes).

The 1-channel members of the catalog's "General Purpose ESD Protection (TVS
Discretes and Arrays)" class. Headline specs (working/clamp voltage, capacitance,
ESD contact-discharge rating, surge current) are from the catalog's page-2
selector table; orderable MPNs, packages, and directionality are verified from
each series' datasheet section. ESD parts are rated by ESD kV + surge current,
not Vbr/Ppp, so those columns stay NULL.

Unidirectional parts use terra-diodes:D_TVS_unidir; bidirectional use Device:D_TVS.

NOT INCLUDED (no KiCad footprint): SP1003-01DTG (SOD-723) and the entire SP1006
series (uDFN-2). The multi-channel arrays in this class (SP05, SP1001, SP1002,
SP1004, SP1011) are handled separately once array symbols exist.
"""
from pathlib import Path
from _tvs import insert, write

DATASHEET = "${TERRA_EDA_LIB}/datasheets/littelfuse/spa-diode-arrays-catalog.pdf"
LINK = "https://www.littelfuse.com/products/tvs-diode-arrays.aspx"
SYM = {"unidirectional": "terra-diodes:D_TVS_unidir", "bidirectional": "Device:D_TVS"}
FP = {
    "SOD-882": "Diode_SMD:D_SOD-882",
    "SOD-323": "Diode_SMD:D_SOD-323",
    "0201": "Diode_SMD:D_0201_0603Metric",
}

# mpn, package, directionality, working V, clamp, cap, ESD kV, surge
PARTS = [
    ("SP1003-01ETG", "SOD-882", "unidirectional", "5.0V", "12.0V @ 7A", "30pF", "30kV", "7A"),
    ("SP1005-01ETG", "SOD-882", "bidirectional", "6.0V", "9.3V @ 1A", "30pF", "30kV", "10A"),
    ("SP1005-01WTG", "0201", "bidirectional", "6.0V", "9.3V @ 1A", "30pF", "30kV", "10A"),
    ("SP1007-01ETG", "SOD-882", "bidirectional", "6.0V", "11.2V @ 1A", "3.5pF", "8kV", "2A"),
    ("SP1007-01WTG", "0201", "bidirectional", "6.0V", "11.2V @ 1A", "3.5pF", "8kV", "2A"),
    ("SP1008-01WTG", "0201", "bidirectional", "6.0V", "10.7V @ 1A", "6pF", "15kV", "2.5A"),
    ("SD05-01FTG", "SOD-323", "unidirectional", "5.0V", "8.0V @ 1A", "350pF", "30kV", "30A"),
    ("SD05C-01FTG", "SOD-323", "bidirectional", "5.0V", "8.0V @ 1A", "200pF", "30kV", "30A"),
]


def rows():
    out = []
    for mpn, pkg, direction, vwm, vc, cap, esd, surge in PARTS:
        short = "uni" if direction == "unidirectional" else "bidi"
        w = vwm.lower().rstrip("v")
        pkg_slug = pkg.lower().replace("-", "")
        out.append(insert({
            "unique_id": f"Littelfuse-{mpn}",
            "part_locator": f"tvs-esd-{w}v-{short}-{pkg_slug}",
            "mpn": mpn, "manufacturer": "Littelfuse",
            "package": pkg, "value": f"{vwm} ESD {short}",
            "description": (
                f"Littelfuse {mpn} {vwm} {direction} ESD-protection TVS diode, "
                f"{esd} (IEC 61000-4-2), {pkg}"
            ),
            "datasheet": DATASHEET, "manufacturer_link": LINK,
            "kicad_symbol": SYM[direction], "kicad_footprint": FP[pkg],
            "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
            "source": None, "dump_priority": 0, "tier": 2,
            "keywords": f"tvs,esd,protection,{short},{w}v,{esd.lower()}",
            "pin_count": "2",
            "temp_operating_min": -55.0, "temp_operating_max": 125.0,
            "temp_storage_min": -55.0, "temp_storage_max": 150.0,
            "directionality": direction, "standoff_voltage": vwm,
            "clamping_voltage": vc, "capacitance": cap,
            "peak_pulse_current": surge, "esd_contact_kv": esd, "channels": 1,
        }))
    return out


if __name__ == "__main__":
    write(
        Path(__file__).with_name("diodes_tvs_generated_320_littelfuse_spa_discrete.sql"),
        Path(__file__).name, rows(),
        "Littelfuse SPA single-channel ESD-protection TVS discretes",
    )
