#!/usr/bin/env python3
"""Through-hole small-signal MOSFETs in TO-92: onsemi 2N7000 and BS170, Diodes BS250P.

Specs are transcribed from the datasheets parked in the local store:
  - 2N7000:  datasheets/onsemi/nds7002a-d.pdf (2N7000/2N7002/NDS7002A, Rev. 11, Mar 2025)
  - BS170:   datasheets/onsemi/mmbf170-d.pdf (BS170/MMBF170, Rev. 9, Feb 2026)
  - BS250P:  datasheets/diodes-inc/bs250p.pdf (DS33014 Rev. 3-2, Oct 2019)

mpn is the straight-lead bulk orderable: onsemi's product pages list 2N7000 and BS170
(Fairchild lineage) as Active, while the Motorola-lineage 2N7000G / BS170G and their
RLRA reels are Obsolete; the -D26Z/-D27Z/-D74Z/-D75Z formed-lead reel and ammo codes
are packaging options and are not recorded.

Pinouts (pins 1-2-3) and symbols, each checked by _th_fets.check():
  - 2N7000: 1 = S, 2 = G, 3 = D  -> Transistor_FET:2N7000 (S-G-D)
  - BS170:  "Pin Array DGS"      -> Transistor_FET:BS170 (extends BS107, D-G-S)
  - BS250P: E-Line drawing labels the leads D, G, S in order (no pin numbers);
            taken as 1 = D, 2 = G, 3 = S -> Transistor_FET:BS250 (D-G-S)
All use Package_TO_SOT_THT:TO-92_Inline (1.27 mm straight leads). The BS250P E-Line
body is "TO92 compatible" per its datasheet, which gives no outline, so that footprint
is the nearest stock match rather than a dimensioned one.

VN10LF is not included: the only current datasheet (Diodes/Zetex VN10LF, 1996) is a
SOT-23 part, not TO-92.

Lifecycle: onsemi product-page schema data (2026-11-25) for 2N7000 and BS170; BS250P
from Octopart ("in production") and a distributor listing (Active) because Digi-Key,
Mouser and diodes.com refused scripted fetches. Recheck BS250P against a distributor.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

from _th_fets import write

HERE = Path(__file__).resolve().parent
OUTPUT_FILE = HERE / "mosfet_generated_330_th_small_signal.sql"
CREATED_BY = Path(__file__).name
DS = "${TERRA_EDA_LIB}/datasheets"

COMMON = {
    "package": "TO-92", "kicad_footprint": "Package_TO_SOT_THT:TO-92_Inline",
    "lifecycle_status": "Active", "allow_substitution": "No", "tracking": "No",
    "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
    "pin_count": "3", "channels": 1,
    "temp_operating_min": -55, "temp_operating_max": 150,
    "temp_storage_min": -55, "temp_storage_max": 150, "temp_junction_max": "150C",
}

PARTS = [
    {
        **COMMON,
        "manufacturer": "onsemi", "unique_id": "onsemi-2N7000", "mpn": "2N7000",
        "value": "2N7000", "pinout": "SGD",
        "part_locator": "mosfet-nch-60v-0.2a-to92",
        "description": ("onsemi 2N7000 N-channel enhancement MOSFET, 60V 200mA, "
                        "RDS(on) 5 ohm max @ 10V (5.3 ohm @ 4.5V), logic-level, TO-92"),
        "datasheet": f"{DS}/onsemi/nds7002a-d.pdf",
        "manufacturer_link": "https://www.onsemi.com/products/discrete-power-modules/"
                             "mosfets/small-signal-mosfets/2n7000",
        "kicad_symbol": "Transistor_FET:2N7000",
        "keywords": "mosfet,transistor,n-channel,nmos,small-signal,logic-level,switch,"
                    "through-hole,to-92,60V,2N7000",
        "transistor_type": "nmos", "v_ce_ds_max": "60V", "i_c_d_max": "200mA",
        "power_dissipation": "400mW (Tc=25C)",
        "rds_on": "5ohm max @ Vgs=10V, Id=500mA (5.3ohm max @ Vgs=4.5V, Id=75mA)",
        "vgs_th": "0.8V min / 3.0V max",
        "temp_soldering": 300.0,
    },
    {
        **COMMON,
        "manufacturer": "onsemi", "unique_id": "onsemi-BS170", "mpn": "BS170",
        "value": "BS170", "pinout": "DGS",
        "part_locator": "mosfet-nch-60v-0.5a-to92",
        "description": ("onsemi BS170 N-channel enhancement MOSFET, 60V 500mA, "
                        "RDS(on) 5 ohm max @ 10V, TO-92"),
        "datasheet": f"{DS}/onsemi/mmbf170-d.pdf",
        "manufacturer_link": "https://www.onsemi.com/products/discrete-power-modules/"
                             "mosfets/small-signal-mosfets/bs170",
        "kicad_symbol": "Transistor_FET:BS170",
        "keywords": "mosfet,transistor,n-channel,nmos,small-signal,switch,"
                    "through-hole,to-92,60V,BS170",
        "transistor_type": "nmos", "v_ce_ds_max": "60V", "i_c_d_max": "500mA",
        "power_dissipation": "830mW (Ta=25C)",
        "rds_on": "5ohm max @ Vgs=10V, Id=200mA",
        "vgs_th": "0.8V min / 3.0V max",
        "temp_soldering": 300.0,
    },
    {
        **COMMON,
        "manufacturer": "Diodes, Inc.", "unique_id": "Diodes, Inc.-BS250P", "mpn": "BS250P",
        "value": "BS250P", "pinout": "DGS", "package": "E-Line (TO-92 compatible)",
        "part_locator": "mosfet-pch-45v-0.23a-to92",
        "description": ("Diodes Inc. BS250P P-channel enhancement vertical DMOS FET, "
                        "-45V -230mA, RDS(on) 14 ohm max @ -10V, E-Line (TO-92 compatible)"),
        "datasheet": f"{DS}/diodes-inc/bs250p.pdf",
        "manufacturer_link": "https://www.diodes.com/part/view/BS250P",
        "kicad_symbol": "Transistor_FET:BS250",
        "keywords": "mosfet,transistor,p-channel,pmos,small-signal,high-side,switch,"
                    "through-hole,to-92,e-line,45V,BS250P,BS250",
        "transistor_type": "pmos", "v_ce_ds_max": "45V", "i_c_d_max": "230mA",
        "power_dissipation": "700mW (Ta=25C)",
        "rds_on": "14ohm max @ Vgs=-10V, Id=-200mA",
        "vgs_th": "-1.0V min / -3.5V max",
        "temp_soldering": None,
    },
]


def main():
    write(OUTPUT_FILE, CREATED_BY, PARTS, "through-hole small-signal TO-92 MOSFETs")


if __name__ == "__main__":
    main()
