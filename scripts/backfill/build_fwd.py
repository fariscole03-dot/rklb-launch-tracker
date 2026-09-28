# -*- coding: utf-8 -*-
import json, csv, re
SP='/tmp/claude-0/-home-user-rklb-launch-tracker/8fa36831-ce9d-5f77-a8a7-81692d2da751/scratchpad/'
OUT='/home/user/rklb-launch-tracker/data/'
RUN='2026-09-28'
P=json.load(open(SP+'parsed.json'))
WIKI='https://en.wikipedia.org/wiki/List_of_Electron_launches'
WIKIN='https://en.wikipedia.org/wiki/Rocket_Lab_Neutron'

COLS=['Row Type','Announcement Date','Vehicle','Customer(s)','Customer Disclosure',
      'Number of Launches in booking','Announced Timeframe','Launch Site',
      'Contract Value - Disclosed ($)','Contract Value - Estimated ($)','Status',
      'Timeframe Change History','Sources','Notes']

def hist(tf): return f"{RUN}: initial observation - \"{tf}\""
rows=[]
def add(**k):
    r={c:'' for c in COLS}; r.update(k)
    r['Timeframe Change History']=hist(r['Announced Timeframe'])
    rows.append(r)

# ---------- A. Contract-level bookings (Rocket Lab / SEC primary sources) ----------
add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2026-07-27','Vehicle':'HASTE',
 'Customer(s)':'U.S. Space Force - Space Systems Command, Rocket Systems Launch Program (RSLP)',
 'Customer Disclosure':'Disclosed','Number of Launches in booking':'12 firm + up to 6 options (up to 18)',
 'Announced Timeframe':'First launch no earlier than end of 2026; work to be completed by 31 December 2028',
 'Launch Site':'Pacific Spaceport Complex - Alaska (PSCA), Kodiak, AK (new site for Rocket Lab)',
 'Contract Value - Disclosed ($)':266000000,'Status':'Booked',
 'Sources':'https://rocketlabcorp.com/updates/record-contract-rslp-kodiak/ | https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-awarded-record-266m-missile-defense-contract-us-space',
 'Notes':'Largest launch contract in Rocket Lab history. Missile-defence / hypersonic test launches. NEW LAUNCH SITE: introduces PSCA Kodiak, Alaska as a third Rocket Lab launch location. $266M is the disclosed ceiling value; implies ~$14.8M per mission across 18 missions or ~$22.2M across the 12 firm missions.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2025-09-29','Vehicle':'Electron',
 'Customer(s)':'Synspective','Customer Disclosure':'Disclosed','Number of Launches in booking':'10 (additional)',
 'Announced Timeframe':'Launches from 2026 onward','Launch Site':'LC-1 (Mahia, NZ)','Status':'Booked',
 'Sources':'https://rocketlabcorp.com/updates/rocket-lab-and-synspective-strike-another-10-launch-deal-boosting-contracted-missions-to-21-electron-launches/',
 'Notes':'Second 10-launch Synspective deal; brought total UPCOMING Synspective missions to 21 at announcement (largest dedicated-Electron order from one customer). Value undisclosed.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2026-07-30','Vehicle':'Electron',
 'Customer(s)':'iQPS (Institute for Q-shu Pioneers of Space)','Customer Disclosure':'Disclosed',
 'Number of Launches in booking':'3','Announced Timeframe':'As announced 30-Jul-2026 (see Notes)',
 'Launch Site':'LC-1 (Mahia, NZ)','Status':'Booked',
 'Sources':'https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-secures-multi-launch-deal-iqps-three-dedicated | https://rocketlabcorp.com/updates/rocket-lab-secures-multi-launch-deal-with-iqps-for-three-dedicated-missions/',
 'Notes':'Third iQPS multi-launch booking announced in under a year; reported as taking total iQPS launches booked to 18. Value undisclosed. AMBIGUITY: press-release running totals for iQPS (4 / 8 / 7 / 18) are not internally consistent across releases - see run_log.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2025-10-07','Vehicle':'Electron',
 'Customer(s)':'iQPS','Customer Disclosure':'Disclosed','Number of Launches in booking':'3',
 'Announced Timeframe':'No earlier than 2026','Launch Site':'LC-1 (Mahia, NZ)','Status':'Booked',
 'Sources':'https://rocketlabcorp.com/updates/rocket-lab-secures-latest-multi-launch-contract-with-iqps-for-three-dedicated-electron-missions/',
 'Notes':'Value undisclosed. Supports iQPS 36-satellite SAR constellation.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2023-09-12','Vehicle':'HASTE',
 'Customer(s)':'Leidos (MACH-TB programme)','Customer Disclosure':'Disclosed','Number of Launches in booking':'4',
 'Announced Timeframe':'As contracted 2023; remaining missions NET 2026','Launch Site':'LC-2 (Wallops, VA)',
 'Status':'Partially flown','Sources':'https://www.rocketlabusa.com/updates/rocket-lab-signs-deal-with-leidos-to-launch-four-haste-missions/',
 'Notes':'1 of 4 flown (Flight 55, "HASTE A La Vista", 24-Nov-2024). 3 remaining per Wikipedia manifest. Value undisclosed.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2023-02-28','Vehicle':'Electron',
 'Customer(s)':'Capella Space','Customer Disclosure':'Disclosed','Number of Launches in booking':'4',
 'Announced Timeframe':'Rapid succession following announcement','Launch Site':'LC-1 (Mahia, NZ), option to move to LC-2',
 'Status':'Partially flown','Sources':'https://www.rocketlabusa.com/updates/rocket-lab-signs-multi-launch-deal-to-deploy-satellite-constellation-for-capella-space/',
 'Notes':'Flown: Flights 34, 40, 52; Flight 41 failed (19-Sep-2023). One dedicated launch (Acadia 10 / Capella-20) remains on the manifest for 2026. Value undisclosed.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2022-04-19','Vehicle':'Electron',
 'Customer(s)':'HawkEye 360','Customer Disclosure':'Disclosed','Number of Launches in booking':'3 (1 rideshare + 2 dedicated)',
 'Announced Timeframe':'As contracted 2022','Launch Site':'LC-1 (Mahia, NZ) or LC-2 (Wallops, VA)','Status':'Partially flown',
 'Sources':'https://rocketlabcorp.com/updates/rocket-lab-secures-multi-launch-contract-with-hawkeye-360-confirms-first-launch-planned-from-virginia/',
 'Notes':'Flown: Flight 33 (Jan-2023) and Flight 67 (Jun-2025). One dedicated launch of 6 Hawk satellites remains on the 2026 manifest. Value undisclosed.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2025-05-14','Vehicle':'Electron',
 'Customer(s)':'NASA (Aspera, via VADR contract)','Customer Disclosure':'Disclosed','Number of Launches in booking':'1',
 'Announced Timeframe':'2026','Launch Site':'LC-1 (Mahia, NZ)','Status':'Scheduled (date set)',
 'Sources':'https://www.rocketlabusa.com/updates/rocket-lab-to-launch-nasa-astrophysics-science-mission-on-electron-to-study-galaxy-evolution/',
 'Notes':'Task order under NASA VADR (contract ceiling $300M across all providers/task orders). NASA does not disclose individual VADR task-order values - treat per-mission revenue as undisclosed.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2024-11','Vehicle':'Neutron',
 'Customer(s)':'Undisclosed commercial satellite constellation operator','Customer Disclosure':'Undisclosed',
 'Number of Launches in booking':'2','Announced Timeframe':'Mid-2026 onward','Launch Site':'LC-3 (Wallops, VA)',
 'Status':'Booked','Sources':WIKIN,
 'Notes':'INFERENCE: a commercial LEO constellation operator; no further identifying detail released. Confidence: low. Value undisclosed. Timing is contingent on Neutron\'s first flight, which has NOT yet occurred.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2025-05','Vehicle':'Neutron',
 'Customer(s)':'U.S. Air Force Research Laboratory (AFRL) - Rocket Cargo','Customer Disclosure':'Disclosed',
 'Number of Launches in booking':'1','Announced Timeframe':'No earlier than 2026','Launch Site':'LC-3 (Wallops, VA)',
 'Status':'Booked','Sources':WIKIN,
 'Notes':'Rocket Cargo survivability/point-to-point demonstration. Value undisclosed. Contingent on Neutron first flight.'})

add(**{'Row Type':'Booking (contract-level)','Announcement Date':'2026-05','Vehicle':'Neutron',
 'Customer(s)':'Undisclosed (confidential customer)','Customer Disclosure':'Undisclosed',
 'Number of Launches in booking':'5','Announced Timeframe':'2026-2029','Launch Site':'LC-3 (Wallops, VA)',
 'Status':'Booked','Sources':WIKIN,
 'Notes':'INFERENCE: most likely a commercial constellation operator given the multi-year cadence; confidence low. Value undisclosed. Contingent on Neutron first flight.'})

add(**{'Row Type':'Programme status','Announcement Date':'','Vehicle':'Neutron',
 'Customer(s)':'Rocket Lab (maiden flight)','Customer Disclosure':'Disclosed','Number of Launches in booking':'1',
 'Announced Timeframe':'First flight expected in Q4 2026; vehicle delivery to pad targeted Q4 2026',
 'Launch Site':'LC-3 (Wallops, VA)','Status':'Scheduled (date set)','Sources':WIKIN+' | https://spaceflightnow.com/2026/08/10/window-for-2026-launch-debut-of-rocket-labs-neutron-rocket-is-narrowing-as-development-continues/',
 'Notes':'Neutron has NOT flown as of this run. Aug-2026 disclosure: Stage 1 tank production aligned to a Q4-2026 pad delivery, with exact timing dependent on first-stage qualification and other tests later in 2026; independent reporting describes the 2026 window as narrowing. No Neutron revenue should be assumed before first flight.'})

# ---------- B. Manifest-level scheduled launches (per-launch granularity) ----------
def site_norm(s):
    s=s.replace('Mahia, LC-1','LC-1 (Mahia, NZ)').replace('MARS, LC-2','LC-2 (Wallops, VA)')
    return s
for r in P['upcoming']:
    cust=r['customer'].strip() or 'Unknown'
    disc='Undisclosed' if cust.lower() in ('unknown','confidential','undisclosed') else 'Disclosed'
    add(**{'Row Type':'Scheduled launch (manifest-level)','Announcement Date':'','Vehicle':'Electron',
      'Customer(s)':cust,'Customer Disclosure':disc,'Number of Launches in booking':1,
      'Announced Timeframe':r['date'].strip(),'Launch Site':site_norm(r['site']),
      'Status':'Scheduled (date set)' if re.search(r'[A-Z][a-z]+ \d{4}',r['date']) else 'Booked',
      'Sources':WIKI+' (secondary; individual missions not separately confirmed against a Rocket Lab release this run)',
      'Notes':(f"Payload: {r['payload']}. " if r['payload'] else '')+r['notes']})
for r in P['haste_planned']:
    cust=r['customer'].strip() or 'Unknown'
    disc='Undisclosed' if cust.lower() in ('unknown','confidential','undisclosed') else 'Disclosed'
    notes=r['notes']
    if disc=='Undisclosed':
        notes+=' INFERENCE: likely a U.S. DoD hypersonic-test customer given the HASTE suborbital profile from LC-2 Wallops. Confidence: low-medium.'
    add(**{'Row Type':'Scheduled launch (manifest-level)','Announcement Date':'','Vehicle':'HASTE',
      'Customer(s)':cust,'Customer Disclosure':disc,'Number of Launches in booking':1,
      'Announced Timeframe':r['date'].strip(),'Launch Site':site_norm(r['site']),'Status':'Booked',
      'Sources':WIKI+' (secondary)','Notes':(f"Payload: {r['payload']}. " if r['payload'] else '')+notes})

with open(OUT+'forward_manifest.csv','w',newline='',encoding='utf-8') as fh:
    w=csv.DictWriter(fh,fieldnames=COLS); w.writeheader(); w.writerows(rows)
print('forward_manifest.csv rows:',len(rows))
import collections
print(collections.Counter(r['Row Type'] for r in rows))
print(collections.Counter(r['Vehicle'] for r in rows))
