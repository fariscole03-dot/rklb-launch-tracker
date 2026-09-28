# -*- coding: utf-8 -*-
"""RICH backfill builder: parsed wiki data + verified primary sources -> tracker CSVs."""
import json, re, csv, datetime, os

SP='/tmp/claude-0/-home-user-rklb-launch-tracker/8fa36831-ce9d-5f77-a8a7-81692d2da751/scratchpad/'
OUT='/home/user/rklb-launch-tracker/data/'
RUN_DATE='2026-09-28'

P=json.load(open(SP+'parsed.json'))
FURL=json.load(open(SP+'flight_urls.json'))

WIKI='https://en.wikipedia.org/wiki/List_of_Electron_launches'
Q2_10Q='https://www.sec.gov/Archives/edgar/data/0001819994/000181999426000062/rklb-20260630.htm'

# Official Rocket Lab mission-success releases confirmed on the newsroom this run
OFFICIAL={
 93:'https://rocketlabcorp.com/updates/mission-success-rocket-lab-launches-93rd-electron-mission/',
 94:'https://investors.rocketlabcorp.com/news-releases/news-release-details/mission-success-rocket-lab-launches-94th-electron-mission',
 95:'https://rocketlabcorp.com/updates/mission-success-rocket-lab-launches-95th-electron-mission/',
 96:'https://rocketlabcorp.com/updates/mission-success-rocket-lab-launches-96th-electron-mission/',
 97:'https://rocketlabcorp.com/updates/mission-success-rocket-lab-launches-97th-electron-mission/',
}

MONTHS={m:i+1 for i,m in enumerate(['January','February','March','April','May','June','July',
        'August','September','October','November','December'])}

def parse_date(s):
    """'25 May 2017, 04:20' / '4 July 2020 21:19:36' -> (iso_date, time_str)"""
    s=s.replace(',',' ')
    s=re.sub(r'\s+',' ',s).strip()
    m=re.match(r'(\d{1,2}) ([A-Za-z]+) (\d{4})(?:\s+(\d{1,2}:\d{2}(?::\d{2})?))?', s)
    if not m: return '', ''
    d,mo,y,tm=m.groups()
    if mo not in MONTHS: return '', ''
    return f"{int(y):04d}-{MONTHS[mo]:02d}-{int(d):02d}", (tm or '')

def fnum(r):
    m=re.search(r'\d+', r.get('flight_no','') or '')
    return int(m.group()) if m else None

SITE={'Mahia, LC-1A':'LC-1 (Mahia, NZ) - Pad A',
      'Mahia, LC-1B':'LC-1 (Mahia, NZ) - Pad B',
      'MARS, LC-2':'LC-2 (Wallops, VA)'}

RECOV={'No attempt':'None attempted',
       'Success':'Attempted-recovered',
       'Success (Ocean landing)':'Attempted-recovered',
       'Controlled (atmosphere test)':'None attempted',
       'Partial failure (aerial capture)':'Attempted-recovered'}
RECOV_NOTE={'Controlled (atmosphere test)':'Instrumented controlled re-entry test; no recovery attempted.',
            'Partial failure (aerial capture)':'Helicopter mid-air capture not completed; booster recovered from the ocean.',
            'Success (Ocean landing)':'Booster recovered after ocean splashdown.'}

# --- Estimated Electron revenue per launch, by era. Basis stated per row. ---
ASP={2017:None,2018:5.0,2019:5.0,2020:5.0,2021:6.5,2022:6.5,2023:7.5,2024:7.5,2025:8.3,2026:9.0}
ASP_BASIS={
 5.0:"est. basis: Rocket Lab-stated Electron price of ~US$5M per flight in this era (public statements c.2019); confidence medium.",
 6.5:"est. basis: interpolation between Rocket Lab's ~$5M (2019) and ~$7.5M (2023) stated Electron pricing; confidence low.",
 7.5:"est. basis: Rocket Lab target/list price of ~US$7.5M per Electron (stated 2023); confidence medium.",
 8.3:"est. basis: interpolation between the $7.5M 2023-24 list price and the $9.0M 2026 realised average; confidence low.",
 9.0:("est. basis: derived from RKLB Q2-2026 10-Q - Launch Services revenue of $108.249M for H1-2026 "
      "divided by the 12 Electron-family launches flown in H1-2026 = ~$9.0M per launch; confidence medium."),
}
HASTE_EST=15.0
HASTE_BASIS=("est. basis: only disclosed HASTE-class anchor is the 27-Jul-2026 USSF/RSLP award of $266M for up to 18 "
             "suborbital missions (~$14.8M per mission at 18; ~$22.2M if only the 12 firm missions fly). Applied to all "
             "HASTE missions; confidence LOW for pre-2026 missions, which were contracted separately and are undisclosed.")

# Verified contract-announcement attributions (flight -> (date, note))
CONTRACT={
 4:('', 'Booked under NASA Venture Class Launch Services (VCLS); $6.9M fixed-price demonstration launch award (2015).'),
 5:('2019-01-22','Rocket Lab press release announcing the dedicated DARPA mission.'),
 9:('2019-09-30','Rocket Lab press release announcing the dedicated Astro Digital mission.'),
 17:('2020-11-24','Rocket Lab press release announcing the first dedicated Synspective mission.'),
 27:('2020-02','NASA awarded the CAPSTONE dedicated launch to Rocket Lab in Feb 2020; value $9.95M disclosed.'),
 33:('2022-04-19','HawkEye 360 multi-launch contract (announced 19-Apr-2022).'),
 67:('2022-04-19','HawkEye 360 multi-launch contract (announced 19-Apr-2022).'),
 34:('2023-02-28','Capella Space four-launch multi-launch deal (announced 28-Feb-2023).'),
 40:('2023-02-28','Capella Space four-launch multi-launch deal (announced 28-Feb-2023).'),
 41:('2023-02-28','Capella Space four-launch multi-launch deal (announced 28-Feb-2023).'),
 52:('2023-02-28','Capella Space four-launch multi-launch deal (announced 28-Feb-2023).'),
 55:('2023-09-12','First of four HASTE missions for Leidos under MACH-TB (deal announced 12-Sep-2023).'),
 57:('2023-08-08','Confidential HASTE booking announced 8-Aug-2023.'),
 75:('2023-11-08','Attributed to the DIU HASTE booking announced 8-Nov-2023; attribution medium confidence.'),
 82:('2023-11-08','Attributed to the DIU HASTE booking announced 8-Nov-2023; attribution medium confidence.'),
}
# Disclosed per-mission revenue (only figures explicitly stated by RL / filings / the customer agency)
DISCLOSED={
 4:(6900000,'NASA VCLS fixed-price award of $6.9M for this dedicated demonstration launch.'),
 27:(9950000,'NASA CAPSTONE dedicated launch contract valued at $9.95M.'),
}

UNDISCLOSED_TOKENS=('unknown','confidential','undisclosed','classified')
INFER={
 57:'Likely a U.S. DoD or allied hypersonic-test customer, given the HASTE suborbital profile from LC-2 Wallops and the confidential booking announced 8-Aug-2023. Confidence: medium.',
 71:'Likely a U.S. DoD hypersonic test, probably under the MACH-TB programme (Leidos) given the HASTE profile from LC-2 Wallops. Confidence: low-medium.',
 72:'Likely a U.S. DoD hypersonic test, probably under the MACH-TB programme (Leidos) given the HASTE profile from LC-2 Wallops. Confidence: low-medium.',
 86:'Likely a U.S. DoD hypersonic test under MACH-TB or a DIU booking, given the HASTE profile from LC-2 Wallops. Confidence: low.',
 89:'Likely a U.S. DoD hypersonic test under MACH-TB or a DIU booking, given the HASTE profile from LC-2 Wallops. Confidence: low.',
}

def norm_customers(c, f):
    c=re.sub(r'\bBlackSky\|BlackSky\b','BlackSky',c)   # source typo on the Wikipedia page
    c=re.sub(r'\s*;\s*',' ; ',c).strip(' ;')
    c=re.sub(r'\s{2,}',' ',c)
    return c

def disclosure(c, f):
    cl=c.lower()
    if any(tok in cl for tok in UNDISCLOSED_TOKENS) or cl.strip() in ('','n/a'):
        return 'Undisclosed'
    return 'Disclosed'

rows=[]
for kind,src in (('Electron',P['orbital']),('HASTE',P['haste'])):
    for r in src:
        f=fnum(r)
        iso,tm=parse_date(r['date'])
        yr=int(iso[:4]) if iso else None
        cust=norm_customers(r['customers'], f)
        disc=disclosure(cust, f)
        site=SITE.get(r['site'], r['site'])
        recov_raw=r['recovery']
        notes=[]
        if r['notes']: notes.append(r['notes'])
        if recov_raw in RECOV_NOTE: notes.append(RECOV_NOTE[recov_raw])
        if disc=='Undisclosed' and f in INFER: notes.append('INFERENCE: '+INFER[f])
        # dedicated vs rideshare
        ncust=len([x for x in cust.split(' ; ') if x.strip()])
        if f==1: ded='N/A (test flight)'
        elif kind=='HASTE': ded='Dedicated'
        elif 'rideshare' in (r['notes'] or '').lower() or ncust>1: ded='Rideshare'
        else: ded='Dedicated'
        # revenue
        rev_d, rev_e = '', ''
        if f in DISCLOSED:
            rev_d=DISCLOSED[f][0]; notes.append(DISCLOSED[f][1])
        if kind=='HASTE':
            rev_e=int(HASTE_EST*1e6); notes.append(HASTE_BASIS)
        elif f in (1,2):
            notes.append('Development/test flight - no commercial launch revenue assumed; estimate left blank.')
        elif yr and ASP.get(yr):
            rev_e=int(ASP[yr]*1e6); notes.append(ASP_BASIS[ASP[yr]])
        ca_date, ca_note = CONTRACT.get(f, ('',''))
        if ca_note: notes.append(ca_note)
        # sources
        srcs=[]
        if f in OFFICIAL: srcs.append(OFFICIAL[f])
        srcs += FURL.get(str(f), [])
        srcs.append(WIKI+' (secondary, cross-check)')
        rows.append({
          'Flight #': f,
          'Launch Date (UTC)': iso,
          'Launch Time (UTC)': tm,
          'Vehicle': kind,
          'Mission Name': r['name'].strip().strip('.').strip().strip('"').strip(),
          'Customer(s)': cust,
          'Customer Disclosure': disc,
          'Launch Site': site,
          'Dedicated / Rideshare': ded,
          'Outcome': r['outcome'] or '',
          'Recovery': RECOV.get(recov_raw, recov_raw or 'None attempted'),
          'Contract Announcement Date': ca_date,
          'Revenue - Disclosed ($)': rev_d,
          'Revenue - Estimated ($)': rev_e,
          'Direct Mission Costs ($)': '',
          'Payload': r['payload'],
          'Payload Mass': r['mass'],
          'Destination': r.get('destination',''),
          'Sources': ' | '.join(dict.fromkeys(srcs)),
          'Notes': ' '.join(notes).strip(),
        })

rows.sort(key=lambda x: x['Flight #'])
COLS=list(rows[0].keys())
with open(OUT+'completed_launches.csv','w',newline='',encoding='utf-8') as fh:
    w=csv.DictWriter(fh,fieldnames=COLS); w.writeheader(); w.writerows(rows)
print('completed_launches.csv rows:',len(rows))
json.dump(rows,open(SP+'completed.json','w'),indent=1)
