#!/usr/bin/env python3
"""Harvest curated connector parts from the abc4-spiro mainboard into native terra.

Specific curated parts (not a parametric sweep). All six carry custom footprints
that were migrated into the terra-connectors footprint lib; symbols use standard
KiCad Connector_Generic / Connector_Audio symbols.

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("connectors_generated_300_spiro_harvest.sql")
CREATED_BY = Path(__file__).name

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol",
    "kicad_footprint", "rohs", "allow_substitution", "tracking",
    "source", "dump_priority", "tier", "keywords", "pin_count",
    "connector_category", "connector_family", "connector_series", "connector_type",
    "positions", "rows", "pitch_mm", "orientation", "termination_type", "gender",
    "signal_type", "mates_with",
]

PARTS = [
    {
        "mpn": "15912240", "manufacturer": "Molex", "value": "X10 Primary Extension",
        "description": "Molex 15912240 2x12 0.1in (2.54mm) pin header, SMT, vertical",
        "datasheet": "https://www.molex.com/en-us/products/part-detail/15912240?display=pdf",
        "kicad_symbol": "Connector_Generic:Conn_02x12_Odd_Even",
        "kicad_footprint": "terra-connectors:Molex_15912240_2x12_header_SMD",
        "connector_category": "board-to-board", "connector_family": "Molex 0.1in Header",
        "connector_series": "15912240", "connector_type": "header",
        "positions": 24, "rows": 2, "pitch_mm": 2.54, "orientation": "vertical",
        "termination_type": "SMT", "gender": "male", "signal_type": "mixed",
        "mates_with": None, "pin_count": "24", "keywords": "connector,header",
    },
    {
        "mpn": "15912040", "manufacturer": "Molex", "value": "2x2",
        "description": "Molex 15912040 2x2 0.1in (2.54mm) pin header, SMT, vertical",
        "datasheet": "https://www.molex.com/en-us/products/part-detail/15912040?display=pdf",
        "kicad_symbol": "Connector_Generic:Conn_02x02_Odd_Even",
        "kicad_footprint": "terra-connectors:Molex_15912040_2x2_header_SMD",
        "connector_category": "board-to-board", "connector_family": "Molex 0.1in Header",
        "connector_series": "15912040", "connector_type": "header",
        "positions": 4, "rows": 2, "pitch_mm": 2.54, "orientation": "vertical",
        "termination_type": "SMT", "gender": "male", "signal_type": "mixed",
        "mates_with": None, "pin_count": "4", "keywords": "connector,header",
    },
    {
        "mpn": "DF3A-8P-2DSA", "manufacturer": "Hirose", "value": "1x8 pin connector",
        "description": "Hirose DF3A-8P-2DSA 1x8 2.0mm pin header, through-hole",
        "datasheet": "https://www.hirose.com/en/product/document?clcode=CL0543-0171-2-00&productname=DF3A-8P-2DSA&series=DF3&documenttype=Catalog&lang=en&documentid=en_DF3_CAT",
        "kicad_symbol": "Connector_Generic:Conn_01x08",
        "kicad_footprint": "terra-connectors:CON8_1X8_R_DF3_HIR",
        "connector_category": "wire-to-board", "connector_family": "Hirose DF3",
        "connector_series": "DF3", "connector_type": "header",
        "positions": 8, "rows": 1, "pitch_mm": 2.0, "orientation": "vertical",
        "termination_type": "Through Hole", "gender": "male", "signal_type": "signal",
        "mates_with": None, "pin_count": "8", "keywords": "connector,header",
    },
    {
        "mpn": "STX-3500-3NTR", "manufacturer": "Kycon", "value": "CONN 3.5mm stereo jack SMD",
        "description": "Kycon STX-3500-3NTR 3.5mm stereo (TRS) audio jack, SMT right-angle",
        "datasheet": "https://www.kycon.com/Pub_Eng_Draw/STX-3500-5N.pdf",
        "kicad_symbol": "Connector_Audio:AudioJack3",
        "kicad_footprint": "terra-connectors:STX35003NTR",
        "connector_category": "io", "connector_family": "Kycon 3.5mm Audio Jack",
        "connector_series": "STX-3500", "connector_type": "jack",
        "positions": 3, "rows": 1, "pitch_mm": None, "orientation": "right-angle",
        "termination_type": "SMT", "gender": "jack", "signal_type": "signal",
        "mates_with": None, "pin_count": "3", "keywords": "connector,audio,jack",
    },
    {
        "mpn": "14-37FSV30-BD-16", "manufacturer": "Leader Tech", "value": "Chassis Ground",
        "description": "Leader Tech 14-37FSV30-BD-16 board-mount fingerstock EMI gasket (chassis ground), SMT right-angle",
        "datasheet": "https://leadertechinc.com/wp-content/uploads/2017/01/EMI-Enclosure-Catalog-9-2016.pdf",
        "kicad_symbol": "Connector_Generic:Conn_01x01",
        "kicad_footprint": "terra-connectors:14-37FSV30_3_segments",
        "connector_category": "grounding", "connector_family": "Leader Tech Fingerstock",
        "connector_series": "14-37FSV30", "connector_type": "gasket",
        "positions": 1, "rows": 1, "pitch_mm": None, "orientation": "right-angle",
        "termination_type": "SMT", "gender": None, "signal_type": "shield",
        "mates_with": None, "pin_count": "1", "keywords": "connector,emi,grounding",
    },
    {
        "mpn": "RRC-MC20-90-10", "manufacturer": "RRC Power Solutions", "value": "1x5 battery connector",
        "description": "RRC-MC20-90-10 5-position battery connector, through-hole right-angle (mates RRC2054)",
        "datasheet": "https://www.rrc-ps.com/fileadmin/Dokumente/Data-Sheets/DS_RRC-MC20-90-10.pdf",
        "kicad_symbol": "Connector_Generic:Conn_01x05",
        "kicad_footprint": "terra-connectors:RRCMC209010",
        "connector_category": "wire-to-board", "connector_family": "RRC Battery Connector",
        "connector_series": "MC20", "connector_type": "receptacle",
        "positions": 5, "rows": 1, "pitch_mm": None, "orientation": "right-angle",
        "termination_type": "Through Hole", "gender": "female", "signal_type": "power",
        "mates_with": "RRC2054", "pin_count": "5", "keywords": "connector,battery,power",
    },
]


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


MFR_LINK = {
    "Molex": "https://www.molex.com",
    "Hirose": "https://www.hirose.com",
    "Kycon": "https://www.kycon.com",
    "Leader Tech": "https://leadertechinc.com",
    "RRC Power Solutions": "https://www.rrc-ps.com",
}


def row(p):
    rec = {
        "unique_id": f"{p['manufacturer'].replace(' ', '_')}-{p['mpn']}",
        "part_locator": f"conn-{p['connector_type']}-{p['positions']}pos-{p['connector_series'].lower()}",
        "package": None, "manufacturer_link": MFR_LINK.get(p["manufacturer"]),
        "rohs": "Yes", "allow_substitution": "No", "tracking": "No",
        "source": None, "dump_priority": 0, "tier": 2,
    }
    rec.update(p)
    vals = ", ".join(sql(rec.get(c)) for c in COLS)
    return f"INSERT INTO connectors ({', '.join(COLS)}) VALUES ({vals});"


def main():
    lines = [
        "-- Terra EDA Library - connectors harvest from abc4-spiro mainboard",
        f"-- Curated connector parts ported as native terra rows. Generated by {CREATED_BY}.",
        "-- dump_priority=0, source=NULL: regenerated, not dumped to static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    lines += [row(p) for p in PARTS]
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(PARTS)} parts")


if __name__ == "__main__":
    main()
