import re, json, html
SP='/tmp/claude-0/-home-user-rklb-launch-tracker/8fa36831-ce9d-5f77-a8a7-81692d2da751/scratchpad/'
t=open(SP+'electron.wiki').read()
lines=t.split('\n')

def strip_refs_inline(s):
    prev=None
    while prev!=s:
        prev=s
        s=re.sub(r'<ref[^>]*?/>','',s)
        s=re.sub(r'<ref[^>]*?>.*?</ref>','',s,flags=re.S)
    return s

# Split the ORIGINAL (with refs) into per-launch blocks so we can harvest the
# citation URLs that belong to each individual flight.
blocks=[]; cur=None
for l in lines:
    ls=l.strip()
    if re.match(r'^!\s*rowspan=["\']?\d+["\']?\s*\|', ls):
        if cur: blocks.append(cur)
        head=strip_refs_inline(re.sub(r'^!\s*rowspan=["\']?\d+["\']?\s*\|','',ls))
        head=re.sub(r'\{\{[^|}]*\|([^}]*)\}\}',r'\1',head)
        m=re.search(r'\d+',head)
        cur={'flight':int(m.group()) if m else None,'text':l+'\n'}
    elif cur is not None:
        if ls == '|}':          # end of this wikitable: close the open block
            blocks.append(cur); cur=None
            continue
        cur['text']+=l+'\n'
blocks.append(cur)

out={}
for b in blocks:
    if not b or b['flight'] is None: continue
    urls=re.findall(r'\|\s*url\s*=\s*(\S+)', b['text'])
    urls=[u.rstrip('|}') for u in urls]
    # rank: Rocket Lab primary first, then reputable press, drop archives
    def score(u):
        ul=u.lower()
        if 'web.archive.org' in ul or 'archive.today' in ul: return 99
        if 'rocketlab' in ul: return 0
        if 'nasa.gov' in ul or 'sec.gov' in ul or 'spaceforce.mil' in ul: return 1
        if 'spacenews' in ul or 'spaceflightnow' in ul or 'nasaspaceflight' in ul: return 2
        return 3
    urls=[u for u in dict.fromkeys(urls) if score(u)<99]
    urls.sort(key=score)
    out.setdefault(b['flight'],[]).extend(urls)
for k in out:
    out[k]=list(dict.fromkeys(out[k]))[:4]
json.dump(out,open(SP+'flight_urls.json','w'),indent=1)
print('flights with harvested URLs:',len(out))
have=sum(1 for k,v in out.items() if v)
print('flights with >=1 usable URL:',have)
print('example f27:',out.get(27))
print('example f97:',out.get(97))
