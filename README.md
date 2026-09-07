# RKLB Launch Tracker

A sourced log of every Rocket Lab (NASDAQ: RKLB) launch and launch booking, maintained by
**RICH** (Rocketlab Information Collector & Herald) on a Monday/Friday schedule.

## Files

| File | Contents |
| --- | --- |
| `data/completed_launches.csv` | One row per flown mission (Electron, HASTE, Neutron). Master record. |
| `data/forward_manifest.csv` | One row per announced booking or scheduled future launch. Append-only. |
| `data/run_log.csv` | One row per run: what was checked, what changed, what was emailed. |
| `RKLB_Launch_Tracker.xlsx` | Regenerated from the CSVs every run; this is the emailed workbook. |
| `tools/make_xlsx.py` | Rebuilds the workbook from the CSVs (`python3 tools/make_xlsx.py`). |

The CSVs are the master record; the workbook is a rendering of them.

## Data conventions

- **Rows are never deleted.** Corrections are made in place and noted in `Notes`.
- **Disclosed vs. estimated revenue are never mixed.** `Revenue - Disclosed ($)` carries only
  figures explicitly stated by Rocket Lab or in SEC filings. Everything else is in
  `Revenue - Estimated ($)` with the basis stated in `Notes`, and is re-verified at least quarterly.
- **Undisclosed customers** are logged as `Undisclosed`, with any inference, its reasoning and a
  confidence level (high/medium/low) recorded in `Notes` — never promoted into the customer field.
- **`Timeframe Change History`** in the forward manifest is append-only: every announced date or
  timeframe change is recorded with the date it was observed, for revenue-timing analysis.
- **Announced timeframes are recorded verbatim** ("no earlier than H2 2026"). No projections are
  invented; modelling judgment belongs to the reader, not the tracker.

## Sources, in priority order

1. Rocket Lab official newsroom, mission pages and investor relations
2. SEC EDGAR — RKLB 10-Q, 10-K, 8-K and earnings releases
3. FAA Office of Commercial Space Transportation licences and modifications
4. FCC space/experimental filings (useful for identifying undisclosed payloads)
5. Rocket Lab and Peter Beck social media
6. Independent trackers and reputable spaceflight press — for cross-checking only, confirmed
   against a primary source or clearly marked as secondary

Conflicts between sources are noted rather than silently resolved, with Rocket Lab primary
sources and SEC filings preferred.
