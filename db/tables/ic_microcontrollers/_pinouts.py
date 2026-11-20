"""Pin tables for the custom ic_microcontrollers symbols.

Microchip PIC32CM6408PL10 (datasheet DS40002667A, section 2.3 "Pinout and
Multiplexing"): one row per pad giving its pin number in each package layout. The
32/48/64-pin TQFP and VQFN share numbering; the VQFNs add an exposed pad, which the
datasheet does not assign, so it is a separate passive EP pin. The 28-pin VQFN is
numbered differently from the 28-pin SSOP/SPDIP. Write the symbols with

    python3 tools/make_dip_symbol.py db/tables/ic_microcontrollers/_pinouts.py \\
        kicad_symbols/terra_symbols_ic_microcontrollers.kicad_sym

Pin types: see tools/make_dip_symbol.py.
"""

# (pad, special function, 64-pin, 48-pin, 32-pin, 28-pin VQFN, 28-pin SSOP/SPDIP)
PL10 = [
    ("PA00", None, 62, 44, 30, 26, 22),
    ("PA01", None, 63, 45, 31, 27, 23),
    ("PA02", None, 64, 46, 32, 28, 24),
    ("PA03", None, 1, 47, 1, 1, 25),
    ("PA04", None, 2, 48, 2, 2, 26),
    ("PA05", None, 3, 1, 3, 3, 27),
    ("PA06", None, 4, 2, 4, 4, 28),
    ("PA07", None, 5, 3, 5, 5, 1),
    ("VDD", None, 6, None, None, None, None),
    ("GND", None, 7, None, None, None, None),
    ("PB00", None, 8, 4, None, None, None),
    ("PB01", None, 9, 5, None, None, None),
    ("PB02", None, 10, 6, None, None, None),
    ("PB03", None, 11, 7, None, None, None),
    ("PB04", None, 12, 8, None, None, None),
    ("PB05", None, 13, 9, None, None, None),
    ("PB06", None, 14, None, None, None, None),
    ("PB07", None, 15, None, None, None, None),
    ("PA08", None, 16, 10, 6, 6, 2),
    ("PA09", None, 17, 11, 7, 7, 3),
    ("PA10", None, 18, 12, 8, 8, 4),
    ("PA11", None, 19, 13, 9, 9, 5),
    ("VDDIO2", None, 20, 14, 10, 10, 6),
    ("GND", None, 21, 15, None, None, None),
    ("PA12", None, 22, 16, None, None, None),
    ("PA13", None, 23, 17, None, None, None),
    ("PA14", None, 24, 18, None, None, None),
    ("PA15", None, 25, 19, None, None, None),
    ("PA16", None, 26, 20, None, None, None),
    ("PA17", None, 27, 21, 11, 11, 7),
    ("PA18", None, 28, 22, 12, 12, 8),
    ("PA19", None, 29, 23, 13, 13, 9),
    ("PA20", "SWDIO", 30, 24, 14, 14, 10),
    ("PA21", None, 31, 25, 15, 15, 11),
    ("PA22", None, 32, 26, 16, 16, 12),
    ("PA23", "VREFA", 33, 27, 17, 17, 13),
    ("AVDD", None, 34, 28, 18, 18, 14),
    ("AGND", None, 35, 29, 19, 19, 15),
    ("PB08", None, 36, 30, None, None, None),
    ("PB09", None, 37, 31, None, None, None),
    ("PB10", None, 38, 32, None, None, None),
    ("PB11", None, 39, 33, None, None, None),
    ("PB12", None, 40, None, None, None, None),
    ("PB13", None, 41, None, None, None, None),
    ("PB14", None, 42, None, None, None, None),
    ("PB15", None, 43, None, None, None, None),
    ("PA24", "XTAL32K1", 44, 34, 20, 20, 16),
    ("PA25", "XTAL32K2", 45, 35, 21, 21, 17),
    ("PA26", None, 46, 36, 22, None, None),
    ("PA27", None, 47, 37, 23, None, None),
    ("PA28", None, 48, 38, 24, None, None),
    ("PA29", None, 49, 39, 25, None, None),
    ("PA30", "~{RESET}", 50, 40, 26, 22, 18),
    ("PA31", "SWCLK", 51, 41, 27, 23, 19),
    ("PB16", None, 52, None, None, None, None),
    ("PB17", None, 53, None, None, None, None),
    ("PB18", None, 54, None, None, None, None),
    ("PB19", None, 55, None, None, None, None),
    ("VDD", None, 56, 42, 28, 24, 20),
    ("GND", None, 57, 43, 29, 25, 21),
    ("PB20", None, 58, None, None, None, None),
    ("PB21", None, 59, None, None, None, None),
    ("PB22", None, 60, None, None, None, None),
    ("PB23", None, 61, None, None, None, None),
]

SUPPLIES = {"VDD", "GND", "VDDIO2", "AVDD", "AGND"}
COLUMN = {"64": 2, "48": 3, "32": 4, "28-VQFN": 5, "28": 6}


def _pl10(layout, footprint, package, ep=None):
    col = COLUMN[layout]
    pins, pa, pb = {}, [], []
    for pad, special, *nums in PL10:
        num = (pad, special, *nums)[col]
        if num is None:
            continue
        if pad in SUPPLIES:
            pins[num] = (pad, "pwr")
            continue
        name = f"{pad}/{special}" if special else pad
        pins[num] = (name, "bidi")
        (pa if pad.startswith("PA") else pb).append((pad, name))
    left = [n for _, n in sorted(pa)]
    right = [n for _, n in sorted(pb)]
    if not pb:  # 28/32-pin parts: PA00-PA15 left, PA16-PA31 right
        left = [n for p, n in sorted(pa) if int(p[2:]) < 16]
        right = [n for p, n in sorted(pa) if int(p[2:]) >= 16]
    if ep:
        pins[ep] = ("EP", "pas")
        right += [None, "EP"]
    present = {v[0] for v in pins.values()}
    top = [s for s in ("VDD", "AVDD", "VDDIO2") if s in present]
    bottom = [s for s in ("GND", "AGND") if s in present]
    pin_count = max(pins)
    return dict(
        pins=dict(sorted(pins.items())), left=left, right=right,
        top=top, bottom=bottom, width=30.48, footprint=footprint,
        description=(f"PIC32CM6408PL10 Arm Cortex-M0+ MCU, 64KB Flash, 8KB SRAM, "
                     f"1.8-5.5V, {package}"),
        keywords=f"PIC32CM PL10 Cortex-M0+ MCU 5V {package.split()[0]}")


PINOUTS = {
    "PIC32CM6408PL10028-SS_SP": _pl10(
        "28", "Package_SO:SSOP-28_5.3x10.2mm_P0.65mm", "SSOP-28 / SPDIP-28 pinout"),
    "PIC32CM6408PL10028-3LW": _pl10(
        "28-VQFN", "Package_DFN_QFN:QFN-28-1EP_4x4mm_P0.4mm_EP2.4x2.4mm", "VQFN-28", ep=29),
    "PIC32CM6408PL10032-PT": _pl10("32", "Package_QFP:TQFP-32_7x7mm_P0.8mm", "TQFP-32"),
    "PIC32CM6408PL10032-QZB": _pl10(
        "32", "Package_DFN_QFN:VQFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm", "VQFN-32", ep=33),
    "PIC32CM6408PL10048-PT": _pl10("48", "Package_QFP:TQFP-48_7x7mm_P0.5mm", "TQFP-48"),
    "PIC32CM6408PL10048-6MX": _pl10(
        "48", "Package_DFN_QFN:VQFN-48-1EP_6x6mm_P0.4mm_EP4.1x4.1mm", "VQFN-48", ep=49),
    "PIC32CM6408PL10064-PT": _pl10("64", "Package_QFP:TQFP-64_10x10mm_P0.5mm", "TQFP-64"),
    "PIC32CM6408PL10064-5LX": _pl10(
        "64", "Package_DFN_QFN:VQFN-64-1EP_9x9mm_P0.5mm_EP5.4x5.4mm", "VQFN-64", ep=65),
}
