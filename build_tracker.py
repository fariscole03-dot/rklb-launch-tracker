#!/usr/bin/env python3
"""
RICH - Rocketlab Information Collector & Herald
Regenerates RKLB_Launch_Tracker.xlsx from the CSVs in data/.

The CSVs are the source of truth and are edited (append-only; corrections
in place) by RICH each run. This script only formats them into the workbook
that gets emailed.
"""
import csv
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

REPO = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(REPO, "data")
OUT = os.path.join(REPO, "RKLB_Launch_Tracker.xlsx")

TABS = [
    ("Completed Launches", "completed_launches.csv"),
    ("Forward Manifest", "forward_manifest.csv"),
    ("Run Log", "run_log.csv"),
]

HEADER_FILL = PatternFill("solid", fgColor="0B2E4F")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
BODY_FONT = Font(size=10)
BAND_FILL = PatternFill("solid", fgColor="EEF3F8")
THIN = Side(style="thin", color="B7C4D3")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Columns that hold long prose / URLs and should be given generous width + wrap
WIDE = {
    "Notes",
    "Sources",
    "Timeframe Change History",
    "Announced Timeframe",
    "Mission Name",
    "Customer(s)",
    "Sources Checked",
    "Sources Unreachable",
}
MONEY = {
    "Revenue - Disclosed ($)",
    "Revenue - Estimated ($)",
    "Direct Mission Costs ($)",
    "Contract Value - Disclosed ($)",
    "Contract Value - Estimated ($)",
}
# Stored as numbers so Excel/Sheets sort them numerically rather than as text.
INTS = {
    "Flight #",
    "Number of Launches in booking",
    "New Completed Launches Added",
    "Manifest Rows Added",
    "Manifest Rows Updated",
}


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise SystemExit(f"{path} is empty")
    return rows[0], rows[1:]


def build_sheet(wb, title, header, rows):
    ws = wb.create_sheet(title)
    ws.append(header)
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        cell.border = BORDER
    ws.row_dimensions[1].height = 34

    money_idx = {i for i, h in enumerate(header) if h in MONEY}
    int_idx = {i for i, h in enumerate(header) if h in INTS}

    for r, row in enumerate(rows, start=2):
        row = row + [""] * (len(header) - len(row))
        for c, value in enumerate(row[: len(header)]):
            if c in (money_idx | int_idx) and value.strip():
                try:
                    value = float(value) if c in money_idx else int(value)
                except ValueError:
                    pass
            cell = ws.cell(row=r, column=c + 1, value=value)
            cell.font = BODY_FONT
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=header[c] in WIDE)
            if isinstance(value, float):
                cell.number_format = '#,##0;;"-"'
            if r % 2 == 0:
                cell.fill = BAND_FILL

    for i, h in enumerate(header, start=1):
        letter = get_column_letter(i)
        if h in WIDE:
            width = 52
        elif h in MONEY:
            width = 17
        else:
            width = max(11, min(26, len(h) + 4))
        ws.column_dimensions[letter].width = width

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(header))}{len(rows) + 1}"
    return ws


def main():
    wb = Workbook()
    wb.remove(wb.active)
    counts = []
    for title, fname in TABS:
        path = os.path.join(DATA, fname)
        if not os.path.exists(path):
            print(f"missing {path}", file=sys.stderr)
            return 1
        header, rows = load(path)
        build_sheet(wb, title, header, rows)
        counts.append((title, len(rows)))
    wb.save(OUT)
    for title, n in counts:
        print(f"{title}: {n} rows")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
