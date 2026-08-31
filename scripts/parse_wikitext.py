import re, json, sys

raw = open('electron_raw.txt', encoding='utf-8').read()

def strip_refs(t):
    # remove <ref ...>...</ref> and self-closing
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r'<ref[^>/]*?>.*?</ref>', '', t, flags=re.S)
    t = re.sub(r'<ref[^>]*?/>', '', t)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    return t

def clean(t):
    t = strip_refs(t)
    # wiki links
    t = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', t)
    t = re.sub(r'\[\[([^\]]*)\]\]', r'\1', t)
    # external links [url label]
    t = re.sub(r'\[https?://\S+\s+([^\]]*)\]', r'\1', t)
    t = re.sub(r'\[https?://\S+\]', '', t)
    # templates
    t = re.sub(r'\{\{flatlist\|', '', t, flags=re.I)
    t = re.sub(r'\{\{cvt\|(\d+)\|(\w+)\}\}', r'\1 \2', t, flags=re.I)
    t = re.sub(r'\{\{convert\|(\d+)\|(\w+)\}\}', r'\1 \2', t, flags=re.I)
    t = re.sub(r'\{\{(Success|success)\}\}', 'Success', t)
    t = re.sub(r'\{\{(Failure|failure)\}\}', 'Failure', t)
    t = re.sub(r'\{\{(Partial failure|partial failure|Partial|partial)\}\}', 'Partial failure', t)
    t = re.sub(r'\{\{(No attempt|no attempt)\}\}', 'No attempt', t)
    t = re.sub(r'\{\{unofficial2?\|([^}]*)\}\}', r'\1', t)
    t = re.sub(r'\{\{[Nn]owrap\|([^}]*)\}\}', r'\1', t)
    t = re.sub(r'\{\{[Vv]isible anchor\|([^}]*)\}\}', r'\1', t)
    t = re.sub(r'\{\{[^}]*\}\}', ' ', t)
    t = t.replace('&nbsp;', ' ').replace("'''", '').replace("''", '')
    t = t.replace('nowrap |', '').replace('nowrap|', '')
    t = re.sub(r'^\s*\*\s*', '', t, flags=re.M)
    t = re.sub(r'<br\s*/?>', ' ', t)
    t = re.sub(r'</?small>', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip(' |')

# Split into sections
sec_re = re.compile(r'^===?\s*(.+?)\s*===?\s*$', re.M)
marks = [(m.start(), m.group(1)) for m in sec_re.finditer(raw)]
sections = {}
for i, (pos, name) in enumerate(marks):
    end = marks[i+1][0] if i+1 < len(marks) else len(raw)
    sections[name] = raw[pos:end]

print("SECTIONS:", list(sections.keys()))

def split_cells(block):
    """block: lines of a table row after the flight-number line, up to |-"""
    cells = []
    cur = []
    depth = 0
    for line in block:
        stripped = line.strip()
        starts_cell = stripped.startswith('|') and not stripped.startswith('|-') and not stripped.startswith('||')
        if starts_cell and depth == 0:
            if cur:
                cells.append('\n'.join(cur))
            cur = [stripped[1:]]
        elif stripped.startswith('||') and depth == 0:
            if cur:
                cells.append('\n'.join(cur))
            cur = [stripped[2:]]
        else:
            cur.append(line)
        depth += line.count('{{') - line.count('}}')
        if depth < 0:
            depth = 0
    if cur:
        cells.append('\n'.join(cur))
    return cells

def parse_year_table(text):
    lines = text.split('\n')
    out = []
    i = 0
    while i < len(lines):
        m = re.match(r'^!\s*rowspan\s*=\s*"?2"?\s*\|\s*(.+?)\s*$', lines[i])
        if m:
            flight = clean(m.group(1))
            # collect until line that is exactly |-
            body = []
            i += 1
            while i < len(lines) and lines[i].strip() != '|-':
                body.append(lines[i])
                i += 1
            cells = [clean(c) for c in split_cells(body)]
            # notes row follows
            notes = ''
            if i < len(lines) and lines[i].strip() == '|-':
                i += 1
                nb = []
                while i < len(lines) and not re.match(r'^\s*\|-\s*$', lines[i]) and not lines[i].strip().startswith('|}'):
                    nb.append(lines[i])
                    i += 1
                nt = '\n'.join(nb)
                nt = re.sub(r'^\s*\|\s*colspan\s*=\s*"?\d+"?\s*\|', '', nt.strip())
                notes = clean(nt)
            out.append({'flight': flight, 'cells': cells, 'notes': notes})
        else:
            i += 1
    return out

allrows = []
for name, text in sections.items():
    if re.match(r'^(2017|2018|2019|2020|2021|2022|2023|2024|2025|2026)', name) and 'due' not in name:
        rows = parse_year_table(text)
        for r in rows:
            r['section'] = name
        allrows.extend(rows)

print("TOTAL ORBITAL ROWS:", len(allrows))
json.dump(allrows, open('orbital.json', 'w'), indent=1)
for r in allrows[:2]:
    print(r['flight'], '|', ' || '.join(c[:50] for c in r['cells']))

# ---- HASTE completed ----
haste_txt = sections.get('Completed launches', '')
haste = parse_year_table(haste_txt)
print("\nHASTE ROWS:", len(haste))
for r in haste:
    print(' ', r['flight'], '|', ' || '.join(c[:45] for c in r['cells']))
json.dump(haste, open('haste.json', 'w'), indent=1)

# ---- Upcoming tables (rows start with | rowspan) ----
def parse_upcoming(text):
    lines = text.split('\n')
    out = []
    i = 0
    while i < len(lines):
        m = re.match(r'^\|\s*rowspan\s*=\s*"?2"?\s*\|\s*(.*)$', lines[i])
        if m:
            body = [ '|' + m.group(1) ]
            i += 1
            while i < len(lines) and lines[i].strip() != '|-':
                body.append(lines[i])
                i += 1
            cells = [clean(c) for c in split_cells(body)]
            notes = ''
            if i < len(lines) and lines[i].strip() == '|-':
                i += 1
                nb = []
                while i < len(lines) and not re.match(r'^\s*\|-\s*$', lines[i]) and not lines[i].strip().startswith('|}'):
                    nb.append(lines[i]); i += 1
                nt = re.sub(r'^\s*\|\s*colspan\s*=\s*"?\d+"?\s*\|', '', '\n'.join(nb).strip())
                notes = clean(nt)
            out.append({'cells': cells, 'notes': notes})
        else:
            i += 1
    return out

up = parse_upcoming(sections.get('2026 – due', ''))
print("\nUPCOMING ORBITAL:", len(up))
for r in up:
    print(' ', ' || '.join(c[:45] for c in r['cells']), '::', r['notes'][:90])
json.dump(up, open('upcoming.json', 'w'), indent=1)

hp = parse_upcoming(sections.get('Planned launches', ''))
print("\nPLANNED HASTE:", len(hp))
for r in hp:
    print(' ', ' || '.join(c[:45] for c in r['cells']), '::', r['notes'][:90])
json.dump(hp, open('haste_planned.json', 'w'), indent=1)
