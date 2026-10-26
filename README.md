# RKLB Launch Tracker

A complete, sourced log of every Rocket Lab (NASDAQ: RKLB) launch and launch booking,
maintained by **RICH** (Rocketlab Information Collector & Herald).

Purpose: feed a financial model that projects launch timing for revenue recognition by quarter.

## Files

| File | Contents |
|---|---|
| `data/completed_launches.csv` | One row per flown mission (Electron, HASTE, Neutron) |
| `data/forward_manifest.csv` | One row per announced booking / scheduled future launch |
| `data/run_log.csv` | One row per RICH run |
| `RKLB_Launch_Tracker.xlsx` | Formatted three-tab workbook, regenerated every run from the CSVs |

The CSVs are the master record. The workbook is always rebuilt from them and is the file emailed out.

## Regenerating

```bash
/usr/bin/python3.13 scripts/build_tracker.py
```

`scripts/launch_data.py` holds the dataset (edit there, never in the CSVs directly).
`scripts/build_tracker.py` writes the CSVs, builds the workbook, and runs integrity checks that
reconcile the flight log against Rocket Lab's own published milestone counts.

Note: this environment's `python3` is 3.11 and lacks `openpyxl`; use `/usr/bin/python3.13`.

## Conventions

- **Never delete rows.** Corrections are made in place and noted in the row's `Notes`.
- **Dates are UTC.** New Zealand launches are UTC+12/13, so secondary sources sometimes show the
  next local day; UTC is authoritative here.
- **Estimates are always labelled `est.`** with their basis in `Notes`, and are never mixed with
  disclosed figures. Disclosed figures come only from Rocket Lab or SEC filings.
- **Undisclosed customers** are logged as `Undisclosed`, with any inference, its reasoning and a
  confidence level (high/medium/low) in `Notes`.
- **`Timeframe Change History`** in the forward manifest is append-only — every date or timeframe
  change is recorded with the date RICH observed it. This is the critical field for revenue timing.
- **Source conflicts** are recorded rather than silently resolved. Rocket Lab primary sources and
  SEC filings win; the conflict is still noted.

## Source priority

1. Rocket Lab official site — newsroom, mission pages, investor relations
2. SEC EDGAR — 10-Q, 10-K, 8-K, earnings releases
3. FAA Office of Commercial Space Transportation — licences and modifications
4. FCC space/experimental filings
5. Rocket Lab and Peter Beck social media
6. Independent trackers (Wikipedia's Electron list, spaceflight press) — cross-checking only
