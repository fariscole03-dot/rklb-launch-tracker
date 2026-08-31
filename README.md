# RKLB Launch Tracker

Maintained by **RICH** (Rocketlab Information Collector & Herald) — an autonomous agent that keeps a
complete, sourced log of every Rocket Lab (NASDAQ: RKLB) launch and launch booking, for use as the
input layer to a financial model projecting launch timing and revenue recognition by quarter.

## Files

| File | Contents |
| --- | --- |
| `data/completed_launches.csv` | One row per flown mission (Electron, HASTE, Neutron). Append-only; corrections made in place and noted. |
| `data/forward_manifest.csv` | One row per announced booking or scheduled future launch, with append-only `Timeframe Change History`. |
| `data/run_log.csv` | One row per run: what was checked, what changed, what was emailed. |
| `RKLB_Launch_Tracker.xlsx` | Regenerated from the CSVs every run. Three formatted tabs; this is the file that gets emailed. |
| `scripts/build_workbook.py` | Rebuilds the workbook from the CSVs. Run after every CSV change. |
| `scripts/backfill_seed.py` | Provenance for the initial 2026-08-31 historical backfill only. Not used by later runs. |

## Regenerating the workbook

```bash
pip install openpyxl
python3 scripts/build_workbook.py
```

## Data conventions

- **Revenue — Disclosed** holds only figures explicitly stated by Rocket Lab or in filings. Any other
  figure lives in **Revenue — Estimated** and always carries its basis in `Notes`.
- **Customer Disclosure** is `Disclosed` or `Undisclosed`. Undisclosed rows carry a best inference in
  `Notes` with an explicit confidence level (high / medium / low).
- **Dedicated / Rideshare** is assigned as `Rideshare` where a mission carried payloads for more than
  one distinct customer, `Dedicated` otherwise.
- **Sources** marked *(secondary, cross-check backbone)* have not yet been confirmed line-by-line
  against a Rocket Lab press release or SEC filing. These are being converted to primary sources
  incrementally on subsequent runs.
- Rows are never deleted. Corrections are made in place and recorded in `Notes`.

## Current pricing bases for estimates

Re-verified at least quarterly; last verified **2026-08-31**.

| Vehicle | Basis |
| --- | --- |
| Electron 2017–2019 | ~$5.5M — RKLB states Electron came to market at $5–6M/mission |
| Electron 2020–2022 | ~$7.0M — interpolation between introductory pricing and published mission cost |
| Electron 2023–2024 | ~$7.5M — Rocket Lab published Electron mission cost (~300 kg to LEO) |
| Electron 2025–2026 | ~$8.5M — CFO Adam Spice, Q1 FY26 call: commercial Electron backlog ASP |
| HASTE | ~$9.5M — derived from the disclosed $190M / 20-flight MACH-TB 2.0 block buy (2026-03-18) |
| Neutron | $50–55M ASP — stated by RKLB CFO; $52.5M midpoint used for estimates |
