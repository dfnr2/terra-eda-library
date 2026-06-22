# ADI / Linear Technology datasheet worklist

analog.com sits behind Akamai bot protection. Automated fetch (`fetch_adi.py`,
headless Chrome via CDP) returns **HTTP 403** in this environment, and plain
curl gets nothing — so these must be downloaded by hand (browser) and dropped
into the staging dirs below. Once present, the harvest proceeds the same way as
the TI set (`run_320_ti_opamps.py`): extract params → build a generator → file
PDFs into the central store.

URL pattern: `https://www.analog.com/media/en/technical-documentation/data-sheets/<file>.pdf`

## Amplifiers → drop in `staging/adi/` → harvest into `ic_opamp`

| Part | Class | File (`<file>.pdf`) |
|------|-------|---------------------|
| LT1028   | op-amp, ultralow-noise        | lt1028 |
| LT1115   | op-amp, audio low-noise       | lt1115 |
| LT1818   | op-amp, high-speed            | lt1818 |
| LT1812   | op-amp, high-speed            | lt1812 |
| LT1167   | instrumentation amp           | lt1167 |
| LT6018   | op-amp, precision low-noise   | lt6018 |
| LT6016   | op-amp, precision (over-the-top) | lt6016 |
| LTC2057  | op-amp, zero-drift            | ltc2057 |
| LTC2050  | op-amp, zero-drift chopper    | ltc2050 |
| LTC6362  | fully-differential amp        | ltc6362 |
| LTC6363  | fully-differential amp        | ltc6363 |
| AD797    | op-amp, ultralow-noise        | ad797 |
| AD844    | op-amp, current-feedback      | ad844 |
| ADA4528  | op-amp, zero-drift            | ada4528-1 |
| ADA4898  | op-amp, high-speed low-noise  | ada4898-1 |
| ADA4898-2| op-amp, dual high-speed       | ada4898-2 |

## Non-amplifiers → drop in `staging/adi-non-opamp/` → future reference/regulator tables

These are **not** op-amps and do not belong in `ic_opamp`. Parked for a later
voltage-reference / regulator harvest.

| Part | Class | File (`<file>.pdf`) |
|------|-------|---------------------|
| LT3045   | LDO linear regulator      | lt3045 |
| LTC6655  | precision voltage reference | ltc6655 |
| LT1021   | precision voltage reference | lt1021 |
| LT1027   | precision voltage reference | lt1027 |
