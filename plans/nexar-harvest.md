# Nexar parameter & datasheet harvest

**Deadline:** Nexar access rides on Dave's Altium subscription, which lapses **~Nov 2026**.
The sweep has to run before then.

## Intent

Fill the parametric tail and datasheet of terra-native parts from Nexar's structured
data, so the library stays sparse but correct: populate what we can match with
confidence and leave the rest honestly blank. Harvested values are folded into the
**generators** (fill-blanks-only), never written into `terra.db` after the build.

Targets, highest value first:

1. Native tables whose tails are thin (MCUs, analog, regulators, transistors).
2. Parts from `plans/cern-harvest-worklist.csv` worth promoting into native tables.
   That list is the useful remnant of the retired CERN import: parts a real lab used.
   Its `native_tables` column marks MPNs terra already carries.

## What Nexar gives us

Confirmed with a live `supSearchMpn` query (2026-06-11): the free **Evaluation** tier
returns both `bestDatasheet.url` and the full parametric `specs` (60+ attributes:
operating temp, supply voltage, RoHS status, memory sizes, pin and interface counts).
The marketing compare-plans table wrongly implies these are Enterprise-only.

- **Quota:** 1000 matched parts/month. Pace the sweep, checkpoint it, and spend the
  quota on parts where structured data is hard to get elsewhere.
- **Access:** the Altium Live login opens the Nexar portal, but the API needs its own
  OAuth app (`client_id`/`client_secret`) created at nexar.com. Endpoint
  `https://api.nexar.com/graphql`, query `supSearchMpn(q, limit)`, filter by
  manufacturer.
- **Gaps:** storage/soldering temperature and a RoHS proof-document link are not in
  the structured data; those columns stay blank.

Where a family's parameters are standardized and Nexar coverage is unproven, reading
the datasheets with agents is the better spend (the ic_logic precedent in
`plans/ic-logic-datasheet-harvest.md`).

## Rules

- **Match or skip.** Record `no-match` / `low-confidence`; never guess.
- **Fill blanks only.** Curated values win. Curated identity columns (`mpn`,
  `description`, `value`, …) are never harvest targets.
- **Writable columns:** `manufacturer_link`, `rohs`, `rohs_document_link`, `package`,
  `temp_operating_min/max`, `temp_storage_min/max`, `temp_soldering`, the
  `datasheet` reference, plus the part type's tail columns from `db/schema/types/`.
  Everything else Nexar returns is dropped.
- **Datasheets:** pull a permanent copy into `datasheets/<mfr>/` during the sweep
  (see `plans/datasheet-storage.md`); the generator points at the local PDF.
- **Normalize units** on the harvest side (e.g. "85 °C" → 85) for numeric columns.

## Field map (Nexar `shortname` → terra column)

Examples validated against a live STM32 result:

```
minoperatingtemperature -> temp_operating_min   maxoperatingtemperature -> temp_operating_max
minsupplyvoltage        -> supply_voltage_min   maxsupplyvoltage        -> supply_voltage_max
rohs                    -> rohs                 case_package            -> package
flashmemorysize         -> flash_size           ramsize                 -> ram_size
eeprommemorysize        -> eeprom_size          corearchitecture        -> core
numberofpins            -> pin_count            numberofi2cchannels     -> i2c_count
numberofusartchannels   -> uart_count           numberoftimers_counters -> timer_count
```

Unmapped attributes are dropped.

## Fallback

Parts Nexar can't match: Altium's Manufacturer Part Search BOM/CSV export, done by
hand. Not built.

## Open

- [ ] Create the Nexar OAuth app.
- [ ] Rank the worklist and native gaps into monthly batches before the quota window
      runs out.
