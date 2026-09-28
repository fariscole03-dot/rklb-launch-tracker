import re, json, sys

t = open('/tmp/claude-0/-home-user-rklb-launch-tracker/8fa36831-ce9d-5f77-a8a7-81692d2da751/scratchpad/electron_noref.wiki').read()
lines = t.split('\n')

# --- locate sections by heading line numbers ---
heads = [(i, l.strip()) for i, l in enumerate(lines) if l.strip().startswith('==')]
def sect(name):
    for k,(i,h) in enumerate(heads):
        if h.strip('= ').strip() == name:
            end = heads[k+1][0] if k+1 < len(heads) else len(lines)
            return i, end
    raise KeyError(name)

def strip_refs(s):
    # remove <ref ...>...</ref> and <ref ... />
    prev=None
    while prev!=s:
        prev=s
        s=re.sub(r'<ref[^>]*?/>','',s)
        s=re.sub(r'<ref[^>]*?>.*?</ref>','',s,flags=re.S)
    s=re.sub(r'<ref[^>]*?>.*','',s,flags=re.S)  # unterminated
    return s

def clean(s):
    s = strip_refs(s)
    s = re.sub(r'<br\s*/?>', ' ', s)
    s = re.sub(r'&nbsp;', ' ', s)
    # wikilinks
    s = re.sub(r'\[\[[^\]|]*\|([^\]]*)\]\]', r'\1', s)
    s = re.sub(r'\[\[([^\]]*)\]\]', r'\1', s)
    # generic template resolution (innermost-first)
    PASSTHRU_LAST = {'visible anchor','vanchor','unofficial2','unofficial','n/a','na','nowrap',
                     'sort','small','abbr','okay','partial','no2','yes2','center','nts'}
    STATUS = {'success':'Success','failure':'Failure','partial failure':'Partial failure',
              'no attempt':'No attempt','tba':'TBA','tbd':'TBD','planned':'Planned',
              'dts':'','cslist':''}
    def resolve(txt):
        for _ in range(40):
            m2 = re.search(r'\{\{([^{}]*)\}\}', txt)
            if not m2: break
            inner = m2.group(1)
            parts = inner.split('|')
            nm = parts[0].strip().lower()
            args = [p for p in parts[1:]]
            if nm in ('cvt','convert'):
                rep = (args[0].strip()+' '+args[1].strip()) if len(args)>1 else (args[0].strip() if args else '')
            elif nm in STATUS:
                rep = STATUS[nm]
            elif nm in ('flatlist','unbulleted list','ubl','plainlist','hlist'):
                rep = '; '.join(a.strip().lstrip('*').strip() for a in args if a.strip())
            elif nm in PASSTHRU_LAST:
                named=[a for a in args if '=' not in a.split('=')[0][:0]]
                rep = args[-1].strip() if args else ''
            elif nm.startswith('cite') or nm in ('r','refn','efn','sfn'):
                rep = ''
            else:
                rep = args[-1].strip() if args else ''
            txt = txt[:m2.start()] + rep + txt[m2.end():]
        return txt
    s = resolve(s)
    # templates
    s = re.sub(r'\{\{(?:cvt|convert)\|([^|}]*)\|([^|}]*)(\|[^}]*)?\}\}', r'\1 \2', s)
    s = re.sub(r'\{\{Success\}\}', 'Success', s, flags=re.I)
    s = re.sub(r'\{\{Failure\}\}', 'Failure', s, flags=re.I)
    s = re.sub(r'\{\{Partial(?:\s*failure)?\}\}', 'Partial failure', s, flags=re.I)
    s = re.sub(r'\{\{Partial\|([^}]*)\}\}', r'Partial (\1)', s, flags=re.I)
    s = re.sub(r'\{\{No attempt\}\}', 'No attempt', s, flags=re.I)
    s = re.sub(r'\{\{n/?a\}\}', 'N/A', s, flags=re.I)
    s = re.sub(r'\{\{(?:Yes|No)\|([^}]*)\}\}', r'\1', s)
    s = re.sub(r'\{\{(?:Yes|Success2|nowrap)\}\}', '', s)
    s = re.sub(r'\{\{flatlist\|?', '', s, flags=re.I)
    s = re.sub(r'\{\{unbulleted list\|?', '', s, flags=re.I)
    s = re.sub(r'\{\{sort\|[^|}]*\|([^}]*)\}\}', r'\1', s, flags=re.I)
    s = re.sub(r'\{\{[Cc]ite[^}]*\}\}', '', s)
    s = re.sub(r'\{\{TBA\}\}', 'TBA', s, flags=re.I)
    s = re.sub(r'\{\{TBD\}\}', 'TBD', s, flags=re.I)
    s = re.sub(r'\[https?://\S+\s+([^\]]*)\]', r'\1', s)
    s = re.sub(r'\[https?://\S+\]', '', s)
    # leftover braces/markup
    s = s.replace("'''",'').replace("''",'')
    s = re.sub(r'\}\}','',s); s = re.sub(r'\{\{','',s)
    s = re.sub(r'\|\s*$','',s)
    s = re.sub(r'^\s*\*\s*','',s,flags=re.M)
    s = re.sub(r'\s*\n\s*', '; ', s.strip())
    s = re.sub(r'nowrap\s*\|','',s)
    s = re.sub(r'rowspan=\d+\s*\|','',s)
    s = re.sub(r'colspan=[\"\']?\d+[\"\']?\s*\|','',s)
    s = re.sub(r'\s{2,}',' ',s)
    s = re.sub(r'(;\s*)+',
               '; ', s)
    return s.strip(' ;\t')

def depth_delta(l):
    return (l.count('{{') - l.count('}}')), (l.count('[[') - l.count(']]'))

def parse_table(seg, ncols):
    """Parse launch rows out of a wikitable segment."""
    recs = []
    cur = None
    cells = None
    buf = None
    bd = 0; ld = 0
    intable = False
    for raw in seg:
        l = raw.rstrip()
        ls = l.strip()
        # new launch row: '! rowspan=2 | N' possibly with refs
        m = re.match(r'^!\s*rowspan=[\"\']?\d+[\"\']?\s*\|(.*)$', ls)
        if m:
            if cur is not None:
                if buf is not None: cells.append(buf)
                cur['cells'] = cells
                recs.append(cur)
            fno = clean(m.group(1))
            cur = {'flight_no': fno, 'notes': ''}
            cells = []; buf = None; bd = 0; ld = 0
            continue
        if cur is None:
            continue
        # notes row
        mn = re.match(r'^\|\s*colspan=[\"\']?\d+[\"\']?\s*\|(.*)$', ls)
        if mn and bd == 0 and ld == 0:
            if buf is not None:
                cells.append(buf); buf = None
            cur['notes_raw'] = mn.group(1)
            cur['_in_notes'] = True
            continue
        if cur.get('_in_notes'):
            if ls == '|-' or ls == '|}' or ls == '':
                if ls in ('|-','|}'):
                    cur['_in_notes'] = False
                continue
            cur['notes_raw'] = cur.get('notes_raw','') + '\n' + ls
            continue
        if ls in ('|-', '|}'):
            continue
        if ls.startswith('|') and bd == 0 and ld == 0:
            if buf is not None:
                cells.append(buf)
            buf = ls[1:]
        else:
            if buf is None:
                continue
            buf += '\n' + ls
        db, dl = depth_delta(ls)
        bd += db; ld += dl
        if bd < 0: bd = 0
        if ld < 0: ld = 0
    if cur is not None:
        if buf is not None: cells.append(buf)
        cur['cells'] = cells
        recs.append(cur)
    return recs

ORB_COLS = ['name','date','site','payload','mass','destination','customers','outcome','recovery']
HASTE_COLS = ['name','date','site','payload','mass','customers','outcome','recovery']

def build(recs, cols, vehicle_default):
    out = []
    for r in recs:
        c = r.get('cells', [])
        d = {'flight_no': r['flight_no']}
        for i, k in enumerate(cols):
            d[k] = clean(c[i]) if i < len(c) else ''
        d['ncells'] = len(c)
        d['notes'] = clean(r.get('notes_raw',''))
        d['vehicle_guess'] = vehicle_default
        out.append(d)
    return out

result = {}
# orbital year sections
orb = []
for yr in ['2017–2018','2019','2020','2021','2022','2023','2024','2025','2026']:
    s,e = sect(yr)
    rs = parse_table(lines[s:e], 10)
    got = build(rs, ORB_COLS, 'Electron')
    for g in got: g['year_section']=yr
    orb += got
result['orbital'] = orb

s,e = sect('Upcoming orbital launches')
# includes subsection 2026 – due
s2,e2 = sect('2026 – due')
up = build(parse_table(lines[s2:e2], 10), ORB_COLS, 'Electron')
result['upcoming'] = up

s,e = sect('Completed launches')
haste = build(parse_table(lines[s:e], 9), HASTE_COLS, 'HASTE')
result['haste'] = haste

s,e = sect('Planned launches')
hastep = build(parse_table(lines[s:e], 9), HASTE_COLS, 'HASTE')
result['haste_planned'] = hastep

json.dump(result, open('/tmp/claude-0/-home-user-rklb-launch-tracker/8fa36831-ce9d-5f77-a8a7-81692d2da751/scratchpad/parsed.json','w'), indent=1)
for k,v in result.items():
    print(k, len(v))

# ---- second pass: forward-looking tables use '| rowspan="2" |' and 5 cols ----
def parse_fwd(seg, cols):
    recs=[]; cur=None; cells=None; buf=None
    for raw in seg:
        ls=raw.strip()
        m=re.match(r'^\|\s*rowspan=["\']?\d+["\']?\s*\|(.*)$', ls)
        if m:
            if cur is not None:
                if buf is not None: cells.append(buf)
                cur['cells']=cells; recs.append(cur)
            cur={'c0':m.group(1)}; cells=[m.group(1)]; buf=None
            cur['_notes']=''
            continue
        if cur is None: continue
        mn=re.match(r'^\|\s*colspan=["\']?\d+["\']?\s*\|(.*)$', ls)
        if mn:
            if buf is not None: cells.append(buf); buf=None
            cur['_notes']=mn.group(1); cur['_innotes']=True
            continue
        if cur.get('_innotes'):
            if ls in ('|-','|}'):
                cur['_innotes']=False
            elif ls:
                cur['_notes']+=' '+ls
            continue
        if ls in ('|-','|}',''): continue
        if ls.startswith('|'):
            if buf is not None: cells.append(buf)
            buf=ls[1:]
        else:
            if buf is not None: buf+='\n'+ls
    if cur is not None:
        if buf is not None: cells.append(buf)
        cur['cells']=cells; recs.append(cur)
    out=[]
    for r in recs:
        c=r['cells']; d={}
        for i,k in enumerate(cols):
            d[k]=clean(c[i]) if i<len(c) else ''
        d['ncells']=len(c); d['notes']=clean(r.get('_notes',''))
        out.append(d)
    return out

FWD_COLS=['date','site','payload','destination','customer']
HFWD_COLS=['date','site','payload','apogee','customer']
s,e=sect('2026 – due'); result['upcoming']=parse_fwd(lines[s:e],FWD_COLS)
s,e=sect('Planned launches'); result['haste_planned']=parse_fwd(lines[s:e],HFWD_COLS)
json.dump(result,open('/tmp/claude-0/-home-user-rklb-launch-tracker/8fa36831-ce9d-5f77-a8a7-81692d2da751/scratchpad/parsed.json','w'),indent=1)
print('--- final ---')
for k,v in result.items(): print(k,len(v))
