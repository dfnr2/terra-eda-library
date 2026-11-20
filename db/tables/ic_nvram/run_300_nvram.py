#!/usr/bin/env python3
"""Battery-backed nonvolatile SRAM modules: Dallas (Analog Devices) and ST ZEROPOWER.

These are byte-wide SRAMs with a lithium cell and power-fail switch built into the
package, made to drop into a JEDEC SRAM (and usually EPROM/EEPROM) socket. They are
the in-production way to give a vintage or retro board writable, nonvolatile memory.
See plans/vintage-computer-parts.md.

One row per ordering code the current datasheet lists, commercial temperature
(0 to 70 C), DIP module only. Each chip comes in two VCC grades, which the MPN
carries: Dallas AB = 5V +/-5%, AD/Y = 5V +/-10%; ST M48Z02/08/35/58 = 4.75 to 5.5V,
M48Z12/18/35Y/58Y = 4.5 to 5.5V. The grade sets the write-protect (VTP/VPFD) window.

Sources, filed in datasheets/:
  - analog-devices/: ADI (Maxim) datasheets 19-5580 DS1220AB/AD Rev 10/10,
    19-5625 DS1225AB/AD Rev 11/10, 19-5635 DS1230Y/AB Rev 11/10, 19-5638 DS1245Y/AB
    Rev 11/10 (with the 32-pin module drawing, p. 10 of the 2006 revision, appended
    as p. 11), 19-5647 DS1250Y/AB Rev 12/10.
  - st/: DocID02420 M48Z02/M48Z12 Rev 10, DocID02424 M48Z08/M48Z18 Rev 10,
    DocID02608 M48Z35/M48Z35Y Rev 12, DocID02559 M48Z58/M48Z58Y Rev 13.

Scope notes:
  - The 2010 Dallas revisions cut the ordering tables to one speed (-70; -100 for
    the DS1220). Digi-Key still lists -85 to -200 grades of some as Active, but only
    the datasheet's codes are generated.
  - Industrial (IND) grades, the Dallas 34-pin PowerCap modules and the ST SOH28
    SNAPHAT parts are left out: they're surface-mount and need footprints of their
    own. They're listed in the plan as follow-ups.
  - Lifecycle: every code here showed Active on Digi-Key on 2026-11-20 (lead-free
    "+" Dallas codes; the leaded ones are Obsolete). analog.com could not be read,
    so ADI rows carry no manufacturer_link.

Footprints: the modules are wider than a plain DIP (Dallas EDIP 720/740 mil body,
ST CAPHAT 18 mm) but sit on 600-mil rows (ST eA 0.600-0.630 in; Dallas H 0.590-
0.630 in), so the stock W15.24mm land patterns fit. The 24-pin parts use KiCad's
18 mm-body CAPHAT outline; the 28/32-pin silkscreens are narrower than the module.

Symbols: stock Memory_RAM where pin-for-pin (M48Zx2 for 2Kx8, HM62256BLP for 32Kx8,
AS6C4008-55PCN for 512Kx8); custom DS1225/DS1245 in terra_symbols_ic_nvram for the
8Kx8 and 128Kx8 modules, whose CE2 pin is NC (pin tables in _pinouts.py).

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_nvram_generated_300_nvram.sql")
CREATED_BY = Path(__file__).name
LIB = "terra_symbols_ic_nvram"
DS_ROOT = "${TERRA_EDA_LIB}/datasheets"

COLS = [
    "unique_id", "part_locator", "mpn", "manufacturer", "package", "value",
    "description", "datasheet", "manufacturer_link", "kicad_symbol", "kicad_footprint",
    "lifecycle_status", "rohs", "allow_substitution", "tracking", "standards_version",
    "created_by", "source", "dump_priority", "tier", "keywords", "pin_count",
    "temp_operating_min", "temp_operating_max",
    "capacity", "word_size", "speed", "supply_voltage_min", "supply_voltage_max",
    "persistence_years", "write_protect_voltage", "battery", "sram_socket", "rtc",
]

ADI, ST = "Analog Devices", "STMicroelectronics"
# VCC grades: (vcc_min, vcc_max, vtp_min, vtp_max, tolerance as printed).
DS_5PCT = (4.75, 5.25, 4.50, 4.75, "5V ±5%")
DS_10PCT = (4.50, 5.50, 4.25, 4.50, "5V ±10%")
ST_HI = (4.75, 5.50, 4.50, 4.75, "4.75-5.5V")
ST_LO = (4.50, 5.50, 4.20, 4.50, "4.5-5.5V")

# Stock land pattern per pin count (all 600-mil rows; see the docstring).
FOOTPRINT = {
    24: "Package_DIP:DIP-24_18.0mmx34.29mm_W15.24mm",
    28: "Package_DIP:DIP-28_W15.24mm",
    32: "Package_DIP:DIP-32_W15.24mm",
}


def C(**kw):
    return kw


# Each chip: one VCC grade, its ordering codes as (mpn, access time ns).
CHIPS = [
    # ---- Dallas / Analog Devices --------------------------------------------------
    C(mfr=ADI, value="DS1220AB", words=2048, pins=24, socket="6116", grade=DS_5PCT,
      symbol="Memory_RAM:M48Zx2", body="EDIP-24 720mil module", years=10,
      ds="analog-devices/ds1220ab-ds1220ad-2kx8-nvram.pdf",
      codes=[("DS1220AB-100+", 100)], kw=["DS1220", "2716"]),
    C(mfr=ADI, value="DS1220AD", words=2048, pins=24, socket="6116", grade=DS_10PCT,
      symbol="Memory_RAM:M48Zx2", body="EDIP-24 720mil module", years=10,
      ds="analog-devices/ds1220ab-ds1220ad-2kx8-nvram.pdf",
      codes=[("DS1220AD-100+", 100)], kw=["DS1220", "2716"]),
    C(mfr=ADI, value="DS1225AB", words=8192, pins=28, socket="6264", grade=DS_5PCT,
      symbol=f"{LIB}:DS1225", body="EDIP-28 720mil module", years=10, nc26=True,
      ds="analog-devices/ds1225ab-ds1225ad-8kx8-nvram.pdf",
      codes=[("DS1225AB-70+", 70)], kw=["DS1225", "2764", "2864"]),
    C(mfr=ADI, value="DS1225AD", words=8192, pins=28, socket="6264", grade=DS_10PCT,
      symbol=f"{LIB}:DS1225", body="EDIP-28 720mil module", years=10, nc26=True,
      ds="analog-devices/ds1225ab-ds1225ad-8kx8-nvram.pdf",
      codes=[("DS1225AD-70+", 70)], kw=["DS1225", "2764", "2864"]),
    C(mfr=ADI, value="DS1230AB", words=32768, pins=28, socket="62256", grade=DS_5PCT,
      symbol="Memory_RAM:HM62256BLP", body="EDIP-28 740mil module", years=10,
      ds="analog-devices/ds1230ab-ds1230y-32kx8-nvram.pdf",
      codes=[("DS1230AB-70+", 70)], kw=["DS1230", "27256"]),
    C(mfr=ADI, value="DS1230Y", words=32768, pins=28, socket="62256", grade=DS_10PCT,
      symbol="Memory_RAM:HM62256BLP", body="EDIP-28 740mil module", years=10,
      ds="analog-devices/ds1230ab-ds1230y-32kx8-nvram.pdf",
      codes=[("DS1230Y-70+", 70)], kw=["DS1230", "27256"]),
    C(mfr=ADI, value="DS1245AB", words=131072, pins=32, socket="628128", grade=DS_5PCT,
      symbol=f"{LIB}:DS1245", body="EDIP-32 740mil module", years=10, nc30=True,
      ds="analog-devices/ds1245ab-ds1245y-128kx8-nvram.pdf",
      codes=[("DS1245AB-70+", 70)], kw=["DS1245", "27C010"]),
    C(mfr=ADI, value="DS1245Y", words=131072, pins=32, socket="628128", grade=DS_10PCT,
      symbol=f"{LIB}:DS1245", body="EDIP-32 740mil module", years=10, nc30=True,
      ds="analog-devices/ds1245ab-ds1245y-128kx8-nvram.pdf",
      codes=[("DS1245Y-70+", 70)], kw=["DS1245", "27C010"]),
    C(mfr=ADI, value="DS1250AB", words=524288, pins=32, socket="628512", grade=DS_5PCT,
      symbol="Memory_RAM:AS6C4008-55PCN", body="EDIP-32 740mil module", years=10,
      ds="analog-devices/ds1250ab-ds1250y-512kx8-nvram.pdf",
      codes=[("DS1250AB-70+", 70)], kw=["DS1250", "27C040"]),
    C(mfr=ADI, value="DS1250Y", words=524288, pins=32, socket="628512", grade=DS_10PCT,
      symbol="Memory_RAM:AS6C4008-55PCN", body="EDIP-32 740mil module", years=10,
      ds="analog-devices/ds1250ab-ds1250y-512kx8-nvram.pdf",
      codes=[("DS1250Y-70+", 70)], kw=["DS1250", "27C040"]),
    # ---- ST ZEROPOWER ---------------------------------------------------------------
    C(mfr=ST, value="M48Z02", words=2048, pins=24, socket="6116", grade=ST_HI,
      symbol="Memory_RAM:M48Zx2", body="PCDIP-24 CAPHAT", years=10,
      ds="st/m48z02-m48z12-2kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z02.html",
      codes=[("M48Z02-70PC1", 70), ("M48Z02-150PC1", 150)], kw=["DS1220", "2716"]),
    C(mfr=ST, value="M48Z12", words=2048, pins=24, socket="6116", grade=ST_LO,
      symbol="Memory_RAM:M48Zx2", body="PCDIP-24 CAPHAT", years=10,
      ds="st/m48z02-m48z12-2kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z12.html",
      codes=[("M48Z12-70PC1", 70), ("M48Z12-150PC1", 150)], kw=["DS1220", "2716"]),
    C(mfr=ST, value="M48Z08", words=8192, pins=28, socket="6264", grade=ST_HI,
      symbol=f"{LIB}:DS1225", body="PCDIP-28 CAPHAT", years=11, nc26=True,
      ds="st/m48z08-m48z18-8kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z08.html",
      codes=[("M48Z08-100PC1", 100)], kw=["DS1225", "2764"]),
    C(mfr=ST, value="M48Z18", words=8192, pins=28, socket="6264", grade=ST_LO,
      symbol=f"{LIB}:DS1225", body="PCDIP-28 CAPHAT", years=11, nc26=True,
      ds="st/m48z08-m48z18-8kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z18.html",
      codes=[("M48Z18-100PC1", 100)], kw=["DS1225", "2764"]),
    C(mfr=ST, value="M48Z58", words=8192, pins=28, socket="6264", grade=ST_HI,
      symbol=f"{LIB}:DS1225", body="PCDIP-28 CAPHAT", years=10, nc26=True,
      ds="st/m48z58-m48z58y-8kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z58.html",
      codes=[("M48Z58-70PC1", 70)], kw=["DS1225", "2764"]),
    C(mfr=ST, value="M48Z58Y", words=8192, pins=28, socket="6264", grade=ST_LO,
      symbol=f"{LIB}:DS1225", body="PCDIP-28 CAPHAT", years=10, nc26=True,
      ds="st/m48z58-m48z58y-8kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z58y.html",
      codes=[("M48Z58Y-70PC1", 70)], kw=["DS1225", "2764"]),
    C(mfr=ST, value="M48Z35", words=32768, pins=28, socket="62256", grade=ST_HI,
      symbol="Memory_RAM:HM62256BLP", body="PCDIP-28 CAPHAT", years=10,
      ds="st/m48z35-m48z35y-32kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z35.html",
      codes=[("M48Z35-70PC1", 70)], kw=["DS1230", "27256"]),
    C(mfr=ST, value="M48Z35Y", words=32768, pins=28, socket="62256", grade=ST_LO,
      symbol="Memory_RAM:HM62256BLP", body="PCDIP-28 CAPHAT", years=10,
      ds="st/m48z35-m48z35y-32kx8-zeropower-sram.pdf",
      link="https://www.st.com/en/memories/m48z35y.html",
      codes=[("M48Z35Y-70PC1", 70)], kw=["DS1230", "27256"]),
]


def capacity(words):
    """Total bits in ic_memory's format: 2048 words -> '16 Kbit'."""
    kbit = words * 8 // 1024
    return f"{kbit // 1024} Mbit" if kbit % 1024 == 0 else f"{kbit} Kbit"


def org(words):
    return f"{words // 1024}Kx8"


def records():
    for chip in CHIPS:
        o = org(chip["words"])
        vmin, vmax, vtp_min, vtp_max, tol = chip["grade"]
        socket = chip["socket"]
        if chip.get("nc26"):
            socket_note = f"{socket} socket (pin 26 NC)"
        elif chip.get("nc30"):
            socket_note = f"{socket} socket (pin 30 NC)"
        else:
            socket_note = f"{socket} socket"
        for mpn, ns in chip["codes"]:
            desc = ", ".join([
                f"{chip['mfr']} {chip['value']} {o} battery-backed nonvolatile SRAM",
                socket_note, f"{ns}ns", tol,
                f"{chip['years']}-year data retention", chip["body"]])
            kw = [chip["value"], o, socket] + chip["kw"] + [
                "NVRAM", "NV SRAM", "battery-backed", "nonvolatile", "retro"]
            yield {
                "unique_id": f"{chip['mfr']}-{mpn}",
                "part_locator": f"nvram-{o.lower()}-dip{chip['pins']}",
                "mpn": mpn, "manufacturer": chip["mfr"], "package": chip["body"],
                "value": chip["value"], "description": desc,
                "datasheet": f"{DS_ROOT}/{chip['ds']}",
                "manufacturer_link": chip.get("link"),
                "kicad_symbol": chip["symbol"],
                "kicad_footprint": FOOTPRINT[chip["pins"]],
                "lifecycle_status": "Active", "rohs": "Yes",
                "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.0",
                "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
                "keywords": ", ".join(dict.fromkeys(kw)),
                "pin_count": str(chip["pins"]),
                "temp_operating_min": 0, "temp_operating_max": 70,
                "capacity": capacity(chip["words"]), "word_size": "8-bit",
                "speed": f"{ns} ns",
                "supply_voltage_min": vmin, "supply_voltage_max": vmax,
                "persistence_years": f"{chip['years']} years",
                "write_protect_voltage": f"{vtp_min:.2f}-{vtp_max:.2f} V",
                "battery": "integrated lithium", "sram_socket": socket, "rtc": "No",
            }


def sql(v):
    if v is None:
        return "NULL"
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    recs = list(records())
    ids = [r["unique_id"] for r in recs]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise SystemExit(f"duplicate unique_id: {dupes}")
    lines = [
        "-- Terra EDA Library - ic_nvram battery-backed nonvolatile SRAM modules",
        f"-- Generated by {CREATED_BY}. dump_priority=0, source=NULL: not dumped to "
        "static SQL.",
        "",
        "BEGIN TRANSACTION;",
        "",
    ]
    for r in recs:
        vals = ", ".join(sql(r[c]) for c in COLS)
        lines.append(f"INSERT INTO ic_nvram ({', '.join(COLS)}) VALUES ({vals});")
    lines += ["", "COMMIT;", ""]
    OUTPUT_FILE.write_text("\n".join(lines))
    print(f"Generated {OUTPUT_FILE.name}: {len(recs)} parts")


if __name__ == "__main__":
    main()
