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
    2026: "Fleet avg cost per launch disclosed at $4.9M for 6M ended 2026-06-30 (Q2 2026 10-Q); not mission-specific.",
    2025: "Fleet avg cost per launch disclosed at $5.3M for 6M ended 2025-06-30 (Q2 2026 10-Q comparative); not mission-specific.",
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

def build_xlsx(completed, manifest, runlog):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    hdr_fill = PatternFill("solid", fgColor="1F3864")
    hdr_font = Font(color="FFFFFF", bold=True, size=10)
    thin = Side(style="thin", color="D9D9D9")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    def sheet(ws, cols, rows, widths, money_cols=(), wrap_cols=(), number_cols=()):
        ws.append(cols)
        for c in range(1, len(cols) + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill, cell.font, cell.border = hdr_fill, hdr_font, border
            cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
        ws.row_dimensions[1].height = 34
        for r in rows:
            ws.append(r)
        for ri in range(2, ws.max_row + 1):
            for ci in range(1, len(cols) + 1):
                cell = ws.cell(row=ri, column=ci)
                cell.border = border
                cell.font = Font(size=10)
                if ci in money_cols:
                    cell.number_format = '#,##0;[Red]-#,##0'
                    cell.alignment = Alignment(horizontal="right", vertical="top")
                elif ci in number_cols:
                    cell.alignment = Alignment(horizontal="center", vertical="top")
                elif ci in wrap_cols:
                    cell.alignment = Alignment(wrap_text=True, vertical="top")
                else:
                    cell.alignment = Alignment(vertical="top")
            if ri % 2 == 0:
                for ci in range(1, len(cols) + 1):
                    ws.cell(row=ri, column=ci).fill = PatternFill("solid", fgColor="F4F6FB")
        for ci, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(ci)].width = w
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{ws.max_row}"

    ws1 = wb.active
    ws1.title = "Completed Launches"
    sheet(ws1, COMPLETED_COLS, completed,
          [8, 13, 10, 34, 30, 13, 20, 16, 10, 34, 13, 15, 15, 14, 60, 85],
          money_cols=(12, 13, 14), wrap_cols=(4, 5, 7, 10, 15, 16), number_cols=(1,))

    ws2 = wb.create_sheet("Forward Manifest")
    sheet(ws2, MANIFEST_COLS, manifest,
          [14, 16, 34, 13, 11, 46, 34, 17, 17, 18, 70, 60, 85],
          money_cols=(8, 9), wrap_cols=(3, 6, 7, 11, 12, 13), number_cols=(5,))

    ws3 = wb.create_sheet("Run Log")
    sheet(ws3, RUNLOG_COLS, runlog,
          [14, 11, 24, 16, 16, 40, 10, 24, 26, 30, 90],
          wrap_cols=(6, 10, 11), number_cols=(4, 5))

    out = os.path.join(ROOT, "RKLB_Launch_Tracker.xlsx")
    wb.save(out)
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
