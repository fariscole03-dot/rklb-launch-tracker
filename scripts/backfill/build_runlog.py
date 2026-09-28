# -*- coding: utf-8 -*-
import csv, os
OUT='/home/user/rklb-launch-tracker/data/'
COLS=['Run Date','Day of Week','Run Type','Completed Launches in File','Completed Launches Added This Run',
      'Forward Manifest Rows in File','Manifest Rows Added This Run','Timeframe Changes Observed',
      'Email Sent','Email Type','Pre-Earnings Package Sent This Quarter','Next Earnings Date (status)',
      'Sources Checked OK','Sources Unreachable / Not Swept','Ambiguities Flagged','Notes']
row={
 'Run Date':'2026-09-28','Day of Week':'Monday','Run Type':'HISTORICAL BACKFILL (first run)',
 'Completed Launches in File':97,'Completed Launches Added This Run':97,
 'Forward Manifest Rows in File':43,'Manifest Rows Added This Run':43,
 'Timeframe Changes Observed':'n/a (first run - baseline established)',
 'Email Sent':'Yes','Email Type':'Historical Backfill Complete',
 'Pre-Earnings Package Sent This Quarter':'No - not due. Q3-2026 ends 30-Sep-2026; per standing rules, earnings-date checking begins 20-Oct-2026.',
 'Next Earnings Date (status)':'NOT ANNOUNCED. Q2-2026 results were released 10-Aug-2026 and Q1-2026 on 07-May-2026; pattern implies Q3-2026 results ~9-12 Nov 2026. Pattern-based expectation only, not a Rocket Lab announcement.',
 'Sources Checked OK':('Wikipedia "List of Electron launches" (rev. 27-Sep-2026, primary structural source for the backfill); '
   'Wikipedia "Rocket Lab Neutron"; rocketlabcorp.com/updates (newsroom, page 1); Rocket Lab investor press releases via search; '
   'SEC EDGAR RKLB Q2-2026 10-Q (period ended 30-Jun-2026) financial statements; RKLB Q1-2026 10-Q; web search for 2026 announcements.'),
 'Sources Unreachable / Not Swept':('UNREACHABLE: investors.rocketlabcorp.com/news-releases (HTTP 503 on two attempts); '
   'rocketlabcorp.com/updates/page/2/ (HTTP 403) - blocked full newsroom pagination, so pre-2026 booking announcements were '
   'recovered via targeted search + citation mining rather than a complete newsroom sweep. '
   'SEC 10-Q MD&A (Item 2) could not be retrieved (fetch truncated at the notes) - per-launch ASP was therefore derived from '
   'the income-statement Launch Services revenue rather than quoted from MD&A. '
   'NOT SWEPT THIS RUN: FAA Office of Commercial Space Transportation licence database and FCC space/experimental filings - '
   'deliberately deferred to keep the backfill focused on the historical record; both will be swept in the first weekly digest.'),
 'Ambiguities Flagged':('(1) Synspective total: Rocket Lab\'s 26-Sep-2026 release states 13 StriX delivered and 14 remaining (=27 '
   'contracted), while Wikipedia\'s manifest is numbered "of 26" and lists only 13 remaining - one launch unaccounted for. '
   'Used Rocket Lab primary (27 / 14 remaining). '
   '(2) iQPS running totals across Rocket Lab releases (4 / 8 / 7 / 18 booked) are not internally consistent; booking rows are '
   'recorded per-release and the aggregate is NOT asserted. '
   '(3) forward_manifest.csv mixes contract-level bookings and manifest-level scheduled launches - see "Row Type" column; '
   'summing all rows WILL double-count. '
   '(4) Contract Announcement Date is populated on completed launches only where attribution is defensible (15 of 97).'),
 'Notes':('First run: created data/completed_launches.csv, data/forward_manifest.csv, data/run_log.csv and '
   'RKLB_Launch_Tracker.xlsx. 97 Electron-family flights (88 Electron orbital + 9 HASTE suborbital), flight numbers 1-97 '
   'with no gaps or duplicates. Cross-checks passed: 2026 count = 18 launches and cumulative = 97, both matching Rocket Lab\'s '
   '26-Sep-2026 release; 2023 count = 10, matching Rocket Lab\'s 2023 annual-record release. 4 launch failures (flights 1, 13, 20, 41). '
   'Neutron has not flown. NEW LAUNCH SITE recorded: PSCA Kodiak, Alaska (USSF RSLP contract, 27-Jul-2026). '
   'Electron ASP re-verified this run (quarterly requirement met): list price ~$7.5M; H1-2026 realised ~$9.0M per launch.'),
}
newfile=not os.path.exists(OUT+'run_log.csv')
with open(OUT+'run_log.csv','a',newline='',encoding='utf-8') as fh:
    w=csv.DictWriter(fh,fieldnames=COLS)
    if newfile: w.writeheader()
    w.writerow(row)
print('run_log.csv written')
