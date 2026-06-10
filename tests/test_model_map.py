"""Lock the codified CERN package -> KiCad 3D model resolution rules.

The point of tools/model_map is that the mapping is decided once, in code.
These tests pin the decisions so a future edit can't silently change them.
"""
import pytest

from tools.model_map import (
    kicad_3dmodel_dir, kicad_footprint_dir, native_centroid,
    resolve_connector, resolve_from_footprint, resolve_model,
)

_HAVE_KICAD = kicad_3dmodel_dir() is not None
_needs_kicad = pytest.mark.skipif(
    not _HAVE_KICAD, reason="KiCad bundled 3dmodels not installed")


def test_exact_smd_package():
    assert resolve_model("DO-214AC").endswith("/Diode_SMD.3dshapes/D_SMA.step")
    assert resolve_model("SOD-123").endswith("/Diode_SMD.3dshapes/D_SOD-123.step")
    assert resolve_model("SOT23-3").endswith("/Package_TO_SOT_SMD.3dshapes/SOT-23.step")


def test_unknown_package_is_none():
    assert resolve_model("NO-SUCH-PACKAGE") is None


def test_axial_needs_pitch():
    # Without a measured pitch an axial family cannot be resolved.
    assert resolve_model("DO-41") is None


@_needs_kicad
def test_axial_exact_pitch():
    ref = resolve_model("DO-41", pad_pitch_mm=10.16)
    assert ref.endswith("_P10.16mm_Horizontal.step")
    assert "D_DO-41_SOD81" in ref


@_needs_kicad
def test_axial_nearest_within_tolerance():
    # DO-15 at 13.97mm has no exact model; nearest (15.24) is within tolerance.
    ref = resolve_model("DO-15", pad_pitch_mm=13.97)
    assert ref is not None and ref.endswith("_P15.24mm_Horizontal.step")


@_needs_kicad
def test_axial_wide_best_effort_largest():
    # DO-201AD footprint at 20.32mm has no exact model; nearest (15.24, the
    # largest) is within the best-effort cap, so we take it rather than decline.
    ref = resolve_model("DO-201AD", pad_pitch_mm=20.32)
    assert ref is not None and ref.endswith("_P15.24mm_Horizontal.step")


@_needs_kicad
def test_axial_gross_mismatch_declined():
    # DO-41 ships up to 12.70mm; 40mm is beyond the cap -> no plausible model.
    assert resolve_model("DO-41", pad_pitch_mm=40.0) is None


@_needs_kicad
def test_bridge_from_footprint_name():
    ref = resolve_from_footprint("FAIRCHILD_GBU_V")
    assert ref.endswith("/Diode_Bridge_Vishay_GBU.step")
    assert resolve_from_footprint("VISHAY_KBU").endswith("/Diode_Bridge_Vishay_KBU.step")


def test_smd_body_from_footprint_name():
    # SOD flat-lead: narrow -> SOD-123F, wide -> SOD-128 (no KiCad dir needed).
    assert resolve_from_footprint("SODFL3516X80N").endswith("/D_SOD-123F.step")
    assert resolve_from_footprint("SODFL5336X130N").endswith("/D_SOD-128.step")
    # MELF size split.
    assert resolve_from_footprint("DIOMELF1911N").endswith("/D_MicroMELF.step")
    assert resolve_from_footprint("DIOMELF5025N").endswith("/D_MELF.step")
    assert resolve_from_footprint("DIODES-INC_POWERDI123").endswith("/D_PowerDI-123.step")


def test_unmapped_footprint_name_is_none():
    assert resolve_from_footprint("IXYS_IXBOD 1-12R..42") is None


@_needs_kicad
def test_qfn_dimension_resolver():
    # CERN QFN body in name is the true body; N may include the thermal pad.
    assert resolve_from_footprint("QFN50P700X700X90-49N-S580").endswith(
        "/Package_DFN_QFN.3dshapes/QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm.step")
    assert "QFN-32-1EP_5x5mm_P0.5mm" in resolve_from_footprint("QFN50P500X500X100-33N-S330")


@_needs_kicad
def test_qfp_dimension_resolver():
    # CERN QFP body in name is the lead-span; KiCad body ≈ span − 2mm; prefer LQFP.
    assert "LQFP-48" in resolve_from_footprint("QFP50P900X900X160-48N")
    r64 = resolve_from_footprint("QFP50P1200X1200X160-64N")
    assert "LQFP-64" in r64 and "10x10mm_P0.5mm" in r64


@_needs_kicad
def test_bga_dimension_resolver():
    # Exact ball count + pitch; pitch disambiguates same-ball-count bodies.
    r256 = resolve_from_footprint("BGA256C100P16X16_1700X1700X155")
    assert "BGA-256_17.0x17.0mm" in r256 and "P1.0mm" in r256
    assert "BGA-324_19.0x19.0mm" in resolve_from_footprint("BGA324C100P18X18_1900X1900X155")
    # KiCad's only BGA-484 is 23x23 P1.0; CERN's is 0.8mm pitch -> no fit.
    assert resolve_from_footprint("BGA484C80P22X22_1900X1900X325") is None


@_needs_kicad
def test_connector_pin_header_socket():
    # Clean grid + standard pitch -> generic PinHeader/PinSocket.
    h = resolve_connector("4 Contacts, Pitch 2.54mm, Single Row Header",
                          pins=4, rows=1, perrow=4, pitch_mm=2.54)
    assert h.endswith("/Connector_PinHeader_2.54mm.3dshapes/PinHeader_1x04_P2.54mm_Vertical.step")
    s = resolve_connector("Dual Row 2.54mm Socket Receptacle",
                          pins=20, rows=2, perrow=10, pitch_mm=2.54)
    assert "PinSocket_2x10_P2.54mm_Vertical" in s


def test_connector_non_standard_pitch_declined():
    # No clean grid / non-standard pitch -> None (proprietary -> drop-folder).
    assert resolve_connector("Mezzanine board-to-board", pins=80) is None
    assert resolve_connector("0.8mm header", pins=10, rows=1, perrow=10, pitch_mm=0.8) is None


@_needs_kicad
def test_connector_dsub():
    r = resolve_connector("Right Angle D-Sub 9 Male Contacts")
    assert r is not None and "DSUB-9_Pins" in r


@pytest.mark.skipif(kicad_footprint_dir() is None,
                    reason="KiCad bundled footprints not installed")
def test_native_centroid_origin_convention():
    # DIP models are pin1-origin: the native footprint's pad centroid is the
    # body center (3.81, 3.81 for DIP-8), so CERN center-origin footprints must
    # offset the model by that much.
    dip = native_centroid("${KICAD10_3DMODEL_DIR}/Package_DIP.3dshapes/DIP-8_W7.62mm.step")
    assert dip is not None
    assert abs(dip[0] - 3.81) < 0.01 and abs(dip[1] - 3.81) < 0.01
    # SOIC models are center-origin: native centroid ~ (0, 0).
    soic = native_centroid(
        "${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/SOIC-8_3.9x4.9mm_P1.27mm.step")
    assert soic is not None and abs(soic[0]) < 0.1 and abs(soic[1]) < 0.1


@_needs_kicad
def test_to_orientation_and_leads():
    v = resolve_model("TO-247", orientation="v", leads=2)
    assert v.endswith("/Package_TO_SOT_THT.3dshapes/TO-247-2_Vertical.step")
    h = resolve_model("TO-220-2", orientation="h", leads=2)
    assert h.endswith("/Package_TO_SOT_THT.3dshapes/TO-220-2_Horizontal_TabUp.step")


@_needs_kicad
def test_to_horizontal_to247_declined():
    # KiCad ships only Vertical TO-247 models; horizontal has no fit.
    assert resolve_model("TO-247", orientation="h", leads=2) is None


def test_smd_sot223():
    assert resolve_model("SOT223").endswith("/Package_TO_SOT_SMD.3dshapes/SOT-223.step")


def test_tht_to92_default():
    assert resolve_model("TO-92").endswith("/Package_TO_SOT_THT.3dshapes/TO-92_Inline.step")


def test_smd_ic_packages():
    assert resolve_model("MSOP8").endswith("/Package_SO.3dshapes/MSOP-8_3x3mm_P0.65mm.step")
    assert resolve_model("SOT353").endswith("/Package_TO_SOT_SMD.3dshapes/SOT-353_SC-70-5.step")
    assert resolve_model("TO-263-5").endswith("/Package_TO_SOT_SMD.3dshapes/TO-263-5_TabPin3.step")


def test_so_dip_ic_packages():
    assert resolve_model("SOIC14").endswith("/Package_SO.3dshapes/SOIC-14_3.9x8.7mm_P1.27mm.step")
    assert resolve_model("TSSOP14").endswith("/Package_SO.3dshapes/TSSOP-14_4.4x5mm_P0.65mm.step")
    assert resolve_model("SSOP16").endswith("/Package_SO.3dshapes/SSOP-16_3.9x4.9mm_P0.635mm.step")
    assert resolve_model("DIP8-300").endswith("/Package_DIP.3dshapes/DIP-8_W7.62mm.step")
    assert resolve_model("DIP16-300").endswith("/Package_DIP.3dshapes/DIP-16_W7.62mm.step")


@_needs_kicad
def test_plain_to220_family():
    v = resolve_model("TO-220", orientation="v", leads=3)
    assert v.endswith("/Package_TO_SOT_THT.3dshapes/TO-220-3_Vertical.step")


def test_xtal_osc_size_token():
    # Standard body-size code embedded in the vendor footprint name.
    assert resolve_from_footprint("XTAL_KYOCERA_CX3225SB").endswith(
        "/Crystal.3dshapes/Crystal_SMD_3225-4Pin_3.2x2.5mm.step")
    assert resolve_from_footprint("XTAL_NDK_NX2016SA").endswith(
        "/Crystal.3dshapes/Crystal_SMD_2016-4Pin_2.0x1.6mm.step")
    assert resolve_from_footprint("OSC_EPSON_SG7050VEN").endswith(
        "/Oscillator.3dshapes/Oscillator_SMD_Abracon_ASV-4Pin_7.0x5.1mm.step")
    assert resolve_from_footprint("OSC_EPSON_SG5032VAN").endswith(
        "/Oscillator.3dshapes/Oscillator_SMD_EuroQuartz_XO53-4Pin_5.0x3.2mm.step")
    assert resolve_from_footprint("OSC_MICREL_2520").endswith(
        "/Oscillator.3dshapes/Oscillator_SMD_SeikoEpson_SG210-4Pin_2.5x2.0mm.step")


def test_xtal_osc_dimensioned_name():
    # Dimensioned name in 0.01mm units; nearest body within tolerance wins.
    assert resolve_from_footprint("XTAL1160X490X430").endswith(
        "/Crystal.3dshapes/Crystal_SMD_HC49-SD.step")
    assert resolve_from_footprint("OSCSC254P500X700X190-6N").endswith(
        "/Oscillator.3dshapes/Oscillator_SMD_Abracon_ASV-4Pin_7.0x5.1mm.step")
    assert resolve_from_footprint("OSCCC320X500X160-4N").endswith(
        "/Oscillator.3dshapes/Oscillator_SMD_EuroQuartz_XO53-4Pin_5.0x3.2mm.step")


def test_xtal_osc_vendor_exact():
    # Vendor series KiCad ships the exact model for, plus HC-49 THT and DIP cans.
    assert resolve_from_footprint("XTAL_EPSON_TSX-3225").endswith(
        "/Crystal_SMD_SeikoEpson_TSX3225-4Pin_3.2x2.5mm.step")
    assert resolve_from_footprint("XTAL_HC-49_U").endswith("/Crystal_HC49-U_Vertical.step")
    assert resolve_from_footprint("OSCDIP14-300_L2080T1320H598-4A").endswith(
        "/Oscillator.3dshapes/Oscillator_DIP-14.step")


def test_xtal_osc_declines():
    # No 3.2x2.5mm oscillator body ships; nearest (2520) is out of tolerance.
    assert resolve_from_footprint("OSC_MICROCHIP_CDFN3225-4LD-PL-1") is None
    # Part-number digits must never be read as a body size code.
    assert resolve_from_footprint("OSC_CRYSTEK_CVCO55CC-1912-2114") is None
    # Bespoke vendor oscillator body without a size code -> drop-folder.
    assert resolve_from_footprint("OSC_SI-TIME_SiT9365-B") is None


@_needs_kicad
def test_metal_can_by_leads():
    # Cans are named <family>-<leads>.step (no orientation); pin 4 clamps to 3.
    assert resolve_model("TO-18", pin_count=3).endswith("/TO-18-3.step")
    assert resolve_model("TO-39", pin_count=2).endswith("/TO-39-2.step")
    assert resolve_model("TO-5", pin_count=4).endswith("/TO-5-3.step")


def test_relay_footprint_exact():
    # Vendor-series relay bodies KiCad ships, by exact CERN footprint name.
    assert resolve_from_footprint("REL_OMRON_G5V-1").endswith(
        "/Relay_THT.3dshapes/Relay_SPDT_Omron_G5V-1.step")
    assert resolve_from_footprint("REL_OMRON_G6K-2F-Y").endswith(
        "/Relay_SMD.3dshapes/Relay_DPDT_Omron_G6K-2F-Y.step")
    assert resolve_from_footprint("REL_FINDER_30.22").endswith(
        "/Relay_THT.3dshapes/Relay_DPDT_Finder_30.22.step")
    assert resolve_from_footprint("REL_TYCO_SCHRACK_RT42XXXX").endswith(
        "/Relay_THT.3dshapes/Relay_DPDT_Schrack-RT2-FormC_RM5mm.step")


def test_relay_same_case_variants():
    # Latching / sibling variants reuse the non-latching series body.
    assert resolve_from_footprint("REL_OMRON_G6SU-2G").endswith(
        "/Relay_SMD.3dshapes/Relay_DPDT_Omron_G6S-2G.step")
    assert resolve_from_footprint("REL_FINDER_40.61").endswith(
        "/Relay_THT.3dshapes/Relay_SPDT_Finder_40.51.step")


def test_relay_unmapped_declines():
    # No bundled body -> None; and REL/RELS names never fall through to the
    # generic package-token scan (the 'SMA' in a Finder socket variant must not
    # resolve to a diode SMA model).
    assert resolve_from_footprint("REL_PANASONIC_TQ2") is None
    assert resolve_from_footprint("REL_TYCO_IMXXXGX") is None
    assert resolve_from_footprint("RELS_FINDER_94.13SMA") is None


def test_fuse_smd_chip_from_footprint_name():
    # Standard SMD chip-fuse size code embedded in the footprint name -> the
    # KiCad metric chip-fuse model (no KiCad dir needed; exact filename map).
    assert resolve_from_footprint("FUSC_AVX_F0402G").endswith(
        "/Fuse.3dshapes/Fuse_0402_1005Metric.step")
    assert resolve_from_footprint("FUSC_AVX_F0603G").endswith(
        "/Fuse.3dshapes/Fuse_0603_1608Metric.step")
    assert resolve_from_footprint("FUSC_BOURNS_SF-1206S").endswith(
        "/Fuse.3dshapes/Fuse_1206_3216Metric.step")
    # resettable chip PTC carries the same body code in its name
    assert resolve_from_footprint("FUSR_LITTELFUSE_1210L").endswith(
        "/Fuse.3dshapes/Fuse_1210_3225Metric.step")


def test_fuse_dimensioned_resettable_name():
    # FUSRC<LL><WW>X<height>N: LL/WW are body L/W in 0.1mm -> nearest chip body.
    assert resolve_from_footprint("FUSRC3216X100N").endswith(
        "/Fuse.3dshapes/Fuse_1206_3216Metric.step")    # 3.2x1.6 == 1206
    assert resolve_from_footprint("FUSRC3226X62N").endswith(
        "/Fuse.3dshapes/Fuse_1210_3225Metric.step")    # 3.2x2.6 ~ 1210
    # 4.6x3.2 (1812) has no chip-fuse model -> decline.
    assert resolve_from_footprint("FUSRC4632X150N") is None


def test_fuse_holder_vendor_exact():
    # Cylinder PCB holders KiCad ships an exact model for.
    assert resolve_from_footprint("FUSH_SCHURTER_0031.7701").endswith(
        "/Fuse.3dshapes/Fuseholder_Schurter_0031.7701.xx.step")
    assert resolve_from_footprint("FUSH_BULGIN_FX0457").endswith(
        "/Fuseholder_Cylinder-5x20mm_Bulgin_FX0457_Horizontal_Closed.step")


def test_fuse_declines():
    # Bare cartridge bodies, big SMD chips, bespoke PTC/holders and arresters
    # have no bundled model. Embedded part-number digit runs must never be read
    # as a body size (the '1206' in PTS120660 is bounded by digits -> rejected),
    # and FUS*/SAR names never fall through to the generic package-token scan.
    assert resolve_from_footprint("FUSE_5X20_GLASS_V") is None
    assert resolve_from_footprint("FUSR_LITTELFUSE_1812L020") is None   # no 1812 model
    assert resolve_from_footprint("FUSR_BUSSMANN_PTS120660V005") is None
    assert resolve_from_footprint("FUSH_KEYSTONE_3576") is None
    assert resolve_from_footprint("SAR_TDK_A81-C90X") is None
    assert resolve_from_footprint("FUSC_LITTELFUSE_466") is None        # TR5 radial
