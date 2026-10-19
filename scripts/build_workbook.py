#!/usr/bin/env python3
"""Regenerate RKLB_Launch_Tracker.xlsx from the CSVs in data/.

Run from the repository root:  python3 scripts/build_workbook.py
Requires openpyxl.
"""
import csv, os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'RKLB_Launch_Tracker.xlsx')

TABS = [
    ('Completed Launches', 'data/completed_launches.csv'),
    ('Forward Manifest',   'data/forward_manifest.csv'),
    ('Run Log',            'data/run_log.csv'),
]

HEADER_FILL = PatternFill('solid', fgColor='14233C')
HEADER_FONT = Font(bold=True, color='FFFFFF', size=11)
BAND_FILL   = PatternFill('solid', fgColor='F2F5FA')
THIN        = Side(style='thin', color='D0D7E3')
BORDER      = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Columns rendered as currency, and columns kept narrow-but-wrapped
MONEY_HINTS = ('($)',)
WIDE = {'Sources': 60, 'Notes': 80, 'Timeframe Change History': 55,
        'Mission Name': 30, 'Customer(s)': 28, 'Announced Timeframe': 26,
        'Sources Checked': 60, 'Sources Unreachable': 60}


def as_number(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def add_tab(wb, title, path, first):
    full = os.path.join(ROOT, path)
    with open(full, newline='', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    if not rows:
        raise SystemExit(f'{path} is empty')
    head, body = rows[0], rows[1:]

    ws = wb.active if first else wb.create_sheet()
    ws.title = title

    ws.append(head)
    for c in range(1, len(head) + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill, cell.font, cell.border = HEADER_FILL, HEADER_FONT, BORDER
        cell.alignment = Alignment(vertical='center', horizontal='left', wrap_text=True)
    ws.row_dimensions[1].height = 30

    money_cols = {i for i, h in enumerate(head) if any(k in h for k in MONEY_HINTS)}

    for r, row in enumerate(body, start=2):
        row = row + [''] * (len(head) - len(row))
        for i, val in enumerate(row):
            cell = ws.cell(row=r, column=i + 1)
            n = as_number(val) if (i in money_cols or head[i] == 'Flight #') else None
            cell.value = n if n is not None else val
            if i in money_cols and n is not None:
                cell.number_format = '#,##0'
            cell.border = BORDER
            cell.alignment = Alignment(vertical='top', wrap_text=head[i] in WIDE)
            if r % 2 == 0:
                cell.fill = BAND_FILL

    for i, h in enumerate(head, start=1):
        width = WIDE.get(h)
        if width is None:
            longest = max([len(h)] + [len(str(row[i - 1])) for row in body if len(row) >= i])
            width = min(max(longest + 2, 10), 34)
        ws.column_dimensions[get_column_letter(i)].width = width

    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = f'A1:{get_column_letter(len(head))}{len(body) + 1}'
    return len(body)


def main():
    wb = Workbook()
    counts = []
    for n, (title, path) in enumerate(TABS):
        counts.append((title, add_tab(wb, title, path, first=(n == 0))))
    wb.save(OUT)
    print('wrote', OUT)
    for title, c in counts:
        print(f'  {title}: {c} rows')


if __name__ == '__main__':
    main()
