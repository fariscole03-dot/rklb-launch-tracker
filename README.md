# RKLB Launch Tracker

A complete, sourced log of every Rocket Lab (NASDAQ: **RKLB**) launch and launch booking,
maintained by **RICH** (Rocketlab Information Collector & Herald).

The tracker exists to support launch-timing analysis for revenue recognition by quarter.

## Files

| File | Contents |
|---|---|
| `data/completed_launches.csv` | One row per flown mission (Electron, HASTE, Neutron). Source of truth. |
| `data/forward_manifest.csv` | One row per announced booking / scheduled future launch. Source of truth. |
| `data/run_log.csv` | One row per RICH run: what changed, what was emailed, what was unreachable. |
| `RKLB_Launch_Tracker.xlsx` | Regenerated every run from the CSVs. Three formatted tabs. This is the emailed file. |
| `scripts/build_workbook.py` | Rebuilds the workbook from the CSVs (`python3 scripts/build_workbook.py`). |

## Ground rules

- **Rows are never deleted.** Corrections are made in place and noted in the row's `Notes`.
- **Disclosed and estimated figures are never mixed.** Estimates live only in the
  `... - Estimated ($)` columns and always carry their basis and a confidence level in `Notes`.
- **Undisclosed customers** are logged as `Undisclosed` even when independent trackers name a
  likely customer; the inference, its basis and its confidence go in `Notes`. Rocket Lab's own
  disclosure governs, not third-party attribution.
- **Announced timeframes are recorded verbatim.** No projections are invented.
  `Timeframe Change History` in the manifest is append-only, so slippage stays visible.
- **Source priority:** Rocket Lab official → SEC EDGAR → FAA/FCC → Rocket Lab & Peter Beck
  social → independent trackers (cross-check only, marked as secondary).

## Flight numbering

Rocket Lab's sequential flight numbers cover the whole Electron family: orbital Electron **and**
suborbital HASTE share one series. As of 2026-09-11 that series runs to **95** flights =
86 orbital Electron + 9 HASTE, which is why HASTE occupies the gaps (38, 55, 57, 71, 72, 75, 82,
86, 89) in the orbital sequence.

## Known gaps

Tracked in `data/run_log.csv` per run. Open items at the 2026-09-14 backfill:

- `rocketlabcorp.com` / `investors.rocketlabcorp.com` return HTTP 403 (Cloudflare bot challenge)
  to automated fetches; GlobeNewswire copies of the same Rocket Lab wire releases were used
  instead. Retry each run.
- Per-launch revenue estimates for **2017–2022** rest on era-approximate secondary pricing and
  are flagged **LOW confidence** pending verification against Rocket Lab disclosures.
- `Contract Announcement Date` is unpopulated for most completed launches, and for several
  forward-manifest rows, pending per-mission contract backfill.
