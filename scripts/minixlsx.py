# -*- coding: utf-8 -*-
"""Minimal .xlsx writer using a shared-string table.

openpyxl emits inline strings, which roughly triples the sheet XML and prevents the
repeated source citations from collapsing. This writer keeps the workbook small enough
to email while staying a valid, fully formatted spreadsheet.
"""
import zipfile
from xml.sax.saxutils import escape

def _col(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

class Sheet:
    def __init__(self, name, cols, rows, widths=None, money_cols=(), wrap_cols=(), center_cols=()):
        self.name, self.cols, self.rows = name, cols, rows
        self.widths = widths or [14] * len(cols)
        self.money_cols, self.wrap_cols, self.center_cols = set(money_cols), set(wrap_cols), set(center_cols)

# style ids: 0 default, 1 header, 2 wrap/top, 3 money, 4 center/top, 5 plain top
STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="1"><numFmt numFmtId="164" formatCode="#,##0;[Red]-#,##0"/></numFmts>
<fonts count="2"><font><sz val="10"/><name val="Calibri"/></font>
<font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts>
<fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF1F3864"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="6">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center" wrapText="1"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="right" vertical="top"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="top"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="top"/></xf>
</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""

def write(path, sheets):
    sst, sst_order = {}, []
    def sid(v):
        if v not in sst:
            sst[v] = len(sst_order)
            sst_order.append(v)
        return sst[v]

    sheet_xml = []
    for sh in sheets:
        parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                 '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
                 '<sheetPr><outlinePr summaryBelow="1" summaryRight="1"/></sheetPr>',
                 '<dimension ref="A1:%s%d"/>' % (_col(len(sh.cols)), len(sh.rows) + 1),
                 '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
                 'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>',
                 '<sheetFormatPr defaultRowHeight="13"/>', '<cols>']
        for i, w in enumerate(sh.widths, 1):
            parts.append('<col min="%d" max="%d" width="%d" customWidth="1"/>' % (i, i, w))
        parts.append('</cols><sheetData>')
        parts.append('<row r="1" ht="34" customHeight="1">')
        for i, c in enumerate(sh.cols, 1):
            parts.append('<c r="%s1" s="1" t="s"><v>%d</v></c>' % (_col(i), sid(str(c))))
        parts.append('</row>')
        for ri, row in enumerate(sh.rows, 2):
            parts.append('<row r="%d">' % ri)
            for i, v in enumerate(row, 1):
                if v is None or v == "":
                    continue
                ref = "%s%d" % (_col(i), ri)
                if i in sh.money_cols and isinstance(v, (int, float)):
                    parts.append('<c r="%s" s="3"><v>%s</v></c>' % (ref, v))
                elif isinstance(v, (int, float)) and not isinstance(v, bool):
                    st = 4 if i in sh.center_cols else 5
                    parts.append('<c r="%s" s="%d"><v>%s</v></c>' % (ref, st, v))
                else:
                    st = 2 if i in sh.wrap_cols else (4 if i in sh.center_cols else 5)
                    parts.append('<c r="%s" s="%d" t="s"><v>%d</v></c>' % (ref, st, sid(str(v))))
            parts.append('</row>')
        parts.append('</sheetData>')
        parts.append('<autoFilter ref="A1:%s%d"/>' % (_col(len(sh.cols)), len(sh.rows) + 1))
        parts.append('</worksheet>')
        sheet_xml.append("".join(parts))

    sst_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="%d" uniqueCount="%d">'
               % (len(sst_order), len(sst_order))
               + "".join("<si><t xml:space=\"preserve\">%s</t></si>" % escape(s) for s in sst_order)
               + "</sst>")

    wb = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>']
    for i, sh in enumerate(sheets, 1):
        wb.append('<sheet name="%s" sheetId="%d" r:id="rId%d"/>' % (escape(sh.name), i, i))
    wb.append('</sheets></workbook>')

    rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i in range(1, len(sheets) + 1):
        rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                    'relationships/worksheet" Target="worksheets/sheet%d.xml"/>' % (i, i))
    n = len(sheets)
    rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/styles" Target="styles.xml"/>' % (n + 1))
    rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/sharedStrings" Target="sharedStrings.xml"/>' % (n + 2))
    rels.append('</Relationships>')

    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>',
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.'
          'spreadsheetml.sheet.main+xml"/>']
    for i in range(1, len(sheets) + 1):
        ct.append('<Override PartName="/xl/worksheets/sheet%d.xml" ContentType="application/vnd.'
                  'openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' % i)
    ct.append('<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.'
              'spreadsheetml.styles+xml"/>')
    ct.append('<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-'
              'officedocument.spreadsheetml.sharedStrings+xml"/>')
    ct.append('</Types>')

    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                 '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                 'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels", root_rels)
        z.writestr("xl/workbook.xml", "".join(wb))
        z.writestr("xl/_rels/workbook.xml.rels", "".join(rels))
        z.writestr("xl/styles.xml", STYLES)
        z.writestr("xl/sharedStrings.xml", sst_xml)
        for i, x in enumerate(sheet_xml, 1):
            z.writestr("xl/worksheets/sheet%d.xml" % i, x)
