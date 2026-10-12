import csv

SYN   = "https://rocketlabcorp.com/updates/rocket-lab-secures-largest-ever-electron-commercial-deal-20-launch-contract-for-synspective/"
SYNSN = "https://spacenews.com/rocket-lab-signs-contract-with-synspective-for-20-electron-launches/"
KEP   = "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-inks-neutron-launch-deal-kepler-communications"
IQ3   = "https://rocketlabcorp.com/updates/rocket-lab-secures-latest-multi-launch-contract-with-iqps-for-three-dedicated-missions/"
IQ3B  = "https://i-qps.net/en/news/3574/"
CONF  = "https://rocketlabcorp.com/updates/rocket-labs-biggest-launch-deal-yet-confidential-customer-books-multiple-neutron-and-electron-launches/"
EX991 = "https://www.sec.gov/Archives/edgar/data/0001819994/000181999426000027/rklb-05072026ex991.htm"
Q226  = "https://www.sec.gov/Archives/edgar/data/0001819994/000181999426000062/rklb-20260630.htm"
Q226X = "https://www.sec.gov/Archives/edgar/data/0001819994/000181999426000061/rklb-08102026ex991.htm"
WIKI  = "https://en.wikipedia.org/wiki/List_of_Electron_launches"
NEUT  = "https://spaceflightnow.com/2026/08/10/window-for-2026-launch-debut-of-rocket-labs-neutron-rocket-is-narrowing-as-development-continues/"
NEUW  = "https://en.wikipedia.org/wiki/Rocket_Lab_Neutron"
IQ4   = "https://rocketlabcorp.com/updates/rocket-lab-signs-multi-launch-contract-with-iqps-for-four-electron-missions/"
IQ8   = "https://rocketlabcorp.com/updates/rocket-lab-signs-second-multi-launch-deal-secures-eight-electron-missions-with-iqps/"

E_ASP = 9200000     # RKLB-disclosed avg revenue per Electron launch, 6M 2026 (10-Q)
N_ASP = 50000000    # Neutron: public target price band ~$50-55M; low confidence

# AnnDate, Vehicle, Customers, Disclosure, N, Timeframe(verbatim), Site, ValDisclosed, ValEst, Status, TFHistory, Sources, Notes
R = [
("2026-09-30","Electron","Synspective","Disclosed",20,
 "annually from 2028-2031","LC-1 (Mahia, NZ)","", 20*E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'annually from 2028-2031'.",
 [SYN,SYNSN],
 "Rocket Lab's largest-ever commercial Electron deal. Brings Synspective's lifetime total to 47 Electron missions - the most of any Rocket Lab launch customer. 20x StriX SAR satellites to SSO. Financial terms undisclosed. Est. value = 20 x $9.2M disclosed avg revenue/launch (6M-2026 10-Q); medium confidence on rate, but note multi-launch block deals typically price below single-mission rates, so treat as an upper bound. Press coverage states the deal pushes Rocket Lab's launch backlog beyond 100 missions - that 100+ figure is press/IR commentary, not a filing disclosure."),

("2026-08-10","Neutron","Kepler Communications","Disclosed",1,
 "no earlier than 2028","LC-3 (Wallops Island, VA)","", N_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'no earlier than 2028'.",
 [KEP,Q226X],
 "Dedicated Neutron mission. Announced alongside Q2 2026 results. Rocket Lab said the booking pushes Neutron's manifest toward full capacity through the end of the decade. Est. value uses Neutron's publicly discussed ~$50-55M target price - LOW confidence, no company per-launch disclosure."),

("2026-07-30","Electron","iQPS","Disclosed",3,
 "from late 2027","LC-1 (Mahia, NZ)","", 3*E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'from late 2027'.",
 [IQ3,IQ3B],
 "Third iQPS multi-launch booking announced in under a year. Rocket Lab stated this brings iQPS to 18 contracted Electron launches in total, with seven completed as of the announcement (most recent Dec 2025 = Flight 79). CONFLICT FLAGGED: an iQPS release of 2026-04-10 put the running total at eight QPS-SAR satellites on Electron, which does not reconcile with Rocket Lab's 18-mission figure. Counting bases appear to differ (satellites vs missions, or cumulative vs remaining). Unresolved - see Notes in the 2026-04-10 row."),

("2026-05-07","Neutron","Undisclosed (confidential commercial customer)","Undisclosed",5,
 "baselined to launch between 2026 and 2029","LC-3 (Wallops Island, VA)","", 5*N_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'baselined to launch between 2026 and 2029'.",
 [CONF,EX991],
 "Part of what Rocket Lab called the largest launch contract in company history (5 Neutron + 3 Electron). Rocket Lab stated pricing aligns with its average selling price for Neutron and Electron, and that the deal values overall backlog at more than $2.2 billion. Customer inference: a large commercial constellation operator needing both medium-lift and dedicated small-lift - LOW confidence on identity; Rocket Lab has given no identifying detail. NOTE for revenue timing: the 2026 end of the baselined window is now effectively unreachable for Neutron given the vehicle has not yet flown."),

("2026-05-07","Electron","Undisclosed (confidential commercial customer)","Undisclosed",3,
 "baselined to launch between 2026 and 2029","Not stated","", 3*E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'baselined to launch between 2026 and 2029'.",
 [CONF,EX991],
 "Electron portion of the same May 2026 confidential-customer deal. Same customer as the 5-Neutron row - do not double-count contract value across the two rows."),

("2026-04-10","Electron","iQPS","Disclosed",3,
 "additional QPS-SAR launches (2026-2027)","LC-1 (Mahia, NZ)","", 3*E_ASP,"Booked",
 "2026-10-12: initial entry; timeframe recorded as announced.",
 [WIKI,IQ3B],
 "Second of the three iQPS bookings in the 2025-26 wave. Announcement date sourced from an iQPS corporate release dated 2026-04-10 referenced in Wikipedia's citation list; the matching Rocket Lab press release was NOT directly retrieved this run - date carries medium confidence and is flagged for primary-source confirmation next run. See the CONFLICT note on the 2026-07-30 row regarding iQPS mission totals."),

("","Electron","Synspective","Disclosed",10,
 "2025-2027 (renewed 10-launch agreement)","LC-1 (Mahia, NZ)","", 10*E_ASP,"Partially flown",
 "2026-10-12: initial entry. Flights 17-26 of Synspective's 47 fall under this agreement per Wikipedia's manifest; Flight 96 (2026-09-19, StriX-10) recorded as the first flown under the renewal.",
 [WIKI],
 "A 10-launch Synspective agreement signed in 2024 (exact announcement date NOT verified this run - left blank rather than guessed; flagged for confirmation). Several missions already flown as Flights 84/88/91/94/96/97. Included for completeness of the booking record; superseded in size by the Sept 2026 20-launch deal."),

("","HASTE","Leidos (MACH-TB program) for U.S. DoD","Disclosed",4,
 "NET 2026 for remaining missions","LC-2 / MARS (Wallops Island, VA)","", "","Partially flown",
 "2026-10-12: initial entry. 1 of 4 flown (Flight 55, 2024-11-24). 3 remaining listed NET 2026.",
 [WIKI],
 "Multi-Service Advanced Capability Hypersonic Test Bed task order covering four HASTE suborbital missions. Contract value not disclosed by Rocket Lab; no Electron ASP applied because HASTE pricing is undisclosed and the mission profile differs materially - deliberately left blank rather than estimated. Some of HASTE Flights 71/72/86/89 may already fall under this task order, but Rocket Lab did not attribute them; unresolved."),

("","HASTE","Undisclosed ('JAKE 4')","Undisclosed",1,
 "NET 2026","LC-2 / MARS (Wallops Island, VA)","", "","Booked",
 "2026-10-12: initial entry, announced timeframe 'NET 2026'.",
 [WIKI],
 "Listed on Wikipedia's planned-HASTE manifest as 'JAKE 4' with unknown customer and payload. Best inference: U.S. DoD hypersonic test customer given the HASTE profile and Wallops range - medium confidence. Secondary source only; not confirmed against a Rocket Lab release."),

("","Electron","NASA (Aspera)","Disclosed",1,
 "NET 2026","LC-1 (Mahia, NZ)","", E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'NET 2026'.",
 [WIKI],
 "NASA Aspera galaxy-astrophysics SmallSat, awarded May 2025. Venture-class NASA launch awards historically price well below commercial Electron rates, so the $9.2M est. is likely HIGH for this mission - low confidence."),

("","Electron","Eta Space / NASA (LOXSAT cryogenic fluid management demo)","Disclosed",1,
 "NET 2026","LC-1 (Mahia, NZ)","", E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'NET 2026'.",
 [WIKI],
 "LOXSAT flown on a Rocket Lab Photon under a NASA Tipping Point cryogenic-fluid-management demonstration. Wikipedia citation notes a 'no earlier than July 17' reference for 2026, implying the date has already moved right - exact current target not confirmed this run. Low confidence on value."),

("","Electron","Capella Space","Disclosed",1,
 "2026","LC-1 (Mahia, NZ)","", E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe '2026'.",
 [WIKI],
 "Acadia-10 (Capella-20). Secondary source only."),

("","Electron","HawkEye 360","Disclosed",1,
 "2026","LC-1 (Mahia, NZ) or LC-2 (Wallops, VA)","", E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe '2026'.",
 [WIKI],
 "Listed as carrying 6 Hawk satellites. Launch count in booking recorded as 1 mission (not 6) - the 6 refers to spacecraft. Secondary source only."),

("","Electron","Rocket Lab (in-house Venus Life Finder)","Disclosed",1,
 "NET 2026","LC-1 (Mahia, NZ)","", "","Booked",
 "2026-10-12: initial entry, announced timeframe 'NET 2026'.",
 [WIKI],
 "Rocket Lab-funded private Venus atmospheric probe on a Photon to heliocentric trajectory. NO external launch revenue - in-house mission; value deliberately blank. Has slipped repeatedly in prior years."),

("","Electron","iQPS","Disclosed",4,
 "NET 2027","LC-1 (Mahia, NZ)","", 4*E_ASP,"Booked",
 "2026-10-12: initial entry, announced timeframe 'NET 2027'.",
 [WIKI,IQ8,IQ4],
 "Wikipedia's manifest lists QPS-SAR missions 14th-17th of 17 at NET 2027. These are the tail of iQPS's earlier 4-launch (2024) and 8-launch (2025) agreements rather than a new booking. OVERLAP WARNING: do not sum this row with the 2026-04-10 and 2026-07-30 iQPS rows without reconciling against Rocket Lab's stated 18-mission total; the manifest-level and contract-level views have not been reconciled this run."),

("","Electron","Synspective","Disclosed",13,
 "2026-2027 (StriX flights 14th-26th of 47)","LC-1 (Mahia, NZ)","", "","Booked",
 "2026-10-12: initial entry, timeframe recorded as listed on the manifest.",
 [WIKI],
 "Manifest-level view of Synspective StriX missions 14-26. OVERLAP WARNING: overlaps the 10-launch renewal row above (flights 17-26). Recorded for manifest completeness; value deliberately blank to avoid double-counting against the contract-level rows."),

("","Neutron","Rocket Lab (in-house debut flight)","Disclosed",1,
 "fourth quarter of 2026 (per 2026-05-07 earnings call); window described in Aug 2026 as 'narrowing'","LC-3 (Wallops Island, VA)","", "","Slipped",
 "2026-10-12: initial entry. Documented slip history: original target mid-2025; moved to 2026 (Nov 2025); narrowed to 'at least Q4 2026' after a January 2026 propellant-tank test failure; CEO Peter Beck reaffirmed Q4 2026 on the 2026-05-07 earnings call; Spaceflight Now reported 2026-08-10 that the 2026 window 'is narrowing'. No launch as of 2026-10-12.",
 [NEUT,NEUW,"https://spacenews.com/rocket-lab-delays-neutron-debut-to-late-2026/","https://spaceflightnow.com/2025/11/11/rocket-lab-delays-debut-of-neutron-rocket-to-2026/"],
 "NEUTRON HAS NOT FLOWN as of this run. Debut is an in-house test flight - no customer launch revenue, value deliberately blank. HIGHEST-IMPACT TIMING ITEM in this tracker: five booked Neutron missions are baselined from 2026 and Kepler's is NET 2028, all gated behind this debut. Engine testing continues at NASA Stennis; LC-3 at Wallops listed as awaiting vehicle activation with zero launches. Rocket Lab has not published a specific target date."),
]

HDR = ["Announcement Date","Vehicle","Customer(s)","Customer Disclosure","Number of Launches in booking",
       "Announced Timeframe","Launch Site","Contract Value - Disclosed ($)","Contract Value - Estimated ($)",
       "Status","Timeframe Change History","Sources","Notes"]

with open("/home/user/rklb-launch-tracker/data/forward_manifest.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(HDR)
    for (ad,veh,cust,disc,n,tf,site,vd,ve,st,hist,srcs,notes) in R:
        w.writerow([ad,veh,cust,disc,n,tf,site,vd,ve,st,hist," | ".join(srcs),notes])
print("forward rows:",len(R))
