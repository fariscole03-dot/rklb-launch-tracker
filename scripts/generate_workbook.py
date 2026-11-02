#!/usr/bin/env python3
"""Regenerate RKLB_Launch_Tracker.xlsx from the CSVs in data/.

Run every RICH run:  /usr/local/bin/python3.13 scripts/generate_workbook.py
"""
import csv, os, sys, re, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data')
OUT  = os.path.join(ROOT, 'RKLB_Launch_Tracker.xlsx')

TABS = [
    ('Completed Launches', 'completed_launches.csv'),
    ('Forward Manifest',   'forward_manifest.csv'),
    ('Run Log',            'run_log.csv'),
]

HDR_FILL   = PatternFill('solid', fgColor='0B3D5C')
HDR_FONT   = Font(color='FFFFFF', bold=True, size=11)
BAND_FILL  = PatternFill('solid', fgColor='EEF3F7')
FAIL_FILL  = PatternFill('solid', fgColor='F8D7DA')
SLIP_FILL  = PatternFill('solid', fgColor='FFF3CD')
THIN       = Side(style='thin', color='C8D2DA')
BORDER     = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

# Columns that hold long prose -> capped width, wrapped
WIDE = {'Sources', 'Notes', 'Timeframe Change History', 'Announced Timeframe', 'Launch Site',
        'Customer(s)', 'Mission Name', 'Number of Launches in booking'}
MONEY_HINT = ('($)',)


def autosize(ws, header):
    for i, name in enumerate(header, start=1):
        col = get_column_letter(i)
        if name in ('Sources', 'Notes', 'Timeframe Change History'):
            ws.column_dimensions[col].width = 60
            continue
        longest = len(str(name))
        for r in range(2, ws.max_row + 1):
            v = ws.cell(row=r, column=i).value
            if v is not None:
                longest = max(longest, min(len(str(v)), 48))
        ws.column_dimensions[col].width = min(max(longest + 2, 10), 46)


def build():
    wb = Workbook()
    wb.remove(wb.active)
    made = 0
    for tab, fn in TABS:
        path = os.path.join(DATA, fn)
        if not os.path.exists(path):
            print(f'  ! missing {fn}, skipping tab "{tab}"', file=sys.stderr)
            continue
        with open(path, newline='', encoding='utf-8') as f:
            rows = list(csv.reader(f))
        if not rows:
            continue
        header, body = rows[0], rows[1:]
        ws = wb.create_sheet(tab)

        ws.append(header)
        for c in range(1, len(header) + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill, cell.font = HDR_FILL, HDR_FONT
            cell.alignment = Alignment(vertical='center', wrap_text=True)
            cell.border = BORDER
        ws.row_dimensions[1].height = 30

        money_cols = [i for i, h in enumerate(header) if any(k in h for k in MONEY_HINT)]
        out_i  = header.index('Outcome') if 'Outcome' in header else None
        stat_i = header.index('Status') if 'Status' in header else None

        for ri, row in enumerate(body, start=2):
            row = row + [''] * (len(header) - len(row))
            for ci, val in enumerate(row, start=1):
                v = val
                h = header[ci - 1]
                if (ci - 1) in money_cols and val:
                    try:
                        v = float(val)
                    except ValueError:
                        v = val
                elif h == 'Flight #' and val.isdigit():
                    v = int(val)
                elif h == 'Launch Date (UTC)' and val:
                    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})(?:\s+(\d{2}):(\d{2}))?$', val.strip())
                    if m:
                        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
                        hh = int(m.group(4)) if m.group(4) else 0
                        mi = int(m.group(5)) if m.group(5) else 0
                        v = datetime.datetime(y, mo, d, hh, mi)
                cell = ws.cell(row=ri, column=ci, value=v)
                cell.border = BORDER
                cell.alignment = Alignment(
                    vertical='top',
                    wrap_text=header[ci - 1] in WIDE or header[ci - 1] in ('Sources', 'Notes', 'Timeframe Change History'))
                if isinstance(v, float):
                    cell.number_format = '#,##0'
                elif isinstance(v, datetime.datetime):
                    cell.number_format = 'yyyy-mm-dd hh:mm'
            fill = BAND_FILL if ri % 2 == 0 else None
            if out_i is not None and row[out_i] in ('Failure', 'Partial'):
                fill = FAIL_FILL
            elif stat_i is not None and row[stat_i] == 'Slipped':
                fill = SLIP_FILL
            if fill:
                for ci in range(1, len(header) + 1):
                    ws.cell(row=ri, column=ci).fill = fill

        ws.freeze_panes = 'A2'
        ws.auto_filter.ref = f'A1:{get_column_letter(len(header))}{ws.max_row}'
        autosize(ws, header)
        print(f'  {tab}: {len(body)} rows x {len(header)} cols')
        made += 1

    if not made:
        print('no tabs built; aborting', file=sys.stderr)
        return 1
    wb.save(OUT)
    print(f'wrote {OUT} ({os.path.getsize(OUT):,} bytes)')
    return 0


if __name__ == '__main__':
    raise SystemExit(build())
