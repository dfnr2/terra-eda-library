#!/usr/bin/env python3
"""TIMEKEEPER SRAMs: battery-backed SRAM modules with a real-time clock (rtc = 'Yes').

Same idea as run_300_nvram.py (byte-wide SRAM, lithium cell and power-fail switch in
the package), plus a 32.768 kHz crystal and BCD clock registers in the top eight
bytes. They drop into a JEDEC SRAM socket, so a vintage board gets a clock as well as
nonvolatile RAM. See plans/vintage-computer-parts.md.

One row per DIP-module ordering code, commercial temperature (0 to 70 C).

Sources, filed in datasheets/:
  - st/: Doc ID 2410 Rev 9 M48T02/M48T12, Doc ID 2411 Rev 11 M48T08/M48T18/M48T08Y,
    Doc ID 2611 Rev 10 M48T35/M48T35Y, Doc ID 2412 Rev 8 M48T58/M48T58Y (all June
    2011, fetched from st.com through Chrome).
  - analog-devices/: 19-5058 Rev 5/10 DS1643/DS1643P, 19-5203 Rev 4/10 DS1644/DS1644P.

Codes: ST's sheets give an ordering scheme (M48T + type + -speed + PC + 1; tubes have
no shipping letter). The codes used are the PCDIP ones each ST product page lists as
orderable on 2026-11-24: M48T02/12 -70 and -150 (the sheet's -200 is "not recommended
for new design"), M48T08/18 -100 and -150, M48T35/35Y/58/58Y -70. All eight product
pages show Active. Mouser stocked the M48T02/12 and M48T18 codes and listed the
M48T08, M48T35, M48T35Y and M48T58 ones with a 30-week factory lead time.
  - The M48T35 sheet says the M48T35Y comes only as the SOH28 SNAPHAT, but ST's
    product page and Mouser both list M48T35Y-70PC1, so the PCDIP code is used.
  - The M48T08Y is SOH28-only and is left out, as are the SOH28 parts generally.
  - Dallas codes are printed in each sheet's ordering table: DS1643-85+, DS1643-100+,
    DS1644-120+. Mouser lists all three as Obsolete (2026-11-24); they are kept for
    restorations, as plans/vintage-computer-parts.md decides. The P (PowerCap) codes are surface-mount and are left out. The DS1644
    table calls the module "32 EDIP"; its pin drawing and package table are 28-pin.

Clock features, from each sheet:
  - M48T02/12: registers 7F8-7FF; calibration; no century bit, alarm or interrupt.
  - M48T08/18: registers 1FF8-1FFF as the M48T02; INT power-fail interrupt on pin 1
    (open drain, pull-up needed even if unused); E1/E2 chip enables.
  - M48T35/35Y: registers 7FF8-7FFF; calibration; century bit.
  - M48T58/58Y: registers 1FF8-1FFF; calibration; century bit; battery-low flag; FT
    frequency-test output on pin 1 (open drain); E1/E2 chip enables.
  - DS1643/DS1644: registers 1FF8-1FFF / 7FF8-7FFF; oscillator stop and FT bits;
    leap-year compensation to 2100; no calibration or century register.

Footprints and symbols:
  - ST CAPHAT and Dallas EDIP bodies are wider than a DIP but sit on 600 mil rows; the
    24-pin parts use the 18 mm-body CAPHAT outline, as in run_300_nvram.py.
  - M48T02/12: stock Memory_RAM:M48Tx2 (its keywords name both).
  - M48T35/35Y and DS1644: stock Memory_RAM:HM62256BLP (62256 pinout).
  - DS1643: stock Memory_RAM:HY6264AxP (6264 with pin 1 NC and CS2 on pin 26).
  - M48T08/18 and M48T58/58Y: custom terra_symbols_ic_nvram:M48T08 and :M48T58 (pin 1
    INT or FT, E2 on pin 26), pin tables in _pinouts.py.

Generated output (dump_priority=0, source=NULL) is not dumped back to static SQL.
"""
from pathlib import Path

OUTPUT_FILE = Path(__file__).with_name("ic_nvram_generated_310_timekeepers.sql")
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
# VCC grades: (vcc_min, vcc_max, vpfd_min, vpfd_max, tolerance as printed)
ST_HI = (4.75, 5.50, 4.50, 4.75, "4.75-5.5V")
ST_LO = (4.50, 5.50, 4.20, 4.50, "4.5-5.5V")
DS1643_G = (4.50, 5.50, 4.25, 4.50, "5V ±10%")
DS1644_G = (4.50, 5.50, 4.00, 4.50, "5V ±10%")

FOOTPRINT = {
    24: "Package_DIP:DIP-24_18.0mmx34.29mm_W15.24mm",
    28: "Package_DIP:DIP-28_W15.24mm",
}

ST_LINK = "https://www.st.com/en/clocks-and-timers/{}.html"

CLOCK = {
    "M48T02": "BCD clock/calendar at 7F8-7FF with calibration",
    "M48T08": "BCD clock/calendar at 1FF8-1FFF with calibration, power-fail INT "
              "output on pin 1 (open drain), E1/E2 enables",
    "M48T35": "BCD clock/calendar at 7FF8-7FFF with calibration and century bit",
    "M48T58": "BCD clock/calendar at 1FF8-1FFF with calibration, century bit and "
              "battery-low flag, FT output on pin 1 (open drain), E1/E2 enables",
    "DS1643": "BCD clock/calendar at 1FF8-1FFF, leap years to 2100",
    "DS1644": "BCD clock/calendar at 7FF8-7FFF, leap years to 2100",
}


def C(**kw):
    return kw


CHIPS = [
    C(mfr=ST, value="M48T02", clock="M48T02", words=2048, pins=24, socket="6116",
      grade=ST_HI, symbol="Memory_RAM:M48Tx2", body="PCDIP-24 CAPHAT", years=10,
      ds="st/m48t02-m48t12-2kx8-timekeeper-sram.pdf",
      codes=[("M48T02-70PC1", 70), ("M48T02-150PC1", 150)], kw=["DS1642", "2716"]),
    C(mfr=ST, value="M48T12", clock="M48T02", words=2048, pins=24, socket="6116",
      grade=ST_LO, symbol="Memory_RAM:M48Tx2", body="PCDIP-24 CAPHAT", years=10,
      ds="st/m48t02-m48t12-2kx8-timekeeper-sram.pdf",
      codes=[("M48T12-70PC1", 70), ("M48T12-150PC1", 150)], kw=["DS1642", "2716"]),
    C(mfr=ST, value="M48T08", clock="M48T08", words=8192, pins=28, socket="6264",
      grade=ST_HI, symbol=f"{LIB}:M48T08", body="PCDIP-28 CAPHAT", years=10,
      ds="st/m48t08-m48t18-8kx8-timekeeper-sram.pdf",
      codes=[("M48T08-100PC1", 100), ("M48T08-150PC1", 150)], kw=["DS1643"]),
    C(mfr=ST, value="M48T18", clock="M48T08", words=8192, pins=28, socket="6264",
      grade=ST_LO, symbol=f"{LIB}:M48T08", body="PCDIP-28 CAPHAT", years=10,
      ds="st/m48t08-m48t18-8kx8-timekeeper-sram.pdf",
      codes=[("M48T18-100PC1", 100), ("M48T18-150PC1", 150)], kw=["DS1643"]),
    C(mfr=ST, value="M48T35", clock="M48T35", words=32768, pins=28, socket="62256",
      grade=ST_HI, symbol="Memory_RAM:HM62256BLP", body="PCDIP-28 CAPHAT", years=10,
      ds="st/m48t35-m48t35y-32kx8-timekeeper-sram.pdf",
      codes=[("M48T35-70PC1", 70)], kw=["DS1644", "27256"]),
    C(mfr=ST, value="M48T35Y", clock="M48T35", words=32768, pins=28, socket="62256",
      grade=ST_LO, symbol="Memory_RAM:HM62256BLP", body="PCDIP-28 CAPHAT", years=10,
      ds="st/m48t35-m48t35y-32kx8-timekeeper-sram.pdf",
      codes=[("M48T35Y-70PC1", 70)], kw=["DS1644", "27256"]),
    C(mfr=ST, value="M48T58", clock="M48T58", words=8192, pins=28, socket="6264",
      grade=ST_HI, symbol=f"{LIB}:M48T58", body="PCDIP-28 CAPHAT", years=7,
      ds="st/m48t58-m48t58y-8kx8-timekeeper-sram.pdf",
      codes=[("M48T58-70PC1", 70)], kw=["DS1643"]),
    C(mfr=ST, value="M48T58Y", clock="M48T58", words=8192, pins=28, socket="6264",
      grade=ST_LO, symbol=f"{LIB}:M48T58", body="PCDIP-28 CAPHAT", years=7,
      ds="st/m48t58-m48t58y-8kx8-timekeeper-sram.pdf",
      codes=[("M48T58Y-70PC1", 70)], kw=["DS1643"]),
    C(mfr=ADI, value="DS1643", clock="DS1643", words=8192, pins=28, socket="6264",
      grade=DS1643_G, symbol="Memory_RAM:HY6264AxP", body="EDIP-28 740mil module",
      years=10, ds="analog-devices/ds1643-8kx8-timekeeper-nvram.pdf",
      codes=[("DS1643-85+", 85), ("DS1643-100+", 100)], kw=["M48T08", "M48T58"],
      status="Obsolete"),
    C(mfr=ADI, value="DS1644", clock="DS1644", words=32768, pins=28, socket="62256",
      grade=DS1644_G, symbol="Memory_RAM:HM62256BLP", body="EDIP-28 740mil module",
      years=10, ds="analog-devices/ds1644-32kx8-timekeeper-nvram.pdf",
      codes=[("DS1644-120+", 120)], kw=["M48T35", "27256"], status="Obsolete"),
]


def capacity(words):
    kbit = words * 8 // 1024
    return f"{kbit // 1024} Mbit" if kbit % 1024 == 0 else f"{kbit} Kbit"


def records():
    root = Path(__file__).resolve().parents[3]
    for chip in CHIPS:
        ds_file = root / "datasheets" / chip["ds"]
        if not ds_file.is_file():
            raise SystemExit(f"missing datasheet {ds_file}")
        o = f"{chip['words'] // 1024}Kx8"
        vmin, vmax, vpf_min, vpf_max, tol = chip["grade"]
        link = ST_LINK.format(chip["value"].lower()) if chip["mfr"] == ST else None
        for mpn, ns in chip["codes"]:
            desc = ", ".join([
                f"{chip['mfr']} {chip['value']} {o} TIMEKEEPER battery-backed SRAM with "
                f"real-time clock", CLOCK[chip["clock"]], f"{chip['socket']} socket",
                f"{ns}ns", tol, f"{chip['years']}-year data retention", chip["body"]])
            kw = [chip["value"], o, chip["socket"]] + chip["kw"] + [
                "TIMEKEEPER", "RTC", "real-time clock", "NVRAM", "battery-backed",
                "nonvolatile", "retro"]
            yield {
                "unique_id": f"{chip['mfr']}-{mpn}",
                "part_locator": f"nvram-rtc-{o.lower()}-dip{chip['pins']}",
                "mpn": mpn, "manufacturer": chip["mfr"], "package": chip["body"],
                "value": chip["value"], "description": desc,
                "datasheet": f"{DS_ROOT}/{chip['ds']}", "manufacturer_link": link,
                "kicad_symbol": chip["symbol"],
                "kicad_footprint": FOOTPRINT[chip["pins"]],
                "lifecycle_status": chip.get("status", "Active"), "rohs": "Yes",
                "allow_substitution": "Yes", "tracking": "No", "standards_version": "1.0",
                "created_by": CREATED_BY, "source": None, "dump_priority": 0, "tier": 2,
                "keywords": ", ".join(dict.fromkeys(kw)),
                "pin_count": str(chip["pins"]),
                "temp_operating_min": 0, "temp_operating_max": 70,
                "capacity": capacity(chip["words"]), "word_size": "8-bit",
                "speed": f"{ns} ns",
                "supply_voltage_min": vmin, "supply_voltage_max": vmax,
                "persistence_years": f"{chip['years']} years",
                "write_protect_voltage": f"{vpf_min:.2f}-{vpf_max:.2f} V",
                "battery": "integrated lithium", "sram_socket": chip["socket"],
                "rtc": "Yes",
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
        "-- Terra EDA Library - ic_nvram TIMEKEEPER SRAMs (battery-backed SRAM + RTC)",
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
