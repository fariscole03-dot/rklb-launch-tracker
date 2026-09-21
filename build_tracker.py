#!/usr/bin/env python3
"""
RICH - Rocketlab Information Collector & Herald
Regenerates RKLB_Launch_Tracker.xlsx from the CSVs in data/.

The CSVs are the source of truth and are edited (append-only; corrections
in place) by RICH each run. This script only formats them into the workbook
that gets emailed.

Uses xlsxwriter rather than openpyxl: xlsxwriter writes a shared-strings
table, so the long Sources/Notes text that repeats across rows is stored
once instead of per cell. That roughly halves the emailed file with no
loss of content.
"""
import csv
import os
import sys

import xlsxwriter

REPO = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(REPO, "data")
OUT = os.path.join(REPO, "RKLB_Launch_Tracker.xlsx")

TABS = [
    ("Completed Launches", "completed_launches.csv"),
    ("Forward Manifest", "forward_manifest.csv"),
    ("Run Log", "run_log.csv"),
]

# Long prose / URL columns: wide and wrapped.
WIDE = {
    "Notes", "Sources", "Timeframe Change History", "Announced Timeframe",
    "Mission Name", "Customer(s)", "Sources Checked", "Sources Unreachable",
    "Payload(s)", "Launch Site",
}
MONEY = {
    "Revenue - Disclosed ($)", "Revenue - Estimated ($)", "Direct Mission Costs ($)",
    "Contract Value - Disclosed ($)", "Contract Value - Estimated ($)",
}
# Stored as numbers so Excel/Sheets sort them numerically rather than as text.
INTS = {
    "Flight #", "Number of Launches in booking", "New Completed Launches Added",
    "Manifest Rows Added", "Manifest Rows Updated",
}


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        raise SystemExit(f"{path} is empty")
    return rows[0], rows[1:]


def build_sheet(wb, fmts, title, header, rows):
    ws = wb.add_worksheet(title)
    ws.write_row(0, 0, header, fmts["header"])
    ws.set_row(0, 34)
    ws.freeze_panes(1, 0)

    for i, h in enumerate(header):
        if h in WIDE:
            width = 52
        elif h in MONEY:
            width = 17
        else:
            width = max(11, min(26, len(h) + 4))
        ws.set_column(i, i, width)

    for r, row in enumerate(rows, start=1):
        row = row + [""] * (len(header) - len(row))
        band = "b" if r % 2 == 0 else "a"
        for c, raw in enumerate(row[: len(header)]):
            h = header[c]
            value, kind = raw, "text"
            if raw.strip() and h in MONEY:
                try:
                    value, kind = float(raw), "money"
                except ValueError:
                    pass
            elif raw.strip() and h in INTS:
                try:
                    value, kind = int(raw), "int"
                except ValueError:
                    pass
            key = f"{kind}_{'wrap' if h in WIDE else 'plain'}_{band}"
            ws.write(r, c, value, fmts[key])

    if rows:
        ws.autofilter(0, 0, len(rows), len(header) - 1)
    return ws


def make_formats(wb):
    base = dict(font_size=10, border=1, border_color="B7C4D3", valign="top")
    fmts = {
        "header": wb.add_format(dict(
            base, bold=True, font_color="FFFFFF", bg_color="0B2E4F",
            valign="vcenter", text_wrap=True)),
    }
    for kind, numfmt in (("text", None), ("money", '#,##0;;"-"'), ("int", "0")):
        for wrap in (True, False):
            for band, colour in (("a", None), ("b", "EEF3F8")):
                spec = dict(base)
                if wrap:
                    spec["text_wrap"] = True
                if colour:
                    spec["bg_color"] = colour
                if numfmt:
                    spec["num_format"] = numfmt
                key = f"{kind}_{'wrap' if wrap else 'plain'}_{band}"
                fmts[key] = wb.add_format(spec)
    return fmts


def main():
    wb = xlsxwriter.Workbook(OUT, {"constant_memory": False, "strings_to_urls": False})
    fmts = make_formats(wb)
    counts = []
    for title, fname in TABS:
        path = os.path.join(DATA, fname)
        if not os.path.exists(path):
            print(f"missing {path}", file=sys.stderr)
            return 1
        header, rows = load(path)
        build_sheet(wb, fmts, title, header, rows)
        counts.append((title, len(rows)))
    wb.close()
    for title, n in counts:
        print(f"{title}: {n} rows")
    print(f"wrote {OUT} ({os.path.getsize(OUT):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
