"""Searchable keywords shared by the capacitors_smt generators.

KiCad's chooser matches search terms against a part's name, description and
keywords. The name is the MPN-based unique_id, and the description spells
capacitance one way ("100nF"), so the keywords carry every common notation
(100nF, 0.1uF, 100000pF) along with the dielectric, voltage and case size.
"""


def _num(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def capacitance_notations(cap_pf):
    """Each conventional spelling of a capacitance: pF below 1uF, nF from 100pF to
    below 1uF, uF from 1nF up."""
    out = []
    if cap_pf < 1e6:
        out.append(f"{_num(cap_pf)}pF")
    if 100 <= cap_pf < 1e6:
        out.append(f"{_num(cap_pf / 1e3)}nF")
    if cap_pf >= 1e3:
        out.append(f"{_num(cap_pf / 1e6)}uF")
    return out


def cap_keywords(cap_pf, dielectric, voltage, case_size):
    terms = ["passive", "capacitor", "mlcc", *capacitance_notations(cap_pf),
             dielectric, f"{_num(voltage)}V", case_size]
    return ", ".join(terms)
