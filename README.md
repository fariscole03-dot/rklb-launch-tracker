# RKLB Launch Tracker

A complete, sourced log of every Rocket Lab (NASDAQ: RKLB) launch and launch booking,
maintained by **RICH** (Rocketlab Information Collector & Herald).

Purpose: feed a financial model that projects launch timing for revenue recognition by quarter.

## Files

| File | Contents |
|---|---|
| `data/completed_launches.csv` | One row per flown mission (Electron orbital + HASTE suborbital) |
| `data/forward_manifest.csv` | One row per announced booking / scheduled future launch |
| `data/run_log.csv` | One row per RICH run |
| `RKLB_Launch_Tracker.xlsx` | Regenerated every run from the CSVs; three formatted tabs. This is the emailed file. |
| `scripts/` | Generators (`build_completed.py`, `build_manifest.py`, `build_workbook.py`) |

The CSVs are the source of truth. The workbook is a derived artifact — never edit it directly.

```bash
python3 scripts/build_completed.py parsed.json   # completed launches
python3 scripts/build_manifest.py                # forward manifest
python3 scripts/build_workbook.py                # regenerate the xlsx
```

## Data conventions

- **Rows are never deleted.** Corrections are made in place and recorded in the row's Notes.
- **Estimates are always labelled `est.`** with their basis stated, and are never presented as
  disclosed figures. Only figures explicitly stated by Rocket Lab or in SEC filings go in the
  `Disclosed` columns.
- **Undisclosed customers** are logged as `Undisclosed`, with any inference, its reasoning and a
  confidence level (high/medium/low) in Notes.
- **`Announced Timeframe` is recorded verbatim** as stated by the source ("no earlier than H2 2026").
  No projections are invented — the model owner makes all timing decisions.
- **`Timeframe Change History` is append-only**, each entry carrying the date the change was
  observed. This is the critical field for revenue-timing analysis.

### Reading `forward_manifest.csv` — before you sum anything

`Number of Launches in booking` is the booking size **as announced**, not a count of remaining
unflown launches. Tranches marked `Booked - partially flown` include missions that have since
flown, so summing the column yields **total contracted, not backlog remaining**. Program-level
reconciliations live in each row's Notes. The file enumerates only *publicly itemised* bookings,
so it totals less than Rocket Lab's company-wide manifest figure.

### Revenue estimate basis

Per-mission estimates use disclosed Launch Services revenue divided by the disclosed launch-mission
count for the same period:

| Period | Launch services revenue | Missions | Est. per mission |
|---|---|---|---|
| FY2021 | $39.0M | 6 | $6.50M |
| FY2022 | $60.7M | 9 | $6.74M |
| FY2023 | $71.9M | 10 | $7.19M |
| FY2024 | $125.3M | 16 | $7.83M |
| FY2025 | $199.0M | 21 | $9.48M |
| H1 2026 | $108.249M | 12 | $9.02M |

2017–2020 predate segment disclosure and fall back to contemporaneous Electron list price
(**low confidence**). Q3 2026 revenue was not yet reported at the last run, so Q3 2026 missions
carry the H1 2026 basis.

**Validation:** launch counts parsed from the launch list match Rocket Lab's own disclosed
"launch missions" counts exactly for every year with a filing (2021=6, 2022=9, 2023=10,
2024=16, 2025=21). This also confirms HASTE missions count toward launch-services revenue.

## Sources, in priority order

1. Rocket Lab official site — newsroom, missions pages, investor relations
2. SEC EDGAR — RKLB 10-Q, 10-K, 8-K, earnings releases
3. FAA Office of Commercial Space Transportation — launch licences and modifications
4. FCC space/experimental filings — for identifying undisclosed payloads
5. Rocket Lab and Peter Beck social media
6. Independent trackers (Wikipedia's Electron launch list, spaceflight press) — **cross-check only**,
   confirmed against primary sources or clearly marked as secondary

Where sources conflict, Rocket Lab primary sources and SEC filings win, and the conflict is noted
rather than silently resolved.
