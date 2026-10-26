# -*- coding: utf-8 -*-
"""Regenerate the RKLB tracker CSVs and the Excel workbook from launch_data.py.

Usage: /usr/bin/python3.13 scripts/build_tracker.py
The CSVs are the master record; the xlsx is always rebuilt from them.
"""
import csv, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import launch_data as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)

COMPLETED_COLS = ["Flight #","Launch Date (UTC)","Vehicle","Mission Name","Customer(s)",
    "Customer Disclosure","Launch Site","Dedicated / Rideshare","Outcome","Recovery",
    "Contract Announcement Date","Revenue - Disclosed ($)","Revenue - Estimated ($)",
    "Direct Mission Costs ($)","Sources","Notes"]

MANIFEST_COLS = ["Announcement Date","Vehicle","Customer(s)","Customer Disclosure",
    "Number of Launches in booking","Announced Timeframe","Launch Site",
    "Contract Value - Disclosed ($)","Contract Value - Estimated ($)","Status",
    "Timeframe Change History","Sources","Notes"]

RUNLOG_COLS = ["Run Date (UTC)","Day of Week","Run Type","New Launches Logged",
    "Manifest Rows Added","Manifest Changes","Email Sent","Email Type",
    "Pre-Earnings Package Sent This Quarter","Sources Unreachable","Notes"]

# Disclosed average cost per launch, by period, from the Q2 2026 10-Q (fleet averages, not per mission).
COST_NOTE = {
    2026: "fleet avg $4.9M H1 2026 (10-Q), not mission-specific",
    2025: "fleet avg $5.3M H1 2025 (10-Q), not mission-specific",
}

def build_completed():
    rows = []
    for (fl, date, veh, mission, cust, disc, site, mode, outcome, rec, extra_src, notes) in D.L:
        year = int(date[:4])
        srcs = [D.WP, D.RLL]
        if extra_src:
            srcs.insert(0, extra_src)
        if year >= 2025:
            srcs.append(D.RLU)
        disclosed, est, basis = "", "", ""
        if fl in D.DISCLOSED_REV:
            disclosed, dbasis = D.DISCLOSED_REV[fl]
            basis = dbasis
            srcs.append(D.Q2_10Q)
        if veh == "HASTE":
            est = D.HASTE_EST
            basis = (basis + " " if basis else "") + D.HASTE_BASIS
        else:
            est = D.EST_BY_YEAR[year]
            basis = (basis + " " if basis else "") + D.EST_BASIS[year]
            srcs.append(D.Q2_10Q)
        note = notes.strip()
        note = (note + " | " if note else "") + "Revenue basis: " + basis
        if year in COST_NOTE:
            note += " | Cost: " + COST_NOTE[year]
        rows.append([fl, date, veh, mission, cust, disc, site, mode, outcome, rec,
                     "", disclosed, est, "", " | ".join(dict.fromkeys(srcs)), note])
    rows.sort(key=lambda r: r[0])
    return rows

def build_manifest():
    rows = []
    for (ad, veh, cust, disc, n, tf, site, vdisc, vest, status, hist, srcs, notes) in D.M:
        rows.append([ad, veh, cust, disc, n, tf, site, vdisc, vest, status, hist, srcs, notes])
    rows.sort(key=lambda r: (r[0], r[2]), reverse=True)
    return rows

def write_csv(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(cols)
        w.writerows(rows)

# The workbook renders the CSVs with repeated citations factored into a legend tab, so the
# emailed file stays small enough to send. The CSVs remain authoritative: they carry the full
# URL list and the full revenue basis on every row.
SOURCE_KEYS = [
    (D.WP, "WIKI-ELECTRON"),
    (D.RLL, "RL-LAUNCHES"),
    (D.RLU, "RL-NEWSROOM"),
    (D.Q2_10Q, "RKLB-10Q-Q2-2026"),
]
METHOD_ROWS = [
    ["SOURCE KEY", "FULL REFERENCE"],
    ["WIKI-ELECTRON", D.WP],
    ["RL-LAUNCHES", D.RLL],
    ["RL-NEWSROOM", D.RLU],
    ["RKLB-10Q-Q2-2026", D.Q2_10Q],
    ["", ""],
    ["REVENUE ESTIMATE BASIS", "(estimates are never mixed with disclosed figures)"],
] + [[str(y), b] for y, b in sorted(D.EST_BASIS.items(), reverse=True)] + [
    ["HASTE (all years)", D.HASTE_BASIS],
    ["", ""],
    ["DIRECT COSTS", "Disclosed fleet averages only, not mission-specific: $4.9M/launch H1 2026, $5.3M/launch "
                     "H1 2025 (Q2 2026 10-Q). Per-mission costs undisclosed, so that column is blank."],
    ["NEUTRON STATUS", D.NEUTRON_NOTE],
    ["THIS WORKBOOK", "Repeated source URLs appear as the keys above to keep the emailed file small. The CSVs in "
                      "the repo carry full URLs and the full revenue basis per row and are the master record."],
]

NOTE_CAP = 185  # workbook only; the CSVs keep the full note text

def _slim(rows, src_i, note_i):
    """XLSX-only: swap repeated URLs for keys and lift per-row basis boilerplate to the method tab."""
    out = []
    for r in rows:
        r = list(r)
        src = r[src_i]
        for url, key in SOURCE_KEYS:
            src = src.replace(url, key)
        r[src_i] = src
        note = r[note_i]
        for marker in (" | Revenue basis: ", "Revenue basis: "):
            if marker in note:
                note = note.split(marker)[0]
                break
        note = note.strip() or "-"
        if len(note) > NOTE_CAP:
            cut = note[:NOTE_CAP]
            sp = cut.rfind(" ")
            note = (cut[:sp] if sp > 110 else cut).rstrip(" ,;.:|") + " ... [full note in CSV]"
        r[note_i] = note
        out.append(r)
    return out

def build_xlsx(completed, manifest, runlog):
    import minixlsx
    sheets = [
        minixlsx.Sheet("Completed Launches", COMPLETED_COLS, _slim(completed, 14, 15),
                       [8, 13, 10, 34, 30, 13, 20, 16, 10, 34, 13, 15, 15, 14, 46, 85],
                       money_cols=(12, 13, 14), wrap_cols=(4, 5, 7, 10, 15, 16), center_cols=(1, 2, 3, 6)),
        minixlsx.Sheet("Forward Manifest", MANIFEST_COLS, _slim(manifest, 11, 12),
                       [14, 16, 34, 13, 11, 46, 34, 17, 17, 18, 70, 46, 85],
                       money_cols=(8, 9), wrap_cols=(3, 6, 7, 11, 12, 13), center_cols=(1, 2, 4, 5)),
        minixlsx.Sheet("Sources & Method", METHOD_ROWS[0], METHOD_ROWS[1:], [26, 120], wrap_cols=(2,)),
        minixlsx.Sheet("Run Log", RUNLOG_COLS, runlog,
                       [14, 11, 24, 16, 16, 40, 10, 24, 26, 30, 90],
                       wrap_cols=(6, 10, 11), center_cols=(1, 2, 4, 5)),
    ]
    out = os.path.join(ROOT, "RKLB_Launch_Tracker.xlsx")
    minixlsx.write(out, sheets)
    return out

def read_runlog():
    path = os.path.join(DATA, "run_log.csv")
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        r = list(csv.reader(f))
    rows = r[1:] if r else []
    for row in rows:  # numeric columns come back as strings from csv
        for i in (3, 4):
            if len(row) > i and str(row[i]).strip().lstrip("-").isdigit():
                row[i] = int(row[i])
    return rows

def main():
    completed = build_completed()
    manifest = build_manifest()
    write_csv(os.path.join(DATA, "completed_launches.csv"), COMPLETED_COLS, completed)
    write_csv(os.path.join(DATA, "forward_manifest.csv"), MANIFEST_COLS, manifest)
    runlog = read_runlog()
    out = build_xlsx(completed, manifest, runlog)

    # --- integrity checks against Rocket Lab's own published milestone counts ---
    from collections import Counter
    by_year = Counter(r[1][:4] for r in completed)
    checks = []
    checks.append(("2024 launch count == 16", by_year["2024"] == 16, by_year["2024"]))
    checks.append(("2025 launch count == 21 (RL: 'ends 2025 with 21 launches')", by_year["2025"] == 21, by_year["2025"]))
    checks.append(("highest flight # == 98 (RL: '98th Electron mission')", completed[-1][0] == 98, completed[-1][0]))
    n2026_thru_93 = sum(1 for r in completed if r[1][:4] == "2026" and r[0] <= 93)
    checks.append(("flight 93 is 14th of 2026 (RL milestone)", n2026_thru_93 == 14, n2026_thru_93))
    checks.append(("2025 all-success (RL: '100% mission success')",
                   all(r[8] == "Success" for r in completed if r[1][:4] == "2025"), "ok"))
    print(f"\nWrote {len(completed)} completed launches, {len(manifest)} manifest rows")
    print(f"Workbook: {out}")
    print("Launches per year:", dict(sorted(by_year.items())))
    print("\nIntegrity checks vs Rocket Lab's own published counts:")
    ok = True
    for name, passed, got in checks:
        print(("  PASS  " if passed else "  FAIL  ") + name + f"   (got {got})")
        ok = ok and passed
    print("ALL CHECKS PASSED" if ok else "*** CHECK FAILURES ***")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
