# bjt: classic through-hole bipolar transistors

**Date:** 2026-11-25
**Status:** Done — 57 rows (38 small-signal + 19 power); see Results
**Scope:** fill the `bjt` table, which held only two SMD parts (`run_310_cart_harvest.py`),
with the through-hole BJTs that turn up on every schematic: the 2N/PN/MPSA/BC TO-92
types, a few TO-18/TO-39 metal cans, and the TIP/BD/MJE/D44H/2N3055 power parts. No
schema change: the `transistors` fragment already has every column needed.

## Generators

| Generator | Family | Packages | Rows |
|---|---|---|---|
| `run_320_small_signal_th.py` | small-signal | TO-92, TO-18, TO-39 | 38 |
| `run_330_power_th.py` | power | TO-220, TO-247, TO-225, TO-3 | 19 |
| `_bjt.py` | shared `Part` record, row builder, pinout check, writer | | |

Each part is a `Part(...)` line transcribed from its data sheet: Vceo, Ic, Pd (with
`Ta=25C` or `Tc=25C` stated), hFE as the sheet's headline min-max at its Ic, fT (the
guaranteed minimum unless marked `typ`; NULL where the sheet has none), Tj max, and
the lead order. `transistor_type` is `npn`/`pnp`; Darlingtons say so in the
description, keywords and `part_locator` (`bjt-npn-darlington-60v-5a-to220`).

## Sources

Preference order: onsemi, then Central Semiconductor, then Diotec. ST was not needed.

- **onsemi** (`datasheets/onsemi/`): the Fairchild-heritage TO-92 line and all the
  power parts. onsemi keeps two generations of most TO-92 types. The older onsemi
  codes (`G`, `RL1G`, `ZL1G`: `P2N2222AG`, `2N3906G`, `MPSA92G`, `BC557BG` ...) are all
  Obsolete. The Fairchild codes (`BU`, `TA`) are the live ones. Several sheets carry
  both, so each MPN was matched against the sheet's own ordering table.
- **Central** (`datasheets/central/`): used for parts onsemi no longer makes:
  2N5088/2N5089, MPSA56, MPSA92, MPSA13/MPSA14, plus the metal cans 2N2222A, 2N2907A,
  2N2219A and 2N3053. Central's sheets come from `central.aeminc.com/datasheets/`, and
  its parametric search (`my.centralsemi.com/paraSearch/...&rcdPerPage=9999`) gives the
  file names. The ordering code is `<type> PBFREE`, which the sheets give as the
  Pb-free suffix.
- **Diotec** (`datasheets/diotec/`, new directory): BC546B, BC548B/C, BC556B,
  BC557B/C and BC558B. onsemi's current sheets list all of these as discontinued.
  Diotec's BC546...BC549 and BC556...BC559 sheets are dated 2026-03-30.

Data sheets used:

| File | Covers |
|---|---|
| onsemi `2n3904-d`, `pzt3906-d`, `pn2222a-d`, `pn2907a-fsc-d`, `mmbt4401-d`, `2n4403t`, `2n5401-d`, `2n5551t-d`, `pzta06-d`, `pzta42-d` | TO-92 general purpose |
| onsemi `bc550-d`, `bc556bta-d`, `bc337-fsc-d`, `bc327-d`, `bc640-fcs-d` | BC series |
| onsemi `tip31a-d`, `tip41a-d`, `tip120-d`, `tip3055-d`, `mje2955t-d`, `d44h-d`, `bd135-d`, `bd136g-d`, `mje340-d`, `mje350-d`, `2n3055-d` | power |
| Central `2n5088-2n5089`, `mpsa05-mpsa56`, `mpsa92-mpsa93`, `mpsa12-mpsa14`, `2n2221a-2n2222a`, `2n2906-2n2907a`, `2n2219-2n2219a`, `2n3053-2n3053a` | |
| Diotec `bc546-bc549`, `bc556-bc559` | |

Two of these needed care:

- **2N3906:** onsemi's product page for 2N3906BU links `2n3906-d.pdf`. That is the old
  onsemi sheet, and it lists only the obsolete `G` and `RL` codes. Instead the row
  uses `pzt3906-d.pdf` (2N3906/MMBT3906/PZT3906), which lists 2N3906BU.
- **MJE350G:** onsemi has no TO-225 sheet for it. The product page links the 2001
  Fairchild MJE350 sheet (TO-126, no ordering table), so the row uses that sheet. The
  MPN comes from the product page.

## Decisions

### Pinout

TO-92 lead order varies by maker and family, so every row takes its lead order
(`pinout`, pin 1 first) from that maker's sheet. `_bjt.rows()` then reads the stock
`Transistor_BJT` library and checks that order against the pin names of the symbol
the row names, with `extends` resolved. A mismatch stops the generator. This was
tested by giving a BC547 row E-B-C, and the generator rejected it.

| Lead order | Parts | Symbol |
|---|---|---|
| E-B-C | 2N3904, 2N3906, PN2222A, PN2907A, 2N4401/4403, 2N5401/5551, 2N5088/5089, MPSA06/42/56/92, metal cans | per-part where KiCad has one (2N3904, 2N3906, PN2222A, MPSA42, MPSA92, 2N2219), else `Q_NPN_EBC`/`Q_PNP_EBC` |
| E-B-C Darlington | MPSA13, MPSA14 | `Q_NPN_Darlington_EBC` |
| C-B-E | BC546-BC550, BC556-BC559, BC337, BC327 (onsemi and Diotec agree) | BC5xx/BC337/BC327 per-part |
| E-C-B | BC640 (TO-92); BD139/BD140, MJE340/MJE350 (TO-225 style 1) | `Q_PNP_ECB`; BD139/BD140; `Q_NPN_ECB`/`Q_PNP_ECB` |
| B-C-E | TO-220 style 1 (TIP31/32/41/42, TIP12x, MJE3055T/2955T, D44H/D45H); TO-247 TIP3055/2955 | TIP41C/42C, TIP120/122/127, TIP3055G/2955G per-part, else `Q_*_BCE` |
| B-E-C(case) | TO-3 style 1: 2N3055, MJ2955 | 2N3055, MJ2955 |

Pinout mismatches found:

- **P2N2222A vs PN2222A:** the old onsemi P2N2222A is C-B-E, but the Fairchild PN2222A
  is E-B-C. P2N2222AG is Obsolete and was left out. PN2222ABU uses the `PN2222A`
  symbol, which is E-B-C.
- **BC640** is E-C-B. KiCad has no BC640 symbol; the stock BC636 symbol has the same
  pins but the wrong name, so the row uses `Q_PNP_ECB`.
- **2N5401:** the sheet's "-C" suffix is a centre-collector (E-C-B) variant. The
  orderable 2N5401YBU is the standard E-B-C part.
- **PN2907A:** onsemi's PN2907A-FSC sheet draws the leads but doesn't name them. The
  row takes E-B-C from onsemi's own PN2907A/D (TO-92 case 29 style 1). This is the
  one row whose lead order comes from a sibling sheet.
- None of the named per-part symbols disagreed with its maker's pinout.

Some stock symbols carry a default footprint that differs from the row's (BC5xx on
lead-formed parts, TIP3055 on TO-218). The row's `kicad_footprint` governs.

### Packing and footprints

- **onsemi TO-92:** use bulk `BU` (straight leads, 1.27 mm, `TO-92_Inline`) wherever
  onsemi still sells it. Use ammo `TA` (case 135AR, leads formed to 2.40-2.80 mm,
  `TO-92_Inline_Wide`) only where bulk is discontinued: BC549B/C, BC559C and BC640.
  MPSA06 and MPSA42 are sold bulk-only under the bare type number.
- **Diotec:** the standard code ships in ammo with leads formed to 2.54 mm, so these
  rows use `TO-92_Inline_Wide`. Bulk ("BK", 1.27 mm) is on request only.
- **Central:** `PBFREE` is bulk with straight leads (`TO-92_Inline`).
- The description says "(leads formed to 2.54mm)" on every formed-lead row.
- **TO-225** (onsemi case 77) has the TO-126 outline and lead pitch, so it uses
  `TO-126-3_Vertical` (RM 2.28 mm).
- **Other packages:** TO-18 uses `TO-18-3`, TO-39 uses `TO-39-3`, TO-3 uses `TO-3`
  (pad 3 is the case, which is the collector), TO-220 uses `TO-220-3_Vertical` and
  TO-247 uses `TO-247-3_Vertical`.
- **TIP3055G:** the sheet lists this code in both SOT-93 (TO-218) and TO-247, but notes
  that it is moving to TO-247 only, and the product page shows TO-247. The row uses
  TO-247 with the `TIP3055G`/`TIP2955G` symbols.

### SPICE

Plain BJTs set `sim_device` NPN/PNP. They also set `sim_pins` in the sheet's lead order
(`1=E 2=B 3=C` etc.), so the DB value matches what the stock symbol carries. This gives
KiCad's default Gummel-Poon model, as the stock symbols do. Darlingtons leave both
NULL, as their stock symbols do.

### Lifecycle (2026-11-25)

- **Distributors:** Digi-Key returned 403 and Mouser returned 403 or timed out to
  scripted fetches. As the brief allows, lifecycle comes from the makers.
- **onsemi:** taken from the product pages, found through the site search
  (`POST /search-results/search`) or `product.do?id=<MPN>`. Each page's
  orderable-parts table gives the status. Every row here is Active except
  **TIP2955G**: "Last Shipments", stored as `EOL`. It stays in because it is the
  TIP3055's only complement.
- **Where onsemi's sheet and product page disagree,** the newer sheet wins. BC550/D
  Rev. 6 (Feb 2026) marks BC546BTA, BC547BTA, BC548BTA/CTA and BC550CTA
  discontinued, while the product page still showed them Active. They were not used.
- **Central:** a part counts as Active when the parametric search lists it and no PDN
  covers it. Central appends PDNs to its sheets. The 2N2221A and 2N2906 sheets carry
  EOL notices for 2N2221A, 2N2906 and 2N2906A, but not for 2N2222A or 2N2907A.
- **Diotec:** product pages (`diotec.com/en/product/<MPN>.html`) show "Life Cycle
  active" for all seven parts.

## Not added

| Part | Why |
|---|---|
| P2N2222A | onsemi P2N2222AG Obsolete; PN2222ABU covers the type |
| BC639 | onsemi BC63916 is "Active, Not Recommended"; the onsemi BC639 codes are Obsolete. BC640 is in without its complement |
| BC560C | onsemi BC560CTA discontinued (BC556BTA/D), BC560CG Obsolete; Diotec's sheet stops at BC559 |
| TIP125 | onsemi TIP125G Obsolete; Central TIP125 end-of-life (PDN01250, appended to its TIP120 sheet) |
| MJE13005 | onsemi MJE13005G Obsolete; Central MJE13005 also on PDN01250 |
| onsemi BC546B, BC548B/C, BC556B, BC557B/C, BC558B | discontinued at onsemi; taken from Diotec instead |
| onsemi MPSA56, MPSA92, MPSA13/14, 2N5088/89 | all codes Obsolete at onsemi; taken from Central instead |

## Results

- **Rows:** 57 new rows. With the two SMD cart-harvest parts, the `bjt` table has 59.
- **Small-signal, 38 rows:**
  - onsemi TO-92 general purpose: 10
  - onsemi BC series: 11 (BC547B/C, BC549B/C, BC550C, BC559C, BC337-25/-40,
    BC327-25/-40, BC640)
  - Diotec BC series: 7
  - Central TO-92: 6
  - Central metal cans: 4
- **Power, 19 rows:** TO-220 11, TO-247 2, TO-225 4, TO-3 2.
- **Lifecycle:** 56 Active, 1 EOL (TIP2955G).
- **Checks:**
  - every symbol's lead order was checked against its data sheet;
  - every footprint resolves in the stock KiCad 10 library;
  - every data sheet path exists.
- **Build and tests:** `make bjt-generate && make bjt-build` is clean, and
  `uv run pytest tests/ -q` passes 219 tests.
- **Spot checks against the sheets:** BC547BBU, BC549CTA, BC640TA, MPSA13, 2N2222A,
  TIP120G, TIP2955G, BD139G and 2N3055G match on MPN, value, symbol pins, footprint,
  Vceo/Ic/Pd/hFE/fT.

## Follow-ups

- **TIP2955 replacement:** Central's parametric search lists an active TIP2955/TIP3055
  in TO-218, but it links only a line-card summary (LSSGP091), not a full sheet. If
  one turns up, it can replace the EOL TIP2955G.
- **Distributor check:** recheck lifecycle at Digi-Key/Mouser from a browser, since
  scripted fetches were refused.
- **SPICE:** onsemi and Central publish `.model` cards for most of these types. Parking
  them in `spice/<mfr>/` and setting `sim_model_file`/`sim_params` would replace the
  default Gummel-Poon model.
- **Central packing:** tape or ammo codes for Central's TO-92 parts weren't sought;
  bulk `PBFREE` only.
