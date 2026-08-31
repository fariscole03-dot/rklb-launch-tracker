#!/usr/bin/env python3
"""
RICH historical backfill seed (first run, 2026-08-31).

Emits data/completed_launches.csv and data/forward_manifest.csv from the
researched dataset. This script is provenance for the initial backfill only.
Subsequent runs edit the CSVs directly (append-only; corrections in place).
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

WIKI = "https://en.wikipedia.org/wiki/List_of_Electron_launches"
RL_MISSIONS = "https://rocketlabcorp.com/missions/"
SEC = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001819994&type=10-&dateb=&owner=include&count=40"

# Secondary-source marker used where the row has not yet been checked
# line-by-line against a Rocket Lab press release / SEC filing.
SEC_CHECK = f"{WIKI} (secondary, cross-check backbone)"


def est_electron(date):
    """Era-based Electron ASP estimate. Basis recorded in Notes."""
    y = int(date[:4])
    if y <= 2019:
        return 5500000, "est. $5.5M - basis: RKLB states Electron came to market at $5-6M/mission (CFO A. Spice, Q1 FY26 call)"
    if y <= 2022:
        return 7000000, "est. $7.0M - basis: interpolation between $5-6M introductory pricing and ~$7.5M published mission cost"
    if y <= 2024:
        return 7500000, "est. $7.5M - basis: Rocket Lab published Electron mission cost ~$7.5M for ~300kg to LEO"
    return 8500000, "est. $8.5M - basis: RKLB CFO A. Spice, Q1 FY26 earnings call: commercial Electron backlog ASP ~$8.5M"


HASTE_EST = 9500000
HASTE_BASIS = ("est. $9.5M - basis: $190M disclosed / 20 flights, MACH-TB 2.0 block buy announced 2026-03-18. "
               "Earlier HASTE flights flew under prior MACH-TB task orders at possibly different pricing.")

# flight, date, vehicle, mission, customers, disclosure, site, ded/ride, outcome, recovery, notes
ORBITAL = [
    (1, "2017-05-25", "It's a Test", "Rocket Lab (internal test flight)", "Disclosed", "LC-1A", "Dedicated", "Failure", "None attempted", "Inaugural Electron flight. Reached space but terminated ~T+4min due to a ground-equipment telemetry fault; did not reach orbit. Test flight - no customer launch revenue."),
    (2, "2018-01-21", "Still Testing", "Planet Labs; Spire Global", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", "Second test flight; first Electron to reach orbit. Carried customer cubesats plus Rocket Lab's Humanity Star. Test flight - revenue likely nominal/none."),
    (3, "2018-11-11", "It's Business Time", "Spire Global; GeoOptics", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", "First fully commercial Electron flight."),
    (4, "2018-12-16", "This One's For Pickering", "NASA", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "NASA ELaNa-19 / Venture Class Launch Services."),
    (5, "2019-03-28", "Two Thumbs Up", "DARPA", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Payload: R3D2."),
    (6, "2019-05-05", "That's a Funny Looking Cactus", "U.S. Air Force", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Payload: STP-27RD."),
    (7, "2019-06-29", "Make it Rain", "BlackSky; USSOCOM", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", "Spaceflight Inc. rideshare; included USSOCOM Prometheus."),
    (8, "2019-08-19", "Look Ma, No Hands", "UnseenLabs; BlackSky", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", ""),
    (9, "2019-10-17", "As the Crow Flies", "Astro Digital", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "First flight of the Rocket Lab Photon-derived kick stage lineage."),
    (10, "2019-12-06", "Running Out Of Fingers", "ALE Co.; Fossa Systems", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", "First guided first-stage re-entry instrumentation test; no recovery attempted."),
    (11, "2020-01-31", "Birds of a Feather", "NRO", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Payload: NROL-151. Second instrumented re-entry test; no recovery attempted."),
    (12, "2020-06-13", "Don't Stop Me Now", "NRO; Boston University; NASA", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", ""),
    (13, "2020-07-04", "Pics Or It Didn't Happen", "Canon; Planet Labs", "Disclosed", "LC-1A", "Rideshare", "Failure", "None attempted", "Second-stage anomaly ~T+6min; all payloads lost."),
    (14, "2020-08-31", "I Can't Believe It's Not Optical", "Capella Space", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Return-to-flight after Flight 13."),
    (15, "2020-10-28", "In Focus", "Planet Labs; Canon", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", ""),
    (16, "2020-11-20", "Return To Sender", "TriSept; UnseenLabs", "Disclosed", "LC-1A", "Rideshare", "Success", "Attempted-recovered", "First successful Electron first-stage ocean splashdown and recovery."),
    (17, "2020-12-15", "The Owl's Night Begins", "Synspective", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "First Synspective StriX mission; start of the Synspective relationship."),
    (18, "2021-01-20", "Another One Leaves The Crust", "OHB Group", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (19, "2021-03-22", "They Go Up So Fast", "BlackSky; Fleet Space", "Disclosed", "LC-1A", "Rideshare", "Success", "None attempted", ""),
    (20, "2021-05-15", "Running Out Of Toes", "BlackSky", "Disclosed", "LC-1A", "Dedicated", "Failure", "Attempted-recovered", "Second-stage engine shutdown; two BlackSky satellites lost. First stage was still recovered from the ocean."),
    (21, "2021-07-29", "It's A Little Chile Up Here", "U.S. Space Force", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Payload: Monolith (STP-27RM)."),
    (22, "2021-11-18", "Love At First Insight", "BlackSky", "Disclosed", "LC-1A", "Dedicated", "Success", "Attempted-recovered", "Ocean recovery; helicopter tracked the descent but no capture attempted."),
    (23, "2021-12-09", "A Data With Destiny", "BlackSky", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (24, "2022-02-28", "The Owl's Night Continues", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (25, "2022-04-02", "Without Mission A Beat", "BlackSky", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (26, "2022-05-02", "There And Back Again", "Alba Orbital; E-Space", "Disclosed", "LC-1A", "Rideshare", "Success", "Attempted-recovered", "First mid-air helicopter capture of an Electron booster; pilot released the stage due to unexpected load, stage splashed down and was recovered from the ocean."),
    (27, "2022-06-28", "CAPSTONE", "NASA", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "Lunar CAPSTONE mission using Rocket Lab Lunar Photon. Disclosed value is NASA's stated launch services award, not an RKLB-stated or filed figure - verify against the primary NASA release."),
    (28, "2022-07-13", "Wise One Looks Ahead", "NRO", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Payload: NROL-162."),
    (29, "2022-08-04", "Antipodean Adventure", "NRO", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "Payload: NROL-199."),
    (30, "2022-09-15", "The Owl Spreads Its Wings", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (31, "2022-10-07", "It Argos Up From Here", "NOAA; CNES", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "Payload: Argos-4 / GAzelle."),
    (32, "2022-11-04", "Catch Me If You Can", "Swedish National Space Agency", "Disclosed", "LC-1B", "Dedicated", "Success", "Attempted-recovered", "Payload: MATS. Helicopter capture planned but not attempted (loss of telemetry during descent); stage recovered from the ocean."),
    (33, "2023-01-24", "Virginia Is For Launch Lovers", "HawkEye 360", "Disclosed", "LC-2", "Dedicated", "Success", "None attempted", "First Electron launch from U.S. soil (LC-2, Wallops)."),
    (34, "2023-03-16", "Stronger Together", "Capella Space", "Disclosed", "LC-2", "Dedicated", "Success", "None attempted", ""),
    (35, "2023-03-24", "The Beat Goes On", "BlackSky", "Disclosed", "LC-1B", "Dedicated", "Success", "Attempted-recovered", ""),
    (36, "2023-05-08", "Rocket Like A Hurricane", "NASA", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "NASA TROPICS (1 of 2)."),
    (37, "2023-05-26", "Coming to a Storm Near You", "NASA", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "NASA TROPICS (2 of 2)."),
    (39, "2023-07-18", "Baby Come Back", "Telesat; Spire Global", "Disclosed", "LC-1B", "Rideshare", "Success", "Attempted-recovered", ""),
    (40, "2023-08-23", "We Love The Nightlife", "Capella Space", "Disclosed", "LC-1B", "Dedicated", "Success", "Attempted-recovered", ""),
    (41, "2023-09-19", "We Will Never Desert You", "Capella Space", "Disclosed", "LC-1B", "Dedicated", "Failure", "None attempted", "Second-stage anomaly shortly after stage separation; Acadia-2 lost. Electron returned to flight in Dec 2023."),
    (42, "2023-12-15", "The Moon God Awakens", "iQPS", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "First iQPS mission; return to flight after Flight 41."),
    (43, "2024-01-31", "Four Of A Kind", "Spire Global", "Disclosed", "LC-1B", "Dedicated", "Success", "Attempted-recovered", ""),
    (44, "2024-02-18", "On Closer Inspection", "Astroscale", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "Payload: ADRAS-J."),
    (45, "2024-03-12", "Owl Night Long", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (46, "2024-03-21", "Live and Let Fly", "NRO", "Disclosed", "LC-2", "Dedicated", "Success", "None attempted", "Payload: NROL-123. First NRO mission from LC-2."),
    (47, "2024-04-23", "Beginning Of The Swarm", "KAIST; NASA", "Disclosed", "LC-1B", "Rideshare", "Success", "None attempted", "NEONSAT-1 plus NASA ACS3 solar sail."),
    (48, "2024-05-25", "Ready, Aim, PREFIRE", "NASA", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "NASA PREFIRE (1 of 2)."),
    (49, "2024-06-05", "PREFIRE And Ice", "NASA", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "NASA PREFIRE (2 of 2)."),
    (50, "2024-06-20", "No Time Toulouse", "Kineis", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "First of five Kineis IoT constellation missions."),
    (51, "2024-08-02", "Owl For One, One For Owl", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (52, "2024-08-11", "A Sky Full Of SARs", "Capella Space", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (53, "2024-09-20", "Kineis Killed The RadIoT Star", "Kineis", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (54, "2024-11-05", "Changes In Latitudes, Changes In Attitudes", "E-Space", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (56, "2024-11-25", "Ice AIS Baby", "Kineis", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (58, "2024-12-21", "Owl The Way Up", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (59, "2025-02-08", "IoT 4 You and Me", "Kineis", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (60, "2025-02-18", "Fasten Your Space Belts", "BlackSky", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "BlackSky Gen-3."),
    (61, "2025-03-15", "The Lightning God Reigns", "iQPS", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (62, "2025-03-18", "High Five", "Kineis", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Fifth and final Kineis constellation mission."),
    (63, "2025-03-26", "Finding Hot Wildfires Near You", "OroraTech", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "First OroraTech mission."),
    (64, "2025-05-17", "The Sea God Sees", "iQPS", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (65, "2025-06-02", "Full Stream Ahead", "BlackSky", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (66, "2025-06-11", "The Mountain God Guards", "iQPS", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (67, "2025-06-26", "Get The Hawk Outta Here", "HawkEye 360", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (68, "2025-06-28", "Symphony In The Stars", "EchoStar", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "Launched ~48h after Flight 67 - fastest Electron turnaround at the time."),
    (69, "2025-08-05", "The Harvest Goddess Thrives", "iQPS", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (70, "2025-08-23", "Live, Laugh, Launch", "E-Space", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (73, "2025-10-14", "Owl New World", "Synspective", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (74, "2025-11-05", "The Nation God Navigates", "iQPS", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (76, "2025-11-20", "Follow My Speed", "BlackSky", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (77, "2025-12-14", "RAISE And Shine", "JAXA", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (78, "2025-12-18", "Don't Be Such A Square", "U.S. Space Force", "Disclosed", "LC-2", "Dedicated", "Success", "None attempted", ""),
    (79, "2025-12-21", "The Wisdom God Guides", "iQPS", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (80, "2026-01-22", "The Cosmos Will See You Now", "Open Cosmos", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (81, "2026-01-30", "Bridging The Swarm", "KAIST", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (83, "2026-03-05", "Insight At Speed Is A Friend Indeed", "BlackSky", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (84, "2026-03-20", "Eight Days A Week", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (85, "2026-03-28", "Daughter Of The Stars", "ESA", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (87, "2026-04-23", "Kakushin Rising", "JAXA", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", ""),
    (88, "2026-05-22", "Viva La StriX", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (90, "2026-06-19", "VICTUS HAZE", "U.S. Space Force - Space Systems Command", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Tactically responsive space demonstration."),
    (91, "2026-06-26", "Ten Owl Of Ten", "Synspective", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", ""),
    (92, "2026-08-06", "The Grain Goddess Provides", "iQPS", "Disclosed", "LC-1A", "Dedicated", "Success", "None attempted", "Payload QPS-SAR-13. 8th launch for iQPS; 13th RKLB launch of 2026 (incl. 3 HASTE). Verified against Rocket Lab press release."),
    (93, "2026-08-20", "The Lightning God Defends", "iQPS", "Disclosed", "LC-1B", "Dedicated", "Success", "None attempted", "Deployed next QPS-SAR to 575km LEO. 14th RKLB launch of 2026. Verified against Rocket Lab press release."),
]

# HASTE: flight, date, mission, payload, customer, disclosure, notes
HASTE = [
    (38, "2023-06-18", "Scout's Arrow", "Dynetics (Leidos)", "Disclosed", "Payload: DYNAMO-A. First HASTE flight and first suborbital Electron variant."),
    (55, "2024-11-24", "HASTE A La Vista", "Leidos", "Disclosed", "MACH-TB program payload."),
    (57, "2024-12-14", "Stonehenge", "Undisclosed", "Undisclosed", "Wikipedia lists customer as 'Confidential'. Inference: MACH-TB task order via Leidos/DoD (confidence: medium) - LC-2 HASTE profile and timing 3 weeks after the Leidos MACH-TB flight."),
    (71, "2025-09-23", "Jenna", "Undisclosed", "Undisclosed", "Inference: MACH-TB / DoD hypersonic test payload (confidence: medium) - HASTE flies almost exclusively for the MACH-TB program and DIU out of LC-2."),
    (72, "2025-10-01", "Justin", "Undisclosed", "Undisclosed", "Inference: MACH-TB / DoD hypersonic test payload (confidence: medium). Flew 8 days after 'Jenna'."),
    (75, "2025-11-18", "Prometheus Run", "U.S. DoD - Defense Innovation Unit (DIU)", "Disclosed", "Payload: VAN."),
    (82, "2026-02-28", "That's Not A Knife", "U.S. DoD - Defense Innovation Unit (DIU); Hypersonix", "Disclosed", "Payload: DART AE, a scramjet-powered aircraft by Hypersonix (Australia). Rocket Lab's 4th hypersonic test mission in under six months."),
    (86, "2026-04-22", "Bubbles", "Undisclosed", "Undisclosed", "Inference: MACH-TB 2.0 task order for DoD/TRMC (confidence: medium-high) - first HASTE flight after the Mar 2026 $190M 20-flight MACH-TB 2.0 block buy, which RKLB said would begin flying 'within months'."),
    (89, "2026-06-11", "Curveball", "Undisclosed", "Undisclosed", "Inference: MACH-TB 2.0 task order for DoD/TRMC (confidence: medium-high). Reported as carrying classified payloads to speeds above Mach 20. Scrubbed 2026-06-10, flew on the backup window."),
]

SITE_FULL = {
    "LC-1A": "LC-1A (Mahia, New Zealand)",
    "LC-1B": "LC-1B (Mahia, New Zealand)",
    "LC-2": "LC-2 (Wallops Island, Virginia)",
}

CONTRACT_ANN = {
    # flight -> contract announcement date, where the booking announcement is known
    27: "2020-02-14",
    92: "2025-02-27",
    93: "2025-02-27",
}

rows = []
for (fl, date, mission, cust, disc, site, mode, outcome, recovery, notes) in ORBITAL:
    est, basis = est_electron(date)
    rev_disc = ""
    if fl == 27:
        rev_disc = "9950000"
        est, basis = "", "Disclosed figure used; no estimate needed."
    if fl in (1, 2):
        est, basis = "", "Test flight - no customer launch revenue recognised; excluded from ASP estimates."
    note = (notes + " " if notes else "") + basis
    rows.append({
        "Flight #": fl,
        "Launch Date (UTC)": date,
        "Vehicle": "Electron",
        "Mission Name": mission,
        "Customer(s)": cust,
        "Customer Disclosure": disc,
        "Launch Site": SITE_FULL[site],
        "Dedicated / Rideshare": mode,
        "Outcome": outcome,
        "Recovery": recovery,
        "Contract Announcement Date": CONTRACT_ANN.get(fl, ""),
        "Revenue - Disclosed ($)": rev_disc,
        "Revenue - Estimated ($)": est,
        "Direct Mission Costs ($)": "",
        "Sources": SEC_CHECK,
        "Notes": note.strip(),
    })

for (fl, date, mission, cust, disc, notes) in HASTE:
    rows.append({
        "Flight #": fl,
        "Launch Date (UTC)": date,
        "Vehicle": "HASTE",
        "Mission Name": mission,
        "Customer(s)": cust,
        "Customer Disclosure": disc,
        "Launch Site": "LC-2 (Wallops Island, Virginia)",
        "Dedicated / Rideshare": "Dedicated",
        "Outcome": "Success",
        "Recovery": "None attempted",
        "Contract Announcement Date": "",
        "Revenue - Disclosed ($)": "",
        "Revenue - Estimated ($)": HASTE_EST,
        "Direct Mission Costs ($)": "",
        "Sources": SEC_CHECK,
        "Notes": (notes + " " + HASTE_BASIS).strip(),
    })

rows.sort(key=lambda r: r["Flight #"])

# Flight 92/93 and the HASTE table were verified against Rocket Lab primary sources
rows_by_flight = {r["Flight #"]: r for r in rows}
rows_by_flight[92]["Sources"] = ("https://www.globenewswire.com/news-release/2026/08/06/3340045/0/en/"
                                 "rocket-lab-successfully-completes-92nd-electron-mission-8th-launch-for-iqps-earth-imaging-constellation.html"
                                 " | " + SEC_CHECK)
rows_by_flight[93]["Sources"] = ("https://investors.rocketlabcorp.com/news-releases/news-release-details/"
                                 "mission-success-rocket-lab-launches-93rd-electron-mission | " + SEC_CHECK)
rows_by_flight[38]["Sources"] = "https://rocketlabcorp.com/missions/launches/scouts-arrow/ | " + SEC_CHECK

COMPLETED_COLS = list(rows[0].keys())
with open(os.path.join(DATA, "completed_launches.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COMPLETED_COLS)
    w.writeheader()
    w.writerows(rows)

print(f"completed_launches.csv: {len(rows)} rows")


# ---------------------------------------------------------------- forward manifest
FM_COLS = [
    "Announcement Date", "Vehicle", "Customer(s)", "Customer Disclosure",
    "Number of Launches in booking", "Announced Timeframe", "Launch Site",
    "Contract Value - Disclosed ($)", "Contract Value - Estimated ($)",
    "Status", "Timeframe Change History", "Sources", "Notes",
]

OBS = "2026-08-31"
RL = "https://rocketlabcorp.com/updates/"

FORWARD = [
    # --- Contract-level bookings ---
    {
        "Announcement Date": "2024-06", "Vehicle": "Electron",
        "Customer(s)": "Synspective", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "10",
        "Announced Timeframe": "across 2025-2027",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "85000000",
        "Status": "Booked (partially flown)",
        "Timeframe Change History": f"{OBS}: initial record - announced timeframe 'across 2025-2027'",
        "Sources": "https://rocketlabcorp.com/updates/rocket-lab-signs-record-deal-for-10-electron-launches-with-synspective/",
        "Notes": "First Synspective multi-launch deal. Est. value = 10 x $8.5M Electron backlog ASP. Exact announcement day in June 2024 to be confirmed against the Rocket Lab press release next run.",
    },
    {
        "Announcement Date": "2025-09-29", "Vehicle": "Electron",
        "Customer(s)": "Synspective", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "10",
        "Announced Timeframe": "through to the end of the decade",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "85000000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - announced timeframe 'through to the end of the decade'",
        "Sources": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-and-synspective-strike-another-10-launch-deal",
        "Notes": "Second Synspective 10-launch deal; RKLB stated this brings total contracted Synspective missions to 21 - largest single-customer dedicated Electron order to date. Est. value = 10 x $8.5M ASP.",
    },
    {
        "Announcement Date": "2025-02-04", "Vehicle": "Electron",
        "Customer(s)": "iQPS (Institute for Q-shu Pioneers of Space)", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "4",
        "Announced Timeframe": "three missions in 2025, fourth in 2026",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "34000000",
        "Status": "Booked (partially flown)",
        "Timeframe Change History": f"{OBS}: initial record - 'three dedicated missions in 2025, fourth in 2026'",
        "Sources": "https://rocketlabcorp.com/updates/rocket-lab-signs-multi-launch-contract-with-iqps-for-four-electron-missions/",
        "Notes": "First iQPS multi-launch contract. CONFLICT: one secondary summary described the contract as signed July 2024, while the Businesswire release ID (20250204) and SatNews coverage (2025-02-05) indicate a 2025-02-04 announcement. Recorded as 2025-02-04; flagged for primary verification.",
    },
    {
        "Announcement Date": "2025-02-27", "Vehicle": "Electron",
        "Customer(s)": "iQPS", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "4 (bringing iQPS total booked to 8)",
        "Announced Timeframe": "six missions in 2025, two in 2026",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "34000000",
        "Status": "Booked (partially flown)",
        "Timeframe Change History": f"{OBS}: initial record - 'six missions scheduled 2025, two 2026'",
        "Sources": "https://rocketlabcorp.com/updates/rocket-lab-signs-second-multi-launch-deal-secures-eight-electron-missions-with-iqps/",
        "Notes": "Second iQPS deal. Flights 92 and 93 (Aug 2026) fall under the iQPS booking stack.",
    },
    {
        "Announcement Date": "2026-04-09", "Vehicle": "Electron",
        "Customer(s)": "iQPS", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "3 (RKLB stated total iQPS Electron missions now 15)",
        "Announced Timeframe": "from 2028",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "25500000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - announced 'from 2028'",
        "Sources": "https://investors.rocketlabcorp.com/news-releases/news-release-details/iqps-books-three-new-launches-electron-extending-multi-year",
        "Notes": "Est. value = 3 x $8.5M ASP.",
    },
    {
        "Announcement Date": "2026-07-30", "Vehicle": "Electron",
        "Customer(s)": "iQPS", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "3 (RKLB stated total iQPS launches booked now 18)",
        "Announced Timeframe": "from late 2027",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "25500000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - announced 'from late 2027'",
        "Sources": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-secures-multi-launch-deal-iqps-three-dedicated",
        "Notes": "Described by RKLB as the third iQPS multi-launch booking in under a year. NOTE the running totals do not reconcile cleanly (8 booked Feb 2025 -> 15 Apr 2026 -> 18 Jul 2026); RKLB's totals appear to mix flown and booked missions. Flagged for the user.",
    },
    {
        "Announcement Date": "2026-05-07", "Vehicle": "Neutron; Electron",
        "Customer(s)": "Undisclosed", "Customer Disclosure": "Undisclosed",
        "Number of Launches in booking": "8 (5 Neutron + 3 Electron)",
        "Announced Timeframe": "baselined to launch between 2026 and 2029",
        "Launch Site": "LC-1 (Mahia, New Zealand) and LC-3 (Wallops Island, Virginia)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "288000000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - announced 'between 2026 and 2029'",
        "Sources": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-labs-biggest-launch-deal-yet-confidential-customer-books",
        "Notes": ("Largest launch contract in RKLB history. Customer confidential. Inference: a commercial LEO constellation "
                  "operator rather than a government customer (confidence: low) - RKLB framed it as a commercial bulk order and "
                  "declined to name the customer, and no government award of this size appeared in public procurement records. "
                  "RKLB stated pricing 'aligns with average selling price' for both vehicles, so est. = (5 x $52.5M Neutron mid-ASP) "
                  "+ (3 x $8.5M Electron ASP) = $288M. RKLB said the deal took total manifest above 70 missions and backlog above $2.2B."),
    },
    {
        "Announcement Date": "2026-03-18", "Vehicle": "HASTE",
        "Customer(s)": "U.S. Department of War - TRMC MACH-TB 2.0 (via Kratos, with NSWC Crane)", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "20",
        "Announced Timeframe": "over a four-year period; first mission within months of signing",
        "Launch Site": "LC-2 (Wallops Island, Virginia)",
        "Contract Value - Disclosed ($)": "190000000", "Contract Value - Estimated ($)": "",
        "Status": "Booked (partially flown)",
        "Timeframe Change History": f"{OBS}: initial record - 'over a four-year period'",
        "Sources": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-secures-190m-contract-20x-haste-launches-cements",
        "Notes": ("Block buy of 20 hypersonic test flights under MACH-TB 2.0 Task Area 1. Implies $9.5M per HASTE flight - "
                  "the anchor for all HASTE revenue estimates in the completed-launch tab. HASTE flights 86 (Apr 2026) and "
                  "89 (Jun 2026) most likely draw against this block (inference, medium-high confidence)."),
    },
    {
        "Announcement Date": "2025-05-08", "Vehicle": "Neutron",
        "Customer(s)": "U.S. Air Force Research Laboratory (AFRL)", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1",
        "Announced Timeframe": "NET 2026",
        "Launch Site": "LC-3 (Wallops Island, Virginia)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "52500000",
        "Status": "Booked - at risk of slip",
        "Timeframe Change History": (f"{OBS}: initial record - announced 'NET 2026'. As of 2026-08 Neutron had not flown and "
                                     "RKLB's own first flight was still targeting Q4 2026 pad delivery, so a 2026 date for this "
                                     "mission looks unlikely on the public record."),
        "Sources": "https://spaceflightnow.com/2025/05/10/rocket-lab-to-debut-point-to-point-cargo-transportation-capability-on-2026-air-force-mission/",
        "Notes": "Rocket cargo / point-to-point re-entry demonstration under AFRL's REGAL programme. First announced Neutron launch contract. Est. value = Neutron mid-ASP $52.5M.",
    },
    {
        "Announcement Date": "2026-08-10", "Vehicle": "Neutron",
        "Customer(s)": "Kepler Communications", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1",
        "Announced Timeframe": "no earlier than 2028",
        "Launch Site": "LC-3 (Wallops Island, Virginia)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "52500000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - announced 'no earlier than 2028'",
        "Sources": "https://investors.rocketlabcorp.com/news-releases/news-release-details/rocket-lab-inks-neutron-launch-deal-kepler-communications",
        "Notes": "First named dedicated commercial Neutron booking. Deploys multiple Kepler optical-relay satellites to LEO. Announced the same day as Q2 FY26 results. Est. value = Neutron mid-ASP $52.5M.",
    },
    # --- Specific scheduled / upcoming launches ---
    {
        "Announcement Date": "2026-08", "Vehicle": "Electron",
        "Customer(s)": "Synspective", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1",
        "Announced Timeframe": "2026-08-31, window opens 12:00 UTC",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "8500000",
        "Status": "Scheduled (date set)",
        "Timeframe Change History": f"{OBS}: initial record - launch window 2026-08-31 12:00 UTC",
        "Sources": "https://rocketlabcorp.com/missions/launches/owl-around-the-world/",
        "Notes": ("Mission 'Owl Around The World'. AMBIGUITY: Wikipedia lists the payload as StriX-9, while Synspective and "
                  "Rocket Lab describe it as Synspective's 11th StriX satellite and Rocket Lab's 11th dedicated Synspective launch. "
                  "Payload serial not resolved. Launch window opens on the run date - outcome not yet known at time of writing."),
    },
    {
        "Announcement Date": "", "Vehicle": "Electron",
        "Customer(s)": "Eta Space", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1", "Announced Timeframe": "August 2026",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "8500000",
        "Status": "Scheduled (date set)",
        "Timeframe Change History": f"{OBS}: initial record - 'August 2026'",
        "Sources": SEC_CHECK,
        "Notes": "LOXSAT cryogenic-fluid-management demo on a Rocket Lab Photon. Timeframe is secondary-sourced; 'August 2026' is now effectively lapsed and needs re-checking.",
    },
    {
        "Announcement Date": "", "Vehicle": "Electron",
        "Customer(s)": "NASA", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1", "Announced Timeframe": "August 2026",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "8500000",
        "Status": "Scheduled (date set)",
        "Timeframe Change History": f"{OBS}: initial record - 'August 2026'",
        "Sources": SEC_CHECK,
        "Notes": "NASA Aspera astrophysics smallsat. Timeframe secondary-sourced and now effectively lapsed; needs re-checking.",
    },
    {
        "Announcement Date": "", "Vehicle": "Electron",
        "Customer(s)": "Capella Space", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1", "Announced Timeframe": "2026",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "8500000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - '2026'",
        "Sources": SEC_CHECK, "Notes": "Acadia-10 / Capella-20. Secondary-sourced.",
    },
    {
        "Announcement Date": "", "Vehicle": "Electron",
        "Customer(s)": "HawkEye 360", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1 (6 Hawk satellites)", "Announced Timeframe": "2026",
        "Launch Site": "LC-1 (Mahia, New Zealand) or LC-2 (Wallops Island, Virginia)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "8500000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - '2026'",
        "Sources": SEC_CHECK, "Notes": "Secondary-sourced; launch site not yet fixed.",
    },
    {
        "Announcement Date": "", "Vehicle": "Electron",
        "Customer(s)": "BlackSky", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1+", "Announced Timeframe": "NET 2026",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "8500000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - 'NET 2026'",
        "Sources": SEC_CHECK, "Notes": "BlackSky Gen-3. Count of remaining missions not resolved; secondary-sourced.",
    },
    {
        "Announcement Date": "", "Vehicle": "Electron",
        "Customer(s)": "Rocket Lab (internal / Rocket Lab-funded)", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1", "Announced Timeframe": "NET 2026",
        "Launch Site": "LC-1 (Mahia, New Zealand)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - 'NET 2026'",
        "Sources": SEC_CHECK,
        "Notes": "Venus Life Finder - Rocket Lab's self-funded private Venus probe. No third-party launch revenue expected; excluded from revenue estimates.",
    },
    {
        "Announcement Date": "", "Vehicle": "Neutron",
        "Customer(s)": "Rocket Lab (internal - first flight)", "Customer Disclosure": "Disclosed",
        "Number of Launches in booking": "1",
        "Announced Timeframe": "Neutron delivery to pad targeted Q4 2026; debut window described by RKLB as narrowing, may slip to 2027",
        "Launch Site": "LC-3 (Wallops Island, Virginia)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "",
        "Status": "Scheduled (date set)",
        "Timeframe Change History": (
            "2025-11-11: RKLB moved Neutron debut from 2025 into 2026. | "
            "2026-01-21: first-stage tank ruptured during a hydrostatic pressure trial, pushing the debut from mid-2026 to late 2026. | "
            "2026-08-10: RKLB reported Stage 1 tank production aligned with Q4 2026 pad delivery; press reporting (2026-08-10, Spaceflight Now) "
            f"described the 2026 window as 'narrowing' with slip into 2027 possible. | {OBS}: recorded on first run."),
        "Sources": "https://spaceflightnow.com/2026/08/10/window-for-2026-launch-debut-of-rocket-labs-neutron-rocket-is-narrowing-as-development-continues/ | https://spaceflightnow.com/2025/11/11/rocket-lab-delays-debut-of-neutron-rocket-to-2026/",
        "Notes": "Neutron has NOT flown as of 2026-08-31. This is the single largest timing risk in the forward manifest - all Neutron-dependent bookings sit behind it.",
    },
    {
        "Announcement Date": "", "Vehicle": "HASTE",
        "Customer(s)": "Leidos; and JAKE 4 (customer unstated)", "Customer Disclosure": "Undisclosed",
        "Number of Launches in booking": "4 (3 Leidos MACH-TB + 1 JAKE 4)", "Announced Timeframe": "NET 2026",
        "Launch Site": "LC-2 (Wallops Island, Virginia)",
        "Contract Value - Disclosed ($)": "", "Contract Value - Estimated ($)": "38000000",
        "Status": "Booked",
        "Timeframe Change History": f"{OBS}: initial record - 'NET 2026'",
        "Sources": SEC_CHECK,
        "Notes": ("Listed as planned HASTE flights. Likely overlaps with the 20-flight MACH-TB 2.0 block buy rather than being "
                  "additive - do NOT double-count against the $190M contract row (confidence: medium). Est. = 4 x $9.5M."),
    },
]

with open(os.path.join(DATA, "forward_manifest.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FM_COLS)
    w.writeheader()
    for r in FORWARD:
        w.writerow({c: r.get(c, "") for c in FM_COLS})

print(f"forward_manifest.csv: {len(FORWARD)} rows")
