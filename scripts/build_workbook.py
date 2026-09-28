#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate RKLB_Launch_Tracker.xlsx from the CSVs in data/.

Run every RICH run after the CSVs are updated:
    python3 scripts/build_workbook.py
Produces three formatted tabs (Completed Launches, Forward Manifest, Run Log)
that open in Excel or Google Sheets.
"""
import csv, os, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
XLSX = os.path.join(ROOT, 'RKLB_Launch_Tracker.xlsx')

TABS = [
    ('Completed Launches', 'completed_launches.csv'),
    ('Forward Manifest',   'forward_manifest.csv'),
    ('Run Log',            'run_log.csv'),
]

HDR_FILL  = PatternFill('solid', fgColor='0B2C4A')
HDR_FONT  = Font(bold=True, color='FFFFFF', size=10)
BODY_FONT = Font(size=10)
ALT_FILL  = PatternFill('solid', fgColor='F2F6FA')
FAIL_FILL = PatternFill('solid', fgColor='FBD5D5')
THIN      = Side(style='thin', color='D0D7DE')
BORDER    = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MONEY_COLS = {'Revenue - Disclosed ($)', 'Revenue - Estimated ($)',
              'Direct Mission Costs ($)', 'Contract Value - Disclosed ($)',
              'Contract Value - Estimated ($)'}
# Columns that hold long prose -> wrap and give them room
WIDE_COLS  = {'Sources': 62, 'Notes': 80, 'Timeframe Change History': 34,
              'Announced Timeframe': 34, 'Payload': 26, 'Customer(s)': 30,
              'Sources Checked OK': 60, 'Sources Unreachable / Not Swept': 60,
              'Ambiguities Flagged': 60, 'Next Earnings Date (status)': 45,
              'Pre-Earnings Package Sent This Quarter': 40}
NARROW = {'Flight #': 8, 'Launch Date (UTC)': 13, 'Launch Time (UTC)': 11,
          'Vehicle': 10, 'Outcome': 10}


def autosize(ws, headers, rows):
    for i, h in enumerate(headers, start=1):
        letter = get_column_letter(i)
        if h in WIDE_COLS:
            ws.column_dimensions[letter].width = WIDE_COLS[h]
        elif h in NARROW:
            ws.column_dimensions[letter].width = NARROW[h]
        else:
            longest = max([len(h)] + [len(str(r[i-1])) for r in rows[:400]] or [len(h)])
            ws.column_dimensions[letter].width = min(max(longest + 2, 11), 34)


def write_tab(wb, title, path, first):
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    if not os.path.exists(path):
        ws['A1'] = 'source CSV missing: ' + os.path.basename(path)
        return
    with open(path, newline='', encoding='utf-8') as fh:
        rd = list(csv.reader(fh))
    if not rd:
        ws['A1'] = 'empty'
        return
    headers, body = rd[0], rd[1:]
    ws.append(headers)
    for c in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill, cell.font, cell.border = HDR_FILL, HDR_FONT, BORDER
        cell.alignment = Alignment(vertical='center', horizontal='left', wrap_text=True)
    ws.row_dimensions[1].height = 30

    money_idx = {i for i, h in enumerate(headers) if h in MONEY_COLS}
    wrap_idx  = {i for i, h in enumerate(headers) if h in WIDE_COLS}
    try:
        out_idx = headers.index('Outcome')
    except ValueError:
        out_idx = None

    for rn, row in enumerate(body, start=2):
        failed = out_idx is not None and len(row) > out_idx and row[out_idx] not in ('Success', '')
        for i, h in enumerate(headers):
            v = row[i] if i < len(row) else ''
            if i in money_idx and str(v).strip():
                try:
                    v = float(v)
                except ValueError:
                    pass
            elif h == 'Flight #' and str(v).strip():
                try:
                    v = int(v)
                except ValueError:
                    pass
            cell = ws.cell(row=rn, column=i + 1, value=v)
            cell.font, cell.border = BODY_FONT, BORDER
            cell.alignment = Alignment(vertical='top', wrap_text=(i in wrap_idx))
            if i in money_idx:
                cell.number_format = '#,##0'
            if failed:
                cell.fill = FAIL_FILL
            elif rn % 2 == 0:
                cell.fill = ALT_FILL

    ws.freeze_panes = 'B2'
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(body)+1}"
    autosize(ws, headers, body)
    return len(body)


def main():
    wb = Workbook()
    counts = {}
    for n, (title, fn) in enumerate(TABS):
        counts[title] = write_tab(wb, title, os.path.join(DATA, fn), first=(n == 0))
    wb.properties.title = 'RKLB Launch Tracker'
    wb.properties.creator = 'RICH - Rocketlab Information Collector & Herald'
    wb.save(XLSX)
    print('wrote', XLSX)
    for k, v in counts.items():
        print(f'  {k}: {v} rows')


if __name__ == '__main__':
    sys.exit(main())
