#!/usr/bin/env python3
"""Central Semiconductor 1N4728A-1N4764A 1 W Zener diodes, DO-41, 5% tolerance.

The common 1 W through-hole Zener series, the companion to the 500 mW 1N746A-1N759A
in run_330_central_1n746a.py. Central's sheet (datasheets/central/1n4728a-1n4764a.pdf,
R2, 14-October 2013) is the one current sheet with all 37 types, 3.3 to 100 V; onsemi
(run_332) makes 28 of them. Table and row builder in _zener_1n4728a.py.

  - PD 1.0 W at TA = 50 C; TJ and Tstg -65 to +200 C; VF 1.2 V max at 200 mA.
  - Per type: VZ min/nom/max at IZT (76 mA at 3.3 V down to 2.5 mA at 100 V), ZZT,
    ZZK at IZK, IR at VR, surge current and VZ temperature coefficient.

Ordering codes, as for the 1N746A series: "<type> TR PBFREE" (tape and reel, sold cut
to any quantity) or "<type> BK PBFREE" (bulk). On 2026-11-24 Mouser had the TR code
of 14 types in stock and no bulk code in stock, so every row uses TR (PACKING can
switch a type to BK). It listed the 1N4732A, 1N4735A-37A, 1N4741A, 1N4745A, 1N4749A,
1N4752A, 1N4753A and 1N4760A as non-stocked, the 1N4746A, 1N4754A, 1N4758A and
1N4759A with none in stock, and didn't carry the 1N4728A-31A, 1N4744A, 1N4756A or
1N4762A-64A. Central's part search lists every type with no discontinued flag, so
all rows are Active. For the 28 types onsemi makes, its rows
(run_332) are the stocked choice.

value is the JEDEC type, as in run_330 and diodes_th. Symbol Device:D_Zener (1 = K,
2 = A) on the DO-41 footprint, cathode on pad 1.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _zener_1n4728a import DATA, rows, write  # noqa: E402

OUTPUT_FILE = HERE / "diodes_zener_generated_331_central_1n4728a.sql"
CREATED_BY = Path(__file__).name
DATASHEET = "${TERRA_EDA_LIB}/datasheets/central/1n4728a-1n4764a.pdf"
PACKING_TEXT = {"TR": "tape and reel", "BK": "bulk"}

# Types to order in bulk (BK) instead of tape and reel; none as of 2026-11-24.
PACKING = {}


def main():
    recs = list(rows(
        manufacturer="Central Semiconductor", short="Central", types=DATA,
        mpn=lambda t: f"{t} {PACKING.get(t, 'TR')} PBFREE",
        packing_text=lambda t: PACKING_TEXT[PACKING.get(t, "TR")],
        datasheet=DATASHEET, created_by=CREATED_BY))
    write(OUTPUT_FILE, "Central Semiconductor 1N4728A-1N4764A Zener diodes, DO-41, 1W",
          CREATED_BY, HERE.parents[2], DATASHEET, recs)


if __name__ == "__main__":
    main()
