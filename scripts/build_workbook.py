#!/usr/bin/env python3
"""Regenerate RKLB_Launch_Tracker.xlsx from the three CSVs in data/.

Three formatted tabs: Completed Launches, Forward Manifest, Run Log.
Opens in Excel and Google Sheets.
"""
import csv, os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

TABS = [
    ('data/completed_launches.csv', 'Completed Launches', '1F3864'),
    ('data/forward_manifest.csv',   'Forward Manifest',   '385723'),
    ('data/run_log.csv',            'Run Log',            '7F6000'),
]
MONEY = ('Revenue - Disclosed ($)', 'Revenue - Estimated ($)', 'Direct Mission Costs ($)',
         'Contract Value - Disclosed ($)', 'Contract Value - Estimated ($)')
INTS  = ('Flight #', 'Number of Launches in booking', 'Completed Launches in File',
         'Launches Added This Run', 'Manifest Rows in File', 'Manifest Rows Added',
         'Timeframe Changes Observed')
# columns that hold long prose -> wrap, capped width
WIDE  = ('Notes', 'Sources', 'Timeframe Change History', 'Announced Timeframe', 'Customer(s)')

thin = Side(style='thin', color='D9D9D9')

def add_tab(wb, path, title, colour, first):
    rows = list(csv.reader(open(path, encoding='utf-8')))
    ws = wb.active if first else wb.create_sheet()
    ws.title = title
    hdr = rows[0]
    ws.append(hdr)
    for r in rows[1:]:
        ws.append(r)

    # header styling
    fill = PatternFill('solid', fgColor=colour)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF', size=11)
        c.fill = fill
        c.alignment = Alignment(vertical='center', wrap_text=True)
        c.border = Border(bottom=thin)
    ws.row_dimensions[1].height = 34
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions

    # column widths + per-cell formatting
    for i, name in enumerate(hdr, start=1):
        L = get_column_letter(i)
        if name in WIDE:
            width = 70 if name in ('Notes', 'Sources', 'Timeframe Change History') else 30
        else:
            longest = max([len(name)] + [len(str(r[i-1])) for r in rows[1:] if i-1 < len(r)])
            width = min(max(longest + 2, 10), 30)
        ws.column_dimensions[L].width = width

        for row in range(2, ws.max_row + 1):
            cell = ws.cell(row=row, column=i)
            if name in MONEY:
                v = str(cell.value or '').replace(',', '').strip()
                if v and v.lstrip('>').replace('.', '', 1).isdigit() and not v.startswith('>'):
                    cell.value = float(v)
                    cell.number_format = '$#,##0'
                cell.alignment = Alignment(horizontal='right', vertical='top')
            elif name in INTS:
                v = str(cell.value or '').strip()
                if v.isdigit():
                    cell.value = int(v)
                cell.alignment = Alignment(horizontal='right', vertical='top')
            elif name in WIDE:
                cell.alignment = Alignment(vertical='top', wrap_text=True)
            else:
                cell.alignment = Alignment(vertical='top')
            cell.border = Border(bottom=thin)

    # highlight non-success outcomes so failures are impossible to miss
    if 'Outcome' in hdr:
        oc = hdr.index('Outcome') + 1
        red = PatternFill('solid', fgColor='F8CBAD')
        for row in range(2, ws.max_row + 1):
            if str(ws.cell(row=row, column=oc).value).strip().lower() != 'success':
                for i in range(1, len(hdr) + 1):
                    ws.cell(row=row, column=i).fill = red
    if 'Status' in hdr:
        sc = hdr.index('Status') + 1
        amber = PatternFill('solid', fgColor='FFE699')
        for row in range(2, ws.max_row + 1):
            if 'slip' in str(ws.cell(row=row, column=sc).value).lower():
                for i in range(1, len(hdr) + 1):
                    ws.cell(row=row, column=i).fill = amber
    return ws

def main():
    wb = Workbook()
    for n, (path, title, colour) in enumerate(TABS):
        if not os.path.exists(path):
            print('skip missing', path); continue
        ws = add_tab(wb, path, title, colour, first=(n == 0))
        print(f'{title}: {ws.max_row-1} data rows, {ws.max_column} cols')
    wb.save('RKLB_Launch_Tracker.xlsx')
    print('wrote RKLB_Launch_Tracker.xlsx')

if __name__ == '__main__':
    main()
