#!/usr/bin/env python3
"""
Regenerate RKLB_Launch_Tracker.xlsx from the three CSVs in data/.
Run every time the CSVs change. Openable in Excel and Google Sheets.
"""
import csv
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "RKLB_Launch_Tracker.xlsx")

TABS = [
    ("Completed Launches", "completed_launches.csv", "RKLBCompleted"),
    ("Forward Manifest", "forward_manifest.csv", "RKLBManifest"),
    ("Run Log", "run_log.csv", "RKLBRunLog"),
]

HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
FAIL_FILL = PatternFill("solid", fgColor="F8CBAD")
UNDISC_FILL = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MONEY_COLS = {
    "Revenue - Disclosed ($)", "Revenue - Estimated ($)", "Direct Mission Costs ($)",
    "Contract Value - Disclosed ($)", "Contract Value - Estimated ($)",
}
# Columns that hold long prose and should wrap rather than run off the sheet
WIDE_COLS = {"Notes", "Sources", "Timeframe Change History", "Announced Timeframe",
             "Sources Checked", "Sources Unreachable"}

# Sensible per-column widths; anything unlisted is auto-sized within bounds.
FIXED_WIDTHS = {"Notes": 70, "Sources": 50, "Timeframe Change History": 55,
                "Sources Checked": 55, "Sources Unreachable": 40, "Announced Timeframe": 30}


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        return list(r)


def build():
    wb = Workbook()
    wb.remove(wb.active)

    for tab_name, fname, table_name in TABS:
        path = os.path.join(DATA, fname)
        if not os.path.exists(path):
            continue
        rows = load(path)
        if not rows:
            continue
        header, body = rows[0], rows[1:]

        ws = wb.create_sheet(tab_name)
        ws.append(header)
        for row in body:
            # pad/trim to header length so the Excel table stays rectangular
            row = (row + [""] * len(header))[:len(header)]
            ws.append(row)

        idx = {name: i for i, name in enumerate(header)}

        # Flight # numeric so the tab sorts in flight order, not lexically
        if "Flight #" in idx:
            c = idx["Flight #"] + 1
            for r in range(2, ws.max_row + 1):
                cell = ws.cell(row=r, column=c)
                v = str(cell.value or "").strip()
                if v.isdigit():
                    cell.value = int(v)

        # Numeric coercion for money columns so the user can sum them directly
        for col_name in MONEY_COLS & set(header):
            c = idx[col_name] + 1
            for r in range(2, ws.max_row + 1):
                cell = ws.cell(row=r, column=c)
                v = str(cell.value or "").strip()
                if v and v.replace(".", "", 1).isdigit():
                    cell.value = float(v) if "." in v else int(v)
                    cell.number_format = '#,##0'
                cell.alignment = Alignment(horizontal="right", vertical="top")

        # Header styling
        for c in range(1, len(header) + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill = HEADER_FILL
            cell.font = HEADER_FONT
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        ws.row_dimensions[1].height = 30

        # Body styling
        for r in range(2, ws.max_row + 1):
            for c in range(1, len(header) + 1):
                cell = ws.cell(row=r, column=c)
                cell.border = BORDER
                col_name = header[c - 1]
                if col_name in WIDE_COLS:
                    cell.alignment = Alignment(vertical="top", wrap_text=True)
                elif col_name not in MONEY_COLS:
                    cell.alignment = Alignment(vertical="top")

        # Highlight rows that need the reader's eye
        if "Outcome" in idx:
            oc = idx["Outcome"] + 1
            for r in range(2, ws.max_row + 1):
                if str(ws.cell(row=r, column=oc).value).strip() in ("Failure", "Partial"):
                    for c in range(1, len(header) + 1):
                        ws.cell(row=r, column=c).fill = FAIL_FILL
        if "Customer Disclosure" in idx:
            dc = idx["Customer Disclosure"] + 1
            for r in range(2, ws.max_row + 1):
                if str(ws.cell(row=r, column=dc).value).strip() == "Undisclosed":
                    ws.cell(row=r, column=dc).fill = UNDISC_FILL

        # Column widths
        for c, col_name in enumerate(header, start=1):
            letter = get_column_letter(c)
            if col_name in FIXED_WIDTHS:
                ws.column_dimensions[letter].width = FIXED_WIDTHS[col_name]
            else:
                longest = max([len(col_name)] +
                              [len(str(ws.cell(row=r, column=c).value or ""))
                               for r in range(2, min(ws.max_row, 400) + 1)])
                ws.column_dimensions[letter].width = max(10, min(longest + 2, 34))

        # Freeze header + autofilter via a real Excel table
        ws.freeze_panes = "A2"
        if ws.max_row >= 2:
            ref = f"A1:{get_column_letter(len(header))}{ws.max_row}"
            table = Table(displayName=table_name, ref=ref)
            table.tableStyleInfo = TableStyleInfo(
                name="TableStyleLight9", showRowStripes=True, showColumnStripes=False)
            ws.add_table(table)

    wb.save(OUT)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"wrote {path} ({os.path.getsize(path):,} bytes)")
