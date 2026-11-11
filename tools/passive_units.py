#!/usr/bin/env python3
"""Display values and SPICE parameters for passives (R, C, L).

Schematic `value` strings carry the unit sign (10kΩ, 4.7µF, 100nF, 22µH) so a part reads
correctly on the sheet. The simulator must not depend on parsing that text: KiCad reads
the Value field for R/C/L when `Sim.Params` is empty, and sign handling there is not
something to rely on. Generators therefore also write `sim_params` (`r=10k`, `c=4.7u`,
`l=22u`), built here from the same number.

SPICE notes: mega is `Meg` (a bare `M` or `m` means milli in SPICE), micro is `u`.
Zero-ohm jumpers become `r=1u` because ngspice rejects a zero-valued resistor.
"""
import re

# prefix -> exponent, for parsing generator strings such as "4.7u", "10k", "1.02M"
_PARSE = {"": 0, "f": -15, "p": -12, "n": -9, "u": -6, "µ": -6, "μ": -6, "m": -3,
          "k": 3, "K": 3, "M": 6, "Meg": 6, "meg": 6, "G": 9}
# (exponent, display prefix, spice prefix), widest first
_SCALES = [(9, "G", "G"), (6, "M", "Meg"), (3, "k", "k"), (0, "", ""),
           (-3, "m", "m"), (-6, "µ", "u"), (-9, "n", "n"), (-12, "p", "p"), (-15, "f", "f")]
_UNIT_RE = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*(Meg|meg|[fpnuµμmkKMG]?)\s*(?:Ω|ohm|F|H|R)?\s*$")
_KEY = {"R": "r", "C": "c", "L": "l"}


def parse_si(text):
    """'4.7u' / '10kΩ' / '100nF' / '1.02MΩ' -> float in base units (ohm, farad, henry)."""
    m = _UNIT_RE.match(str(text))
    if not m:
        raise ValueError(f"cannot parse passive value {text!r}")
    return float(m.group(1)) * 10.0 ** _PARSE[m.group(2)]


def _mantissa(x):
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return s or "0"


def _scaled(value, skip=()):
    """Return (mantissa string, display prefix, spice prefix) with mantissa in [1, 1000).

    `skip` lists exponents to pass over (capacitors skip milli, so 10000µF stays 10000µF).
    """
    if value == 0:
        return "0", "", ""
    allowed = [sc for sc in _SCALES if sc[0] not in skip]
    for exp, disp, spice in allowed:
        if value >= 10.0 ** exp * 0.9995:
            return _mantissa(value / 10.0 ** exp), disp, spice
    exp, disp, spice = allowed[-1]
    return _mantissa(value / 10.0 ** exp), disp, spice


def display(value, unit):
    """Number in base units -> '4.7µF', '10kΩ', '22µH'. unit is 'Ω', 'F' or 'H'."""
    skip = (9, 6, 3, -3, -15) if unit == "F" else (-15,)
    mant, disp, _ = _scaled(value, skip)
    return f"{mant}{disp}{unit}"


def spice(value):
    """Number in base units -> SPICE literal, e.g. 4.7e-6 -> '4.7u', 1.02e6 -> '1.02Meg'."""
    mant, _, sp = _scaled(value, (-15,))
    return f"{mant}{sp}"


def unit_value(text, unit):
    """Generator string ('1u', '10kΩ', '0.5p') -> schematic value with the unit sign."""
    return display(parse_si(text), unit)


def sim_params(device, text):
    """Generator string -> 'r=10k' / 'c=4.7u' / 'l=22u' for Sim.Params."""
    v = parse_si(text)
    if device == "R" and v == 0:
        v = 1e-6
    return f"{_KEY[device]}={spice(v)}"


if __name__ == "__main__":
    assert unit_value("0.5p", "F") == "0.5pF"
    assert unit_value("1u", "F") == "1µF"
    assert unit_value("100n", "F") == "100nF"
    assert unit_value("1.1n", "F") == "1.1nF"
    assert unit_value("10kΩ", "Ω") == "10kΩ"
    assert unit_value("1.02MΩ", "Ω") == "1.02MΩ"
    assert unit_value("9mΩ", "Ω") == "9mΩ"
    assert unit_value("910µF", "F") == "910µF"
    assert unit_value("1000u", "F") == "1000µF"
    assert unit_value("10000µF", "F") == "10000µF"
    assert sim_params("R", "4.7MΩ") == "r=4.7Meg"
    assert sim_params("R", "9mΩ") == "r=9m"
    assert sim_params("R", "0Ω") == "r=1u"
    assert sim_params("C", "0.5p") == "c=0.5p"
    assert sim_params("C", "910µF") == "c=910u"
    assert sim_params("L", "22µH") == "l=22u"
    print("ok")
