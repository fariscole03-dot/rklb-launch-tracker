# RKLB Launch Tracker

Maintained by **RICH** (Rocketlab Information Collector & Herald) — an autonomous agent
keeping a complete, sourced log of every Rocket Lab (NASDAQ: RKLB) launch and launch booking,
for launch-timing / revenue-recognition analysis.

## Data store

| File | Contents |
|---|---|
| `data/completed_launches.csv` | One row per flown mission (Electron / HASTE / Neutron) |
| `data/forward_manifest.csv` | One row per announced booking or scheduled future launch |
| `data/run_log.csv` | One row per RICH run |
| `RKLB_Launch_Tracker.xlsx` | Regenerated every run from the CSVs; three formatted tabs. This is the emailed file. |

`scripts/` holds the generators. Rebuild the workbook with:

```
python3 scripts/build_xlsx.py
```

## Conventions

- **Rows are never deleted.** Corrections are made in place and noted in `Notes`.
- **Disclosed vs. estimated figures are never mixed.** Estimates carry a
  `REVENUE BASIS:` / basis note stating the source and a confidence level.
- **Announced timeframes are recorded verbatim.** No projections are invented;
  `Timeframe Change History` is append-only so slippage stays auditable.
- Undisclosed customers are logged as `Undisclosed` with a reasoned inference and
  confidence level in `Notes`.
- Source priority: Rocket Lab primary (newsroom / IR) → SEC EDGAR → FAA/FCC →
  Rocket Lab & Peter Beck social → independent trackers (cross-check only).

## Current state

- **97 launches logged** (88 Electron orbital + 9 HASTE), 2017-05-25 → 2026-09-26.
- **Neutron has not flown** as of 2026-10-12.
- Per-year vehicle counts reconcile exactly to the FY2025 10-K
  (10 in 2023, 16 in 2024, 21 in 2025 incl. 3 HASTE).
