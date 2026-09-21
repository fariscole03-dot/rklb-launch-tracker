# RICH — Sourcing & Estimate Methodology

Maintained by RICH (Rocketlab Information Collector & Herald). Last updated: **2026-09-21**.

## Files

| File | Contents |
|---|---|
| `completed_launches.csv` | One row per flown mission. Append-only; corrections made in place and noted. |
| `forward_manifest.csv` | One row per announced booking or scheduled future launch. Append-only. |
| `run_log.csv` | One row per RICH run. |
| `RKLB_Launch_Tracker.xlsx` | Regenerated every run from the three CSVs by `build_tracker.py`. This is the emailed file. |

## Flight numbering

Rocket Lab numbers Electron and HASTE flights in a **single sequential series**. As of
2026-09-21 the series runs **1–96 with no gaps**: **87 orbital Electron** flights and
**9 suborbital HASTE** flights. Rocket Lab's own press releases count the combined series
(its 19 Sep 2026 release calls flight 96 the "96th Electron launch"), so *Rocket Lab's
launch count is not the same as the orbital Electron count*. Both are available in this
tracker: filter the Vehicle column.

Neutron has **not flown** as of this run.

## Disclosure convention

`Customer Disclosure` is `Disclosed` or `Undisclosed`, judged by **what Rocket Lab itself
announced**, not by what has since been worked out. Several missions Rocket Lab announced
for a "confidential commercial customer" are recorded as `Undisclosed` even though the
operator is identifiable from the payload manifest and contract sequence; the inferred
operator and a confidence level are given in `Notes`. Affected flights: 57, 68, 70, 76,
83, 95.

## Revenue estimate bases

Estimates are **always** labelled `est.` and never mixed with disclosed figures.
Rows in the CSVs carry a short tag (`Rev est. basis A/B/C/D`) pointing at the definitions
below. Re-verify at least quarterly — **next scheduled re-verification: after the Q3 2026
10-Q is filed (expected early–mid November 2026).**

**Basis A — Electron dedicated, launches through 2023: `$7,500,000` est.**
Rocket Lab's published Electron list price for a dedicated mission (~300 kg to LEO),
cross-checked against multiple 2026 secondary sources. Treat as an **upper bound** for
2017–2020 missions, which were priced as early-adopter and flight-test contracts and were
very likely below list.

**Basis B — Electron dedicated, launches 2024 onward: `$9,020,000` est.**
Implied blended revenue per launch = Launch Services segment revenue of **$108.249M** for
the six months ended 30 Jun 2026 (RKLB 10-Q) ÷ **12 launches flown in H1 2026**.
*Caveats, which matter:* the Launch Services segment includes launch-adjacent services
beyond the launches themselves, and revenue is recognised on milestones rather than on
launch dates, so this is a blended proxy and not a price. The same 10-Q implies
**$7.43M/launch for Q2 2026 alone** ($44.586M ÷ 6 launches) versus **~$10.6M/launch for
Q1 2026** — the quarter-to-quarter swing is recognition timing, not pricing, which is
exactly why a half-year blend is used.

**Basis C — HASTE: `$15,000,000` est. — confidence: LOW.**
No per-mission HASTE figure has ever been disclosed. The estimate is bracketed between the
Electron dedicated estimates (~$7.5–9.0M) and the **$22.2M** implied by the July 2026 RSLP
award ($266M ÷ 12 firm launches) — and that $22.2M itself absorbs activation of a new
launch site at Kodiak, so it overstates the marginal mission price. The midpoint is used.
This is the weakest number in the tracker; treat it accordingly.

**Basis D — Neutron: `$52,500,000` est. — confidence: LOW-MEDIUM.**
Midpoint of the **$50–55M** per-launch band Rocket Lab management has publicly described
for Neutron. No Neutron mission has flown or been invoiced, and early-flight pricing may
differ from the steady-state band. Not applicable to the AFRL REGAL experimental mission
with any confidence.

**Failed missions carry no revenue estimate.** Rocket Lab has not disclosed how revenue is
treated when a mission fails (re-flights have historically been provided at no additional
charge). Recognition treatment on flights 1, 13, 20 and 41 is left as a **user modelling
decision**.

## Source priority

1. Rocket Lab official — newsroom/updates, mission pages, investor relations
2. SEC EDGAR — RKLB 10-Q, 10-K, 8-K, earnings releases
3. FAA Office of Commercial Space Transportation — licences and modifications
4. FCC space/experimental filings — for identifying undisclosed payloads
5. Rocket Lab and Peter Beck social media
6. Independent trackers (Wikipedia Electron launch list, reputable spaceflight press) —
   **cross-check only**, confirmed against primary sources or marked secondary

## Known limitations of this backfill (honest statement)

- **Launch-level facts for orbital Electron flights in 2017–2025 were taken from the
  consolidated Wikipedia Electron launch list** (parsed from raw wikitext, so the data is
  complete and unsummarised — but Wikipedia is a *secondary* source, even though it cites
  Rocket Lab press releases throughout). Those rows are flagged in `Notes`.
  Primary-source re-verification will be rolled out in tranches on subsequent runs, and the
  run log will record which tranche was verified. The **2026 orbital rows and all 9 HASTE
  rows** carry Rocket Lab press-release citations already.
- The dataset is **internally validated**: flight numbers are contiguous 1–96 with no gaps
  or duplicates, and the outcome/recovery tallies reconcile against the source's own
  aggregate statistics.
- **Contract announcement dates are incomplete.** Only dates firmly tied to a Rocket Lab
  press release are populated; the rest are blank rather than guessed.
- **FAA licence and FCC filing sweeps were not performed on this run** and are deferred to
  the next. These are the leading indicators for upcoming launches, so near-term manifest
  dates rest on Rocket Lab announcements only.
- `Direct Mission Costs ($)` is blank throughout: Rocket Lab does not disclose per-mission
  costs.

## Anomalies worth knowing about

- **Flight 89 ("Curveball", 11 Jun 2026)** — a *suborbital* HASTE vehicle reached orbit.
  Space-Track catalogued the second stage and kick stage in ~189 × 204 km and ~198 × 199 km
  orbits. Recorded as a Success (it met its mission objectives), but it is a genuine
  off-nominal outcome.
- **Flight 20 ("Running Out Of Toes", 15 May 2021)** — mission `Failure` (second-stage
  failure) but the first stage *was* recovered, so `Recovery` reads `Attempted-recovered`.
  The two columns disagreeing is correct, not a data error.
- **Flight 82 ("That's Not A Knife", 28 Feb 2026)** — the source's own note refers to this
  mission as "Cassowary Vex". Naming conflict left flagged, not silently resolved.
- **Synspective booking count** — the source describes the Sep 2025 renewal as "10
  additional" launches but labels the renewed tranche "16 to 26th", which spans 11. Flagged
  in the manifest row rather than silently resolved.
