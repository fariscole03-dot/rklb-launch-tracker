# RKLB Launch Tracker

A complete, sourced log of every Rocket Lab (NASDAQ: **RKLB**) launch and launch booking,
maintained by **RICH** (Rocketlab Information Collector & Herald).

Purpose: feed a financial model that projects launch timing for revenue recognition by quarter.

## Files

| File | Contents |
|---|---|
| `data/completed_launches.csv` | One row per flown mission (Electron orbital, HASTE suborbital, Neutron when it flies) |
| `data/forward_manifest.csv` | One row per announced booking **or** scheduled future launch — see *Row Type* below |
| `data/run_log.csv` | One row per RICH run: what was checked, what changed, what was unreachable |
| `RKLB_Launch_Tracker.xlsx` | Regenerated every run from the CSVs; three formatted tabs. This is the emailed file. |
| `scripts/build_workbook.py` | Rebuilds the workbook from the CSVs |
| `scripts/backfill/` | The one-off scripts used for the 2026-09-28 historical backfill (kept for provenance) |

## Reading `forward_manifest.csv` — important

The file deliberately mixes two granularities, distinguished by the **`Row Type`** column:

- `Booking (contract-level)` — an announced contract, e.g. "10 additional Synspective launches".
- `Scheduled launch (manifest-level)` — a single identified upcoming launch slot.
- `Programme status` — status of a vehicle programme (currently Neutron's maiden flight).

**Summing all rows will double-count.** Filter on `Row Type` first.

## Conventions

- **Dates** are ISO (`YYYY-MM-DD`) and UTC. Partial dates (`2026-05`) mean only month precision is sourced.
- **`Announced Timeframe`** is recorded *verbatim* as announced ("no earlier than 2026"). RICH never invents projections.
- **`Timeframe Change History`** is append-only: every timeframe change with the date RICH observed it.
- **Disclosed vs estimated money** is never mixed. `Revenue - Disclosed ($)` / `Contract Value - Disclosed ($)`
  hold only figures explicitly stated by Rocket Lab, in SEC filings, or by the contracting agency.
  Every `... - Estimated ($)` figure states its basis and a confidence level in `Notes`.
- **Undisclosed customers** are logged as `Undisclosed`, with a reasoned inference and confidence in `Notes`,
  prefixed `INFERENCE:`.
- **Rows are never deleted.** Corrections are made in place and noted.

## Source priority

1. Rocket Lab official (newsroom, mission pages, investor relations)
2. SEC EDGAR — RKLB 10-Q / 10-K / 8-K
3. FAA Office of Commercial Space Transportation licences
4. FCC space/experimental filings
5. Rocket Lab / Peter Beck social media
6. Independent trackers (Wikipedia Electron launch list, spaceflight press) — **cross-check only**, marked secondary

## Rebuilding the workbook

```bash
pip install openpyxl
python3 scripts/build_workbook.py
```

## Delivery note (2026-09-28)

The Gmail connector requires attachment bytes inline as base64. The workbook (~42KB, ~57k base64
characters) exceeds what can be reproduced into a tool call with guaranteed byte-fidelity, so RICH
delivers it by repo link rather than risk emailing a corrupted file. The workbook is still
regenerated and committed every run. If an emailed attachment is required, the practical fix is to
write the workbook to Google Drive and email the Drive link.
