# RKLB Launch Tracker

A sourced log of every Rocket Lab (NASDAQ: RKLB) launch and launch booking,
maintained by **RICH** (Rocketlab Information Collector & Herald).

The tracker exists to support launch-timing analysis for revenue recognition by
quarter. It **logs and organises** — it does not project launch dates. Every
forward-looking timeframe is recorded verbatim as announced.

## Files

| File | Contents |
|---|---|
| `data/completed_launches.csv` | One row per flown mission (Electron, HASTE, Neutron) |
| `data/forward_manifest.csv` | One row per announced booking or scheduled future launch |
| `data/run_log.csv` | One row per RICH run |
| `RKLB_Launch_Tracker.xlsx` | Regenerated every run from the CSVs; three formatted tabs |
| `scripts/build_workbook.py` | Rebuilds the workbook from the CSVs |

Regenerate the workbook after any CSV edit:

```bash
python3 scripts/build_workbook.py   # requires openpyxl
```

## Data rules

- **Never delete rows.** Corrections are made in place and noted in `Notes`.
- **`Timeframe Change History` is append-only.** Every date/timeframe change is
  recorded with the date RICH observed it. This is the critical field for
  revenue-timing analysis.
- **Disclosed vs estimated figures are never mixed.** `... - Disclosed ($)`
  holds only figures explicitly stated by Rocket Lab or in SEC filings.
  `... - Estimated ($)` is RICH's estimate, and its basis is always stated in
  `Notes`.
- **Undisclosed customers** are logged as `Undisclosed`, with any inference and
  a confidence level in `Notes` — never silently resolved to a guess.
- **Conflicting sources** are flagged in `Notes` rather than silently resolved.
  Rocket Lab primary sources and SEC filings take precedence.

### Avoiding double-counted launch revenue

`forward_manifest.csv` mixes two kinds of row, distinguished by `Row Type`:

- `Booking` — an announced contract, carrying the full launch count and value.
- `Scheduled launch` — an individual future mission with a published date, which
  in most cases **draws against one of the bookings above it**.

Do not sum estimated values across both row types, or launch revenue will be
counted twice. The `Notes` field on each `Scheduled launch` row says so too.

## Estimate basis

Revenue estimates use Rocket Lab's own disclosed *revenue per launch* metric for
the year the launch occurred, so the series tracks the company's reporting rather
than a list price:

| Period | Revenue per launch | Source |
|---|---|---|
| FY2020 | $5.5M | FY2022 10-K |
| FY2021 | $8.1M | FY2022 10-K |
| FY2022 | $6.7M | FY2022 10-K |
| FY2023 | $7.1M | FY2025 10-K |
| FY2024 | $7.8M | FY2025 10-K |
| FY2025 | $8.5M | FY2025 10-K |
| H1 2026 | $9.2M (Q1 $9.3M / Q2 $9.1M) | Q2 2026 10-Q |

Pre-IPO years (2017–2019) have no Rocket Lab-disclosed metric; those rows are
anchored to the FY2020 figure and marked **low confidence**.

HASTE estimates use **$9.5M per flight**, implied by the disclosed $190M /
20-flight MACH-TB 2.0 award (2026-03-18).

Neutron rows carry **no estimated value**: Rocket Lab has disclosed no Neutron
price. Per the standing rules, pricing is re-verified against current filings at
least quarterly.

## Sources, in priority order

1. Rocket Lab official site — newsroom/press releases, missions pages, IR
2. SEC EDGAR — RKLB 10-Q, 10-K, 8-K, earnings releases
3. FAA Office of Commercial Space Transportation — licences and modifications
4. FCC space/experimental filings — for identifying undisclosed payloads
5. Rocket Lab and Peter Beck social media
6. Independent trackers (Wikipedia's Electron launch list, spaceflight press) —
   **cross-checking only**, confirmed against primary sources or clearly marked
   as secondary in the `Sources` field
