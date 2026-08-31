# rklb-launch-tracker

Master tracker for every Rocket Lab (NASDAQ: **RKLB**) launch and launch booking, maintained by
**RICH** — Rocketlab Information Collector & Herald.

Purpose: feed a financial model that projects launch timing for revenue recognition by quarter.

## Data store

| File | Contents |
| --- | --- |
| `data/completed_launches.csv` | One row per flown mission (Electron orbital + HASTE suborbital). |
| `data/forward_manifest.csv` | One row per announced booking or scheduled future launch. |
| `data/run_log.csv` | One row per RICH run. |
| `RKLB_Launch_Tracker.xlsx` | Regenerated every run from the CSVs. Three formatted tabs. This is the emailed file. |

**Rows are never deleted.** Corrections are made in place and recorded in the row's `Notes`.
Timeframe changes in the forward manifest are append-only in `Timeframe Change History`.

## Run cadence

- **Monday** — full weekly digest, emailed every week (even a quiet one).
- **Friday** — incremental sweep, emailed only if there is material news.
- **Pre-earnings** — evaluated every run; sent 5–9 days before an announced earnings date,
  once per quarter.

## Sourcing rules

Priority order: Rocket Lab official newsroom / IR → SEC EDGAR (10-Q, 10-K, 8-K) → FAA commercial
space licences → FCC filings → Rocket Lab and Peter Beck social accounts → independent trackers.

Independent trackers are **cross-check only** and are marked as secondary in the `Sources` column.
Estimates are always labelled `est.` with their basis stated, and are never mixed with disclosed
figures. Conflicting sources are noted rather than silently resolved.

### Revenue and cost estimates

Per-mission revenue is essentially never disclosed. Estimates use Rocket Lab's own SEC-disclosed
**revenue per launch** and **cost per launch** period averages:

| Period | Revenue / launch | Cost / launch | Source |
| --- | --- | --- | --- |
| FY2020 | $5.5M | $6.5M | FY2021 10-K |
| FY2021 | $8.1M | $9.2M | FY2021 10-K |
| FY2022 | $6.7M | $7.5M | FY2023 10-K |
| FY2023 | $7.1M | $7.0M | FY2023 10-K |
| FY2024 | $7.8M | $5.7M | FY2025 10-K |
| FY2025 | $8.5M | $4.8M | FY2025 10-K |
| Q1 2026 | $9.3M | $5.4M | Q1 2026 10-Q |
| Q2 2026 | $9.1M | $4.4M | Q2 2026 10-Q |

These are period averages blended across Electron and HASTE, not per-mission prices. Flights before
FY2020 predate the metric's disclosure and are left blank rather than guessed.

## Regenerating the workbook

```bash
pip install openpyxl
python3 scripts/make_xlsx.py
```

`scripts/parse_wikitext.py` and `scripts/backfill_build.py` are the one-off historical backfill
tools, kept for provenance and reproducibility.
