"""Searchable keywords shared by the capacitors_th generators.

KiCad's chooser matches search terms against a part's name, description and keywords.
The name is the MPN-based unique_id and the description spells capacitance one way
("10µF", with a µ that a typed "uF" does not match), so the keywords carry every
conventional spelling (100pF, 100nF, 0.1uF) plus dielectric, voltage and tolerance.
Same scheme as capacitors_smt/_keywords.py.
"""


def _num(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def capacitance_notations(cap_pf):
    """pF below 1uF, nF from 100pF to below 1uF, uF from 1nF up."""
    out = []
    if cap_pf < 1e6:
        out.append(f"{_num(cap_pf)}pF")
    if 100 <= cap_pf < 1e6:
        out.append(f"{_num(cap_pf / 1e3)}nF")
    if cap_pf >= 1e3:
        out.append(f"{_num(cap_pf / 1e6)}uF")
    return out


def th_keywords(cap_pf, dielectric, voltage, tolerance, *extra):
    """Keywords for a through-hole ceramic. tolerance is the display text ("±5%")."""
    terms = ["capacitor", "mlcc", "ceramic", "through-hole", "radial",
             *capacitance_notations(cap_pf), dielectric, f"{_num(voltage)}V",
             tolerance.replace("±", ""), *extra]
    return ", ".join(terms)
