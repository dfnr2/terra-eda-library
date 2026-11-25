#!/usr/bin/env python3
"""Classic through-hole DIP optocouplers: 4N2x/4N3x, CNY17, PC817, 6N13x, HCPL-26xx,
H11L1, H11AA1 and the MOC30xx triac drivers.

Sources (plans/optocouplers-th-classics.md has the detail):

  - onsemi, the Fairchild-heritage 6-pin DIP line (4N25M..4N37M, 4N32M/4N33M,
    H11L1M, MOC302xM/MOC304xM/MOC306xM). The bare `...M` code is the DIP-6 tube or
    bulk part; S, SR2, T and V suffixes are the gull-wing, reel, 0.4" and VDE options
    and are not used. onsemi stands in for Vishay on the 4N parts: Vishay's current
    phototransistor and photodarlington selector tables no longer list 4N25..4N37 or
    4N32/4N33, while onsemi's product pages list every one Active.
  - Vishay for CNY17-1..-4 and H11AA1, both still in its selector tables. The bare
    code is the DIP-6 tube part.
  - Broadcom for 6N135/6N136, 6N137/HCPL-2601/HCPL-2630 and 6N138/6N139, ordering
    option -000E (RoHS, plain 300-mil DIP-8, 50 per tube).
  - Sharp for the PC817: PC817XNNSZ1B, the through-hole sleeve part with no CTR rank.
    Sharp's lineup now lists only the 4-pin DIP photocouplers, so PC827 and PC847 are
    left out.

Pin tables are transcribed from each sheet and checked against the named symbol by
_opto.rows(). Times are max unless marked typ; where a sheet gives only rise/fall
or propagation delays, the field names them (tPHL is turn-on: LED on, output low).

Generated output (dump_priority=0, source=NULL) is not dumped to static SQL.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _opto import CUSTOM_LIB, Part, write  # noqa: E402

OUTPUT_FILE = HERE / "optocouplers_generated_310_th_optocouplers.sql"
CREATED_BY = Path(__file__).name


def on(mpn):
    return f"https://www.onsemi.com/PowerSolutions/product.do?id={mpn}"


BCM = "https://www.broadcom.com/products/optocouplers/industrial-plastic/digital-optocouplers/"
SHARP = "https://global.sharp/products/device/lineup/selection/opto/pc/dip_4pin.html"

# Pin tables, pin 1 first, as each data sheet draws them.
PHOTO_B = "1A 2K 3NC 4E 5C 6B"            # 4N25..4N37, CNY17, 4N32/4N33
HS_8 = "1NC 2A 3K 4NC 5GND 6VO 7VB 8VCC"  # 6N135/6N136, 6N138/6N139 (pin 7 = VB)
LOGIC_8 = "1NC 2A 3K 4NC 5GND 6VO 7EN 8VCC"
TRIAC = "1A 2K 3NC 4MT 5NC 6MT"           # pin 5 = triac substrate, do not connect

# onsemi 4N37M/D (Rev. 2, 2021) covers 4N25M..4N37M: VCEO 30V for every grade; the
# sheet gives no collector-current rating (detector PD 150mW).
ON_4N = dict(manufacturer="onsemi", output_type="phototransistor", channels=1, pins=6,
             pinout=PHOTO_B, isolation="4170Vrms", vf="1.18V typ, 1.50V max @ IF=10mA",
             vo_max="30V", datasheet="onsemi/4n37m-d.pdf")
ON_4N2X_T = dict(t_on="2us typ (IF=10mA, VCC=10V, RL=100R)",
                 t_off="2us typ (IF=10mA, VCC=10V, RL=100R)")
ON_4N3X_T = dict(t_on="10us max (IC=2mA, VCC=10V, RL=100R)",
                 t_off="10us max (IC=2mA, VCC=10V, RL=100R)")

# onsemi H11B1M/D (Rev. 2, 2022) covers 4N32M/4N33M.
ON_4N3D = dict(manufacturer="onsemi", output_type="darlington", channels=1, pins=6,
               symbol=f"{CUSTOM_LIB}:4N32", pinout=PHOTO_B, isolation="4170Vrms",
               ctr="500% min @ IF=10mA, VCE=10V", vf="1.2V typ, 1.5V max @ IF=10mA",
               vo_max="30V", io_max="150mA",
               t_on="5us max (IF=200mA, IC=50mA, VCC=10V, RL=100R)",
               t_off="100us max (IF=200mA, IC=50mA, VCC=10V, RL=100R)",
               datasheet="onsemi/h11b1m-d.pdf", keywords="base-connection")

# Vishay CNY17 (doc 83606, Rev. 2.1): times are typ, non-saturated switching.
VI_CNY17 = dict(manufacturer="Vishay", output_type="phototransistor", channels=1, pins=6,
                pinout=PHOTO_B, isolation="5000Vrms",
                vf="1.39V typ, 1.65V max @ IF=60mA", vo_max="70V", io_max="50mA",
                t_on="3us typ (IF=10mA, VCC=5V, RL=75R, non-saturated)",
                t_off="2.3us typ (IF=10mA, VCC=5V, RL=75R, non-saturated)",
                datasheet="vishay/cny17.pdf",
                link="https://www.vishay.com/en/product/83606/", keywords="base-connection")

# Broadcom AV02-0940EN (2021) covers 6N137, HCPL-2601, HCPL-2630.
BC_LOGIC = dict(manufacturer="Broadcom", output_type="logic", pins=8, isolation="3750Vrms",
                vf="1.5V typ, 1.75V max @ IF=10mA", if_on="5mA max (ITH)",
                vo_max="7V (VO and VCC)", io_max="50mA",
                t_on="tPHL 75ns max at 25C, 100ns over temp (IF=7.5mA, RL=350R)",
                t_off="tPLH 75ns max at 25C, 100ns over temp (IF=7.5mA, RL=350R)",
                datasheet="broadcom/6n137-hcpl-2601-2630.pdf", keywords="10MBd,TTL")

# Broadcom AV02-0171EN (2019) covers 6N135/6N136: VO 20V (JEDEC registers 15V).
BC_HS = dict(manufacturer="Broadcom", output_type="transistor-high-speed", channels=1,
             pins=8, pinout=HS_8, isolation="3750Vrms",
             vf="1.5V typ, 1.7V max @ IF=16mA", vo_max="20V (VO; JEDEC 15V)",
             io_max="8mA avg, 16mA peak", datasheet="broadcom/6n135-6n136-hcpl-2502.pdf",
             keywords="1MBd")

# Broadcom AV02-1359EN (2025) covers 6N138/6N139 (split Darlington).
BC_DARL = dict(manufacturer="Broadcom", output_type="darlington", channels=1, pins=8,
               pinout=HS_8, isolation="3750Vrms",
               vf="1.40V typ, 1.7V max @ IF=1.6mA", io_max="60mA",
               datasheet="broadcom/6n138-6n139-hcpl-0700.pdf",
               keywords="split-darlington,low-input-current,high-gain")

# onsemi triac drivers: MOC3023M/D (Rev. 3), MOC3043M/D (Rev. 4), MOC3163M/D (Rev. 3).
ON_TRIAC = dict(manufacturer="onsemi", channels=1, pins=6, pinout=TRIAC,
                isolation="4170Vrms", keywords="ac-switching")
RANDOM = dict(ON_TRIAC, output_type="triac-driver", vf="1.15V typ, 1.50V max @ IF=10mA",
              vo_max="400V (VDRM)", io_max="1A peak (ITSM, 100us, 120pps)",
              datasheet="onsemi/moc3023m-d.pdf")
ZC400 = dict(ON_TRIAC, output_type="triac-driver-zc", vf="1.25V typ, 1.50V max @ IF=30mA",
             vo_max="400V (VDRM)", io_max="100mA peak (ITM, repetitive)",
             datasheet="onsemi/moc3043m-d.pdf", note="zero-crossing, inhibit 20V max")
ZC600 = dict(ON_TRIAC, output_type="triac-driver-zc", vf="1.3V typ, 1.5V max @ IF=30mA",
             vo_max="600V (VDRM)", io_max="100mA peak (ITM, repetitive)",
             datasheet="onsemi/moc3163m-d.pdf", note="zero-crossing")

PARTS = [
    # --- phototransistor, base connection, DIP-6 ---------------------------------
    Part(mpn="4N25M", value="4N25", symbol="Isolator:4N25",
         ctr="20% min @ IF=10mA, VCE=10V", link=on("4N25M"), **ON_4N, **ON_4N2X_T),
    Part(mpn="4N26M", value="4N26", symbol="Isolator:4N26",
         ctr="20% min @ IF=10mA, VCE=10V", link=on("4N26M"), **ON_4N, **ON_4N2X_T),
    Part(mpn="4N27M", value="4N27", symbol="Isolator:4N27",
         ctr="10% min @ IF=10mA, VCE=10V", link=on("4N27M"), **ON_4N, **ON_4N2X_T),
    Part(mpn="4N28M", value="4N28", symbol="Isolator:4N28",
         ctr="10% min @ IF=10mA, VCE=10V", link=on("4N28M"), **ON_4N, **ON_4N2X_T),
    Part(mpn="4N35M", value="4N35", symbol="Isolator:4N35",
         ctr="100% min @ IF=10mA, VCE=10V", link=on("4N35M"), **ON_4N, **ON_4N3X_T),
    Part(mpn="4N36M", value="4N36", symbol="Isolator:4N36",
         ctr="100% min @ IF=10mA, VCE=10V", link=on("4N36M"), **ON_4N, **ON_4N3X_T),
    Part(mpn="4N37M", value="4N37", symbol="Isolator:4N37",
         ctr="100% min @ IF=10mA, VCE=10V", link=on("4N37M"), **ON_4N, **ON_4N3X_T),
    Part(mpn="CNY17-1", value="CNY17-1", symbol="Isolator:CNY17-1",
         ctr="40-80% @ IF=10mA, VCE=5V", note="CTR bin 1", **VI_CNY17),
    Part(mpn="CNY17-2", value="CNY17-2", symbol="Isolator:CNY17-2",
         ctr="63-125% @ IF=10mA, VCE=5V", note="CTR bin 2", **VI_CNY17),
    Part(mpn="CNY17-3", value="CNY17-3", symbol="Isolator:CNY17-3",
         ctr="100-200% @ IF=10mA, VCE=5V", note="CTR bin 3", **VI_CNY17),
    Part(mpn="CNY17-4", value="CNY17-4", symbol="Isolator:CNY17-4",
         ctr="160-320% @ IF=10mA, VCE=5V", note="CTR bin 4", **VI_CNY17),
    # Vishay H11AA1 (doc 83608, Rev. 2.0, 2026): no IC rating or switching table.
    Part(manufacturer="Vishay", mpn="H11AA1", value="H11AA1",
         output_type="phototransistor", channels=1, pins=6, symbol="Isolator:H11AA1",
         pinout="1AK 2AK 3NC 4E 5C 6B", isolation="5000Vrms",
         ctr="20% min @ IF=+/-10mA, VCE=10V", vf="1.2V typ, 1.5V max @ IF=+/-10mA",
         vo_max="80V", datasheet="vishay/h11aa1.pdf",
         link="https://www.vishay.com/en/product/83608/",
         note="AC input (two anti-parallel LEDs), base connection",
         keywords="ac-input,bidirectional-input,ac-line-detection,base-connection"),

    # --- photodarlington, DIP-6 (terra symbol: no stock 4N32/4N33) ---------------
    Part(mpn="4N32M", value="4N32", link=on("4N32M"), **ON_4N3D),
    Part(mpn="4N33M", value="4N33", link=on("4N33M"),
         **dict(ON_4N3D, symbol=f"{CUSTOM_LIB}:4N33")),

    # --- phototransistor, DIP-4 ---------------------------------------------------
    # Sharp OP18002EN (2018): IC 2.5-30mA at IF=5mA is 50-600% (the cover text says
    # 50-400%; the characteristics table governs). Only rise/fall times are given.
    Part(manufacturer="Sharp", mpn="PC817XNNSZ1B", value="PC817",
         output_type="phototransistor", channels=1, pins=4, symbol="Isolator:PC817",
         pinout="1A 2K 3E 4C", isolation="5000Vrms", ctr="50-600% @ IF=5mA, VCE=5V",
         vf="1.2V typ, 1.4V max @ IF=20mA", vo_max="80V", io_max="50mA",
         t_on="tr 18us max (VCE=2V, IC=2mA, RL=100R)",
         t_off="tf 18us max (VCE=2V, IC=2mA, RL=100R)",
         datasheet="sharp/pc817xxnsz1b.pdf", link=SHARP, note="no CTR rank, sleeve"),

    # --- high-speed transistor output, DIP-8 --------------------------------------
    Part(mpn="6N135-000E", value="6N135", symbol="Isolator:6N135",
         ctr="7-50% @ IF=16mA, VO=0.4V, VCC=4.5V",
         t_on="tPHL 1.5us max (IF=16mA, RL=4.1k)", t_off="tPLH 1.5us max (IF=16mA, RL=4.1k)",
         link=BCM + "1mbd/6n135", **BC_HS),
    Part(mpn="6N136-000E", value="6N136", symbol="Isolator:6N136",
         ctr="19-50% @ IF=16mA, VO=0.4V, VCC=4.5V",
         t_on="tPHL 0.8us max (IF=16mA, RL=1.9k)", t_off="tPLH 0.8us max (IF=16mA, RL=1.9k)",
         link=BCM + "1mbd/6n136", note="TTL-load CTR grade", **BC_HS),

    # --- split-Darlington, DIP-8 ---------------------------------------------------
    Part(mpn="6N138-000E", value="6N138", symbol="Isolator:6N138",
         ctr="300-2600% @ IF=1.6mA, VO=0.4V, VCC=4.5V",
         if_on="1.6mA (min input ON current)", vo_max="7V (VO and VCC)",
         t_on="tPHL 10us max at 25C, 15us over temp (IF=1.6mA, RL=2.2k)",
         t_off="tPLH 35us max at 25C, 50us over temp (IF=1.6mA, RL=2.2k)",
         link=BCM + "100kbd/6n138", note="split Darlington", **BC_DARL),
    Part(mpn="6N139-000E", value="6N139", symbol="Isolator:6N139",
         ctr="400-5000% @ IF=0.5mA, VO=0.4V, VCC=4.5V",
         if_on="0.5mA (min input ON current)", vo_max="18V (VO and VCC)",
         t_on="tPHL 25us max at 25C, 30us over temp (IF=0.5mA, RL=4.7k)",
         t_off="tPLH 60us max at 25C, 90us over temp (IF=0.5mA, RL=4.7k)",
         link=BCM + "100kbd/6n139", note="split Darlington", **BC_DARL),

    # --- logic-gate output, DIP-8 --------------------------------------------------
    Part(mpn="6N137-000E", value="6N137", channels=1, symbol="Isolator:6N137",
         pinout=LOGIC_8, link=BCM + "10mbd/6n137",
         note="output enable, CMR 1kV/us", **BC_LOGIC),
    Part(mpn="HCPL-2601-000E", value="HCPL-2601", channels=1, symbol="Isolator:HCPL-2601",
         pinout=LOGIC_8, link=BCM + "10mbd/hcpl-2601",
         note="output enable, CMR 10kV/us", **BC_LOGIC),
    Part(mpn="HCPL-2630-000E", value="HCPL-2630", channels=2, symbol="Isolator:HCPL-2630",
         pinout="1A1 2K1 3K2 4A2 5GND 6VO2 7VO1 8VCC", link=BCM + "10mbd/hcpl-2630",
         note="no enable, CMR 5kV/us", **BC_LOGIC),

    # --- Schmitt-trigger output, DIP-6 ---------------------------------------------
    # onsemi H11L3M/D (Rev. 4, 2024): open-collector output; VO and VCC 16V abs max.
    Part(manufacturer="onsemi", mpn="H11L1M", value="H11L1", output_type="schmitt",
         channels=1, pins=6, symbol="Isolator:H11L1", pinout="1A 2K 3NC 4VO 5GND 6VCC",
         isolation="4170Vrms", vf="1.2V typ, 1.5V max @ IF=10mA",
         if_on="1.6mA max (IF(on), VCC=5V, RL=270R)", vo_max="16V (VO and VCC)",
         io_max="50mA", t_on="4us max (VCC=5V, RL=270R)", t_off="4us max (VCC=5V, RL=270R)",
         datasheet="onsemi/h11l3m-d.pdf", link=on("H11L1M"),
         note="open-collector, hysteresis", keywords="open-collector,hysteresis"),

    # --- triac drivers, DIP-6 ------------------------------------------------------
    Part(mpn="MOC3021M", value="MOC3021", symbol="Relay_SolidState:MOC3021M",
         if_on="15mA max (IFT)", link=on("MOC3021M"), **RANDOM),
    Part(mpn="MOC3022M", value="MOC3022", symbol="Relay_SolidState:MOC3022M",
         if_on="10mA max (IFT)", link=on("MOC3022M"), **RANDOM),
    Part(mpn="MOC3023M", value="MOC3023", symbol="Relay_SolidState:MOC3023M",
         if_on="5mA max (IFT)", link=on("MOC3023M"), **RANDOM),
    Part(mpn="MOC3041M", value="MOC3041", symbol="Relay_SolidState:MOC3041M",
         if_on="15mA max (IFT)", link=on("MOC3041M"), **ZC400),
    Part(mpn="MOC3043M", value="MOC3043", symbol="Relay_SolidState:MOC3043M",
         if_on="5mA max (IFT)", link=on("MOC3043M"), **ZC400),
    Part(mpn="MOC3063M", value="MOC3063", symbol="Relay_SolidState:MOC3063M",
         if_on="5mA max (IFT)", link=on("MOC3063M"), **ZC600),
]


if __name__ == "__main__":
    write(OUTPUT_FILE, "through-hole DIP optocouplers", CREATED_BY, PARTS)
