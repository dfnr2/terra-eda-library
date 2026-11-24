#!/usr/bin/env python3
"""onsemi 1N4728A-1N4758A 1 W Zener diodes, DO-41 (axial lead, case 017AH), 5%.

Data sheet: datasheets/onsemi/1n4736at-d.pdf (1N4736AT/D Rev. 10, August 2021,
fetched from onsemi.com through Chrome). It lists 28 of the 37 JEDEC types: no
1N4729A, 1N4730A or 1N4731A (3.6-4.3 V), and nothing above 1N4758A (56 V). Its
figures match Central's sheet on every value, so both makers share the table in
_zener_1n4728a.py; Central's rows (run_331) cover the whole series.

Ordering codes, from the sheet's ordering table: "<type>" (3000 bulk bag),
"<type>TR" (tape and reel), "<type>-T50A" (fan-fold ammo) and, for some types,
"<type>-T50R". The bulk code is used. On 2026-11-24 Mouser stocked 27 of the 28
bulk codes (275 to 68,862 pieces); the 1N4744A was listed with none in stock but not
obsolete. Mouser shows onsemi's 1N4729A and 1N4759A-1N4764A as Obsolete, which is
why the sheet stops where it does.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _zener_1n4728a import rows, write  # noqa: E402

OUTPUT_FILE = HERE / "diodes_zener_generated_332_onsemi_1n4728a.sql"
CREATED_BY = Path(__file__).name
DATASHEET = "${TERRA_EDA_LIB}/datasheets/onsemi/1n4736at-d.pdf"

TYPES = ["1N4728A"] + [f"1N{n}A" for n in range(4732, 4759)]


def main():
    recs = list(rows(
        manufacturer="onsemi", short="onsemi", types=TYPES, mpn=lambda t: t,
        packing_text=lambda t: "bulk bag", datasheet=DATASHEET,
        link=None, created_by=CREATED_BY))
    write(OUTPUT_FILE, "onsemi 1N4728A-1N4758A Zener diodes, DO-41, 1W", CREATED_BY,
          HERE.parents[2], DATASHEET, recs)


if __name__ == "__main__":
    main()
