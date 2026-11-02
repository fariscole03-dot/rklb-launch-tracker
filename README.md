# RKLB Launch Tracker

Maintained by **RICH** (Rocketlab Information Collector & Herald) — an autonomous agent that keeps a
complete, sourced log of every Rocket Lab (NASDAQ: **RKLB**) launch and launch booking, for use as the
input layer to a financial model projecting launch timing and revenue recognition by quarter.

## Files

| File | Contents |
| --- | --- |
| `data/completed_launches.csv` | One row per flown mission (Electron, HASTE, Neutron) |
| `data/forward_manifest.csv` | One row per announced booking / scheduled future launch |
| `data/run_log.csv` | One row per RICH run |
| `RKLB_Launch_Tracker.xlsx` | Regenerated from the CSVs every run; three formatted tabs. This is the emailed file. |
| `scripts/generate_workbook.py` | Rebuilds the workbook from the CSVs |

Regenerate the workbook after editing any CSV:

```bash
/usr/local/bin/python3.13 scripts/generate_workbook.py
```

(`openpyxl` is installed under Python 3.13, not the default `python3`.)

## Source priority

1. Rocket Lab official — newsroom/press releases, mission pages, investor relations
2. **SEC EDGAR** — 10-Q, 10-K, 8-K, earnings releases (backlog, launch counts, revenue disclosures)
3. FAA Office of Commercial Space Transportation — launch licences and modifications
4. FCC space/experimental filings — useful for identifying undisclosed payloads
5. Rocket Lab and Peter Beck social media
6. Independent trackers (Wikipedia Electron launch list, spaceflight press) — **cross-check only**,
   confirmed against primary sources or clearly marked secondary

`rocketlabcorp.com` and `investors.rocketlabcorp.com` block direct automated fetches (HTTP 403). Rocket Lab
primary material is therefore read via its 8-K exhibits on SEC EDGAR and its GlobeNewswire distribution,
both of which carry the company's own press-release text.

## Data conventions

- **Dates** are ISO `YYYY-MM-DD` (UTC), with launch time appended as `HH:MM` where known. In the
  workbook, `Launch Date (UTC)` is a real Excel datetime and `Flight #` a real integer.
- **Flight #** follows Rocket Lab's own sequential numbering, which is a single series shared by
  Electron and HASTE. The series is contiguous with no gaps: HASTE occupies the numbers missing from
  the orbital list.
- **Customer Disclosure** is `Disclosed` or `Undisclosed`. Where undisclosed, `Notes` carries an
  inference with explicit confidence (high/medium/low) and the reasoning behind it.
- **Dedicated / Rideshare** is inferred: a manifest with more than one distinct customer is recorded
  as `Rideshare`, otherwise `Dedicated`.
- **Recovery** uses `None attempted` / `Attempted-recovered` / `Attempted-lost`. Two nuances are
  recorded in `Notes` rather than flattened away: flights 10 and 11 were guided controlled re-entry
  tests with no recovery attempted, and flights 26 and 32 attempted mid-air helicopter capture which
  was not completed but whose boosters were then recovered from the ocean.
- **Revenue — Disclosed ($)** holds only figures explicitly stated by Rocket Lab or in a filing.
  Rocket Lab does not disclose per-mission revenue, so this column is empty for all flown missions.
- **Revenue — Estimated ($)** and **Direct Mission Costs ($)** use Rocket Lab's own SEC-disclosed
  *average revenue per launch* and *cost per launch* for the launch year. This is a blended
  Electron+HASTE average transaction price, not a mission-specific or list price, and every row says
  so in `Notes`.

  | Year | Revenue/launch | Cost/launch | Source |
  | --- | --- | --- | --- |
  | 2020 | $5.5M | $6.5M | FY2022 10-K |
  | 2021 | $8.1M | $9.2M | FY2022 10-K |
  | 2022 | $6.7M | $7.5M | FY2022 10-K |
  | 2023 | $7.1M | $7.0M | FY2025 10-K |
  | 2024 | $7.8M | $5.7M | FY2025 10-K |
  | 2025 | $8.5M | $4.8M | FY2025 10-K |
  | H1 2026 | $9.2M | $4.9M | Q2-2026 10-Q |

  Flights 1–10 (2017–2019) carry no estimate: Rocket Lab first disclosed this metric for FY2020.
  Pricing is re-verified at least quarterly and never silently reused once stale.
- **Announced Timeframe** in the forward manifest is recorded verbatim as stated ("no earlier than
  H2 2026", "2028 through 2031"). RICH records only what has been announced and makes no launch-date
  projections of its own.
- **Timeframe Change History** is append-only. Every date or timeframe change is logged with the date
  RICH observed it, because slippage is the thing that moves revenue between quarters.
- Rows are **never deleted**. Corrections are made in place and the correction is noted.

## Verification

The backfill was reconciled against primary sources rather than taken on trust. Launch counts tie
exactly to RKLB's filings — 16 launches in 2024 and 21 in 2025 (FY2025 10-K), 12 in H1 2026 and 10 in
H1 2025 (Q2-2026 10-Q), 10 in 2023 (FY2023 10-K) — and the 98-flight total, the 89 orbital / 9 HASTE
split, the 85 success / 4 failure split and the per-site totals (LC-1A 44, LC-1B 41, LC-2 13) all tie
to Rocket Lab's own "98th Electron mission" release of 2026-10-23.
