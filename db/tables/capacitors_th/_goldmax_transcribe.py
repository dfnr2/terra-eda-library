#!/usr/bin/env python3
"""Transcribe the Kemet Goldmax capacitance-range waterfall tables to goldmax_catalog.json.

Reads datasheets/kemet/KEM_C1049_GOLDMAX_C0G.pdf and KEM_C1093_GOLDMAX_X8L.pdf with
pdftotext -layout, maps each capacitance-code cell to its voltage column by position, and
cross-checks every code against its row's capacitance label (aborts on a mismatch). Run
from anywhere; rewrites the catalog next to this script. The catalog holds availability per
size group (cap x voltage, shoulder-bend flag); run_310_kemet_goldmax.py expands it into
orderable MPNs.
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "goldmax_catalog.json"

PDFS = {
    "C0G": str(ROOT / "datasheets/kemet/KEM_C1049_GOLDMAX_C0G.pdf"),
    "X8L": str(ROOT / "datasheets/kemet/KEM_C1093_GOLDMAX_X8L.pdf"),
}
VOLT = {"3": 25, "5": 50, "1": 100, "2": 200, "A": 250}


def eia_pf(code):
    sig, exp = int(code[:2]), int(code[2])
    return sig * 0.1 if exp == 9 else sig * 10 ** exp


def label_pf(num, unit):
    return float(num) * (1 if unit == "pF" else 1e6)


groups = []
for diel, pdf in PDFS.items():
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    cur = None
    cols = None
    for line in text.splitlines():
        m = re.search(r"Table 1([A-F])", line)
        if m:
            cur = None
            cols = None
            pending = m.group(1)
            continue
        if cur is None and re.search(r"C3\d\d(, C3\d\d)+.*Style/Size|C3\d\d, C3\d\d Style/Size", line):
            styles = re.findall(r"C(3\d\d)", line.split("Style/Size")[0])
            cur = {"dielectric": diel, "table": pending, "styles": styles, "rows": {}}
            groups.append(cur)
            continue
        if cur is None:
            continue
        if "Voltage Code" in line:
            cols = [(mm.start(), mm.group()) for mm in re.finditer(r"(?<=\s)[0-9A](?=\s|$)", line.split("Voltage Code", 1)[1])]
            base = line.index("Voltage Code") + len("Voltage Code")
            cols = [(base + o, c) for o, c in cols]
            continue
        m = re.match(r"\s*([\d.]+)\s*(pF|µF)\s+(.*)$", line)
        if not m or not cols:
            continue
        lab_pf = label_pf(m.group(1), m.group(2))
        pre = len(line) - len(m.group(3))
        rest = re.sub(r"[A-Z] = ±[\d.]+(pF|%)", lambda s: " " * len(s.group()), m.group(3))
        for cm in re.finditer(r"(?<![\d.])(\d{3})(\*?)(?![\d.%])", rest):
            code, star = cm.group(1), bool(cm.group(2))
            pos = pre + cm.start()
            vcode = min(cols, key=lambda c: abs(c[0] - pos))[1]
            if abs(eia_pf(code) - lab_pf) > 1e-6 * max(lab_pf, 1) + 1e-9:
                sys.exit(f"{diel} {cur['table']}: code {code} != label {m.group(1)}{m.group(2)}")
            cur["rows"].setdefault(code, {})[vcode] = star

merged = {}
for g in groups:
    k = (g["dielectric"], g["table"])
    if k in merged:
        for code, vs in g["rows"].items():
            merged[k]["rows"].setdefault(code, {}).update(vs)
    else:
        merged[k] = g
groups = list(merged.values())
out = []
for g in groups:
    caps = []
    for code, vs in g["rows"].items():
        caps.append({"code": code, "pf": round(eia_pf(code), 3),
                     "v": {VOLT[k]: ("shoulder" if s else "") for k, s in vs.items()}})
    caps.sort(key=lambda c: (c["pf"], c["code"]))
    out.append({"dielectric": g["dielectric"], "table": g["table"], "styles": g["styles"], "caps": caps})
    print(g["dielectric"], g["table"], g["styles"], len(caps), "caps,",
          sum(len(c["v"]) for c in caps), "cap-voltage cells")
NL = chr(10)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("[" + NL)
    for gi, g in enumerate(out):
        head = json.dumps({k: g[k] for k in ("dielectric", "table", "styles")}, separators=(",", ":"))[:-1]
        f.write(head + ',"caps":[' + NL)
        f.write(("," + NL).join(" " + json.dumps(c, separators=(",", ":")) for c in g["caps"]))
        f.write(NL + "]}" + ("," if gi < len(out) - 1 else "") + NL)
    f.write("]" + NL)
print("wrote", OUT)
