# rklb-launch-tracker

A sourced log of every Rocket Lab (NASDAQ: **RKLB**) launch and launch booking, maintained
by **RICH** — Rocketlab Information Collector & Herald.

The tracker exists to feed a financial model that projects launch timing for revenue
recognition by quarter. It **logs and organises**; it does not model. No launch-date
projections are made beyond what Rocket Lab has announced.

## Contents

| Path | What it is |
|---|---|
| `data/completed_launches.csv` | One row per flown mission. Append-only. |
| `data/forward_manifest.csv` | One row per announced booking / scheduled future launch. Append-only. |
| `data/run_log.csv` | One row per RICH run. |
| `data/METHODOLOGY.md` | Sourcing rules, revenue-estimate bases, known limitations, anomalies. **Read this before using the revenue columns.** |
| `RKLB_Launch_Tracker.xlsx` | Three formatted tabs, regenerated from the CSVs each run. This is the emailed file. |
| `build_tracker.py` | Regenerates the workbook from the CSVs. |

## Current state (as of 2026-09-21)

- **96 flights** flown in Rocket Lab's sequential series, numbered 1–96 with no gaps:
  **87 orbital Electron** + **9 suborbital HASTE**.
- **92 successes, 4 failures** (flights 1, 13, 20, 41).
- **Neutron has not yet flown** — company guidance is Q4 2026 from LC-3, Wallops.
- **16 forward-manifest rows**, including the record $266M USSF RSLP suborbital award.

## Regenerating the workbook

```bash
pip install -r requirements.txt
python3 build_tracker.py
```

The CSVs are the source of truth. Never delete rows — correct in place and note the
correction, so that timing history stays auditable.
