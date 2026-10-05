#!/usr/bin/env python3
"""Build data/completed_launches.csv from the parsed Wikipedia launch tables.

Launch counts produced here were cross-checked against Rocket Lab's own 10-K/10-Q
"launch missions" counts: 2021=6, 2022=9, 2023=10, 2024=16, 2025=21 -- all match,
which also confirms HASTE flights count as launch missions for revenue purposes.
"""
import json, re, csv, datetime, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else 'parsed.json'
WIKI = 'https://en.wikipedia.org/wiki/List_of_Electron_launches'

# Estimated launch-services revenue per mission, by calendar year.
# 2021-2025: disclosed annual Launch Services revenue / disclosed launch-mission count (10-K).
# 2026: H1 2026 disclosed Launch Services revenue $108.249M / 12 missions flown in H1 (10-Q).
# 2018-2020: pre-IPO, no segment disclosure -> contemporaneous Electron list price, LOW confidence.
REV_EST = {
    2017: (None, 'Maiden flight test, no customer revenue'),
    2018: (5_000_000,  'est. - contemporaneous Electron list price ~$5M; pre-IPO, no segment disclosure; confidence LOW'),
    2019: (6_000_000,  'est. - contemporaneous Electron list price ~$6M; pre-IPO, no segment disclosure; confidence LOW'),
    2020: (6_000_000,  'est. - contemporaneous Electron list price ~$6M; pre-IPO, no segment disclosure; confidence LOW'),
    2021: (6_500_000,  'est. - FY2021 launch services rev $39.0M / 6 missions (FY2022 10-K); confidence MEDIUM'),
    2022: (6_744_000,  'est. - FY2022 launch services rev $60.7M / 9 missions (FY2022 10-K); confidence MEDIUM'),
    2023: (7_190_000,  'est. - FY2023 launch services rev $71.9M / 10 missions (FY2023 10-K); confidence MEDIUM'),
    2024: (7_831_000,  'est. - FY2024 launch services rev $125.3M / 16 missions (FY2025 10-K); confidence MEDIUM'),
    2025: (9_476_000,  'est. - FY2025 launch services rev $199.0M / 21 missions (FY2025 10-K); confidence MEDIUM'),
    2026: (9_021_000,  'est. - H1 2026 launch services rev $108.249M / 12 missions (Q2 2026 10-Q); Q3 2026 not yet reported; confidence MEDIUM'),
}

SITE = {
    'Mahia, LC-1A': 'LC-1A (Mahia, NZ)',
    'Mahia, LC-1B': 'LC-1B (Mahia, NZ)',
    'MARS, LC-2':   'LC-2 (Wallops/MARS, VA)',
}
# Spec enum is None attempted / Attempted-recovered / Attempted-lost. Two Wikipedia
# values do not map cleanly, so they are rendered accurately rather than forced:
# flights 10 & 11 flew guided re-entry data-gathering tests with NO recovery attempt
# (the stage was not recovered), and the two aerial-capture flights were caught briefly,
# released, then recovered from the ocean.
RECOVERY = {
    'No attempt': 'None attempted',
    'Success (Ocean landing)': 'Attempted-recovered',
    'Controlled (atmosphere test)': 'None attempted (controlled re-entry test; stage not recovered)',
    'Partial failure (aerial capture)': 'Attempted-recovered (aerial capture aborted; stage recovered from ocean)',
}
UNDISC = ('unknown', 'confidential', 'undisclosed', 'classified')

def fix(s):
    s = re.sub(r'^nowrap \| ', '', s).strip()
    # collapse "X|X" link artifacts
    s = re.sub(r'\b([^|;]+)\|\1\b', r'\1', s)
    return s.strip()

def parse_dt(s):
    m = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', s.strip())
    d = datetime.datetime.strptime(' '.join(m.groups()), '%d %B %Y').date()
    t = re.search(r'(\d{2}:\d{2})', s)
    return d, (t.group(1) if t else '')

def infer_disclosure(cust):
    low = cust.lower()
    if any(k in low for k in UNDISC) or not cust:
        return 'Undisclosed'
    return 'Disclosed'

def main():
    d = json.load(open(SRC))
    recs = []
    for r in d['orbital']:
        c = r['cells']
        recs.append(dict(flight=r['flight'], vehicle='Electron', name=c[0], date=c[1],
                         site=c[2], payload=c[3], mass=c[4], dest=c[5], cust=c[6],
                         outcome=c[7], recov=c[8], notes=r['notes'], urls=r['urls']))
    for r in d['haste']:
        c = r['cells']
        recs.append(dict(flight=r['flight'], vehicle='HASTE', name=c[0], date=c[1],
                         site=c[2], payload=c[3], mass=c[4], dest='Suborbital', cust=c[5],
                         outcome=c[6], recov=c[7], notes=r['notes'], urls=r['urls']))
    recs.sort(key=lambda x: x['flight'])

    hdr = ['Flight #','Launch Date (UTC)','Vehicle','Mission Name','Customer(s)',
           'Customer Disclosure','Launch Site','Dedicated / Rideshare','Outcome','Recovery',
           'Contract Announcement Date','Revenue - Disclosed ($)','Revenue - Estimated ($)',
           'Direct Mission Costs ($)','Sources','Notes']
    out = []
    for r in recs:
        dt, tm = parse_dt(r['date'])
        cust = fix(r['cust'])
        site = SITE.get(fix(r['site']), fix(r['site']))
        outcome = r['outcome'].capitalize()
        disclosure = infer_disclosure(cust)

        # Dedicated vs rideshare: multiple distinct customers => rideshare (inferred)
        ncust = len([x for x in cust.split(';') if x.strip()])
        if 'flight test' in cust.lower():
            ded = 'Dedicated (test flight)'
        else:
            ded = 'Rideshare' if ncust > 1 else 'Dedicated'

        est, basis = REV_EST[dt.year]
        nt = re.sub(r'\s*\|\}\s*$', '', r['notes']).strip()
        nt = re.sub(r'\s*\|\}\s*', ' ', nt).strip()
        notes = [nt] if nt else []
        if r['payload'] and r['payload'] not in ('None',):
            notes.append(f"Payload: {r['payload']}" + (f" ({r['mass']})" if r['mass'] and 'nknown' not in r['mass'] else ''))
        if r['dest'] and r['dest'] != 'Suborbital':
            notes.append(f"Destination: {r['dest']}")
        if ncust > 1:
            notes.append('Dedicated/Rideshare inferred from multiple named customers.')
        if disclosure == 'Undisclosed':
            if r['vehicle'] == 'HASTE':
                notes.append('INFERENCE: likely US DoD / hypersonic test customer (MDA, DIU or prime '
                             'contractor) given HASTE suborbital profile, LC-2 Wallops launch and classified '
                             'payload mass. Confidence: MEDIUM-HIGH.')
            else:
                notes.append('INFERENCE: customer not named by Rocket Lab. Confidence: LOW.')
        if basis:
            notes.append(f'Revenue basis: {basis}')
        if r['vehicle'] == 'HASTE':
            notes.append('HASTE = suborbital Electron derivative; counts as a "launch mission" in '
                         'Rocket Lab launch-services revenue disclosures.')
        srcs = [WIKI] + [u for u in dict.fromkeys(r['urls'])][:2]

        out.append([
            r['flight'], dt.isoformat() + (f' {tm} UTC' if tm else ''), r['vehicle'],
            r['name'].strip('"'), cust, disclosure, site, ded, outcome,
            RECOVERY.get(r['recov'], r['recov']), '', '',
            (est if est is not None else ''), '', ' | '.join(srcs),
            ' '.join(notes).strip(),
        ])

    with open('data/completed_launches.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(out)
    print(f'wrote data/completed_launches.csv rows={len(out)}')

if __name__ == '__main__':
    main()
