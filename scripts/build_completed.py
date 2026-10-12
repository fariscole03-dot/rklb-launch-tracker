import csv, os

RL   = "https://rocketlabcorp.com/updates/"
WIKI = "https://en.wikipedia.org/wiki/List_of_Electron_launches"
K25  = "https://www.sec.gov/Archives/edgar/data/1819994/000181999426000013/rklb-20251231.htm"
Q226 = "https://www.sec.gov/Archives/edgar/data/0001819994/000181999426000062/rklb-20260630.htm"

# Period-average revenue-per-launch used for the "Estimated" column.
# Disclosed company averages: H1-2025 $7.5M, Q2-2025 $7.9M, H1-2026 $9.2M, Q2-2026 $9.1M (10-Q).
def est_rev(date, vehicle):
    y, m = int(date[:4]), int(date[5:7])
    if y <= 2018: return 5000000
    if y <= 2020: return 6000000
    if y <= 2022: return 7000000
    if y == 2023: return 7500000
    if y == 2024: return 8000000
    if y == 2025: return 7500000 if m <= 6 else 8500000
    return 9200000

def est_basis(date):
    y, m = int(date[:4]), int(date[5:7])
    if y == 2026:
        return "Est. = $9.2M, RKLB-disclosed avg revenue per launch for 6M ended 2026-06-30 (10-Q). Medium confidence."
    if y == 2025 and m <= 6:
        return "Est. = $7.5M, RKLB-disclosed avg revenue per launch for 6M ended 2025-06-30 (10-Q). Medium confidence."
    if y == 2025:
        return "Est. = $8.5M, interpolated between disclosed H1-2025 ($7.5M) and H1-2026 ($9.2M) averages. Low-medium confidence."
    return ("Est. from period Electron pricing trend; no RKLB per-launch disclosure located for this period this run. "
            "Low confidence - flagged for a dedicated filing sweep.")

# Flight#, Date, Vehicle, Mission, Customers, Disclosure, Site, Ded/Ride, Outcome, Recovery, ContractAnnDate, RevDisclosed, DirectCost, Sources, Notes
R = [
(1,"2017-05-25","Electron","It's a Test","Rocket Lab (in-house flight test)","Disclosed","LC-1A","Dedicated","Failure","None attempted","","","",[WIKI],"Maiden Electron flight. Reached space but not orbit; terminated by range safety after a ground-equipment telemetry fault. No customer payload - no launch revenue."),
(2,"2018-01-21","Electron","Still Testing","Planet Labs; Spire Global","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"First Electron to reach orbit. Dove Pioneer, 2x Lemur-2, plus Rocket Lab's Humanity Star."),
(3,"2018-11-11","Electron","It's Business Time","Spire Global; GeoOptics; Fleet Space; Irvine CubeSat STEM Program; NABEO","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"First fully commercial Electron flight."),
(4,"2018-12-16","Electron","This One's For Pickering","NASA (ELaNa-19 / VCLS)","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"NASA Venture Class Launch Services; 13 CubeSats."),
(5,"2019-03-28","Electron","Two Thumbs Up","DARPA","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"R3D2 radio-reflector tech demo."),
(6,"2019-05-05","Electron","That's a Funny Looking Cactus","U.S. Air Force (STP-27RD)","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"SPARC-1, Falcon ODE, Harbinger."),
(7,"2019-06-29","Electron","Make It Rain","BlackSky; USSOCOM; Melbourne Space Program; Swarm; others","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"BlackSky Global-3, 2x Prometheus, ACRUX-1, SpaceBEE 8/9, Painani-1. Spaceflight Inc. rideshare."),
(8,"2019-08-19","Electron","Look Ma, No Hands","UnseenLabs; BlackSky; AFSPC","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"BRO-1, BlackSky Global-4, 2 experimental payloads."),
(9,"2019-10-17","Electron","As the Crow Flies","Astro Digital","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"Palisade tech-demo satellite."),
(10,"2019-12-06","Electron","Running Out Of Fingers","ALE; Fossa Systems; Alba Orbital; Swarm; others","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"ALE-2 plus six PocketQubes. First instrumented guided re-entry test of stage 1 - no recovery attempted."),
(11,"2020-01-31","Electron","Birds of a Feather","U.S. National Reconnaissance Office (NROL-151)","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"NRO Rapid Acquisition of a Small Rocket (RASR) contract. Second guided stage-1 re-entry test."),
(12,"2020-06-13","Electron","Don't Stop Me Now","NRO; Boston University/NASA; UNSW Canberra/RAAF","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"3x classified NRO payloads, ANDESITE, RAAF M2 Pathfinder."),
(13,"2020-07-04","Electron","Pics Or It Didn't Happen","Canon Electronics; Planet Labs; In-Space Missions","Disclosed","LC-1A","Rideshare","Failure","None attempted","","","",[WIKI],"Stage-2 electrical connection failure ~T+4min; 7 satellites lost (CE-SAT-IB, 5x SuperDove, Faraday-1)."),
(14,"2020-08-31","Electron","I Can't Believe It's Not Optical","Capella Space; Rocket Lab (Photon)","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"Capella Sequoia. First operational Photon kick stage (First Light)."),
(15,"2020-10-28","Electron","In Focus","Planet Labs; Canon Electronics (via Spaceflight Inc.)","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI],"9x SuperDove + CE-SAT-IIB."),
(16,"2020-11-20","Electron","Return To Sender","TriSept; UnseenLabs; Univ. of Auckland; Swarm; others","Disclosed","LC-1A","Rideshare","Success","Attempted-recovered","","","",[WIKI],"First successful stage-1 ocean splashdown and ship recovery. 24x SpaceBEE, BRO-2/3, DragRacer, APSS-1, Gnome mass simulator."),
(17,"2020-12-15","Electron","The Owl's Night Begins","Synspective","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"StriX-alpha. First Synspective mission - start of what became a 47-launch relationship."),
(18,"2021-01-20","Electron","Another One Leaves The Crust","OHB Group","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"GMS-T communications satellite."),
(19,"2021-03-22","Electron","They Go Up So Fast","BlackSky; Fleet Space; Myriota; Care Weather; Rocket Lab (Photon)","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI,"https://cosmoquest.org/x/2021/04/rocket-labs-latest-launch-they-go-up-so-fast-breaks-milestone"],"100th satellite deployed by Electron. BlackSky Global-9 plus Photon Pathstone demo. Outcome confirmed Success via secondary sources after Wikipedia table parsed ambiguously."),
(20,"2021-05-15","Electron","Running Out Of Toes","BlackSky","Disclosed","LC-1A","Dedicated","Failure","Attempted-recovered","","","",[WIKI],"Stage-2 engine computer shutdown after ignition; BlackSky-10 and -11 lost. Stage 1 was nonetheless successfully splashed down and recovered."),
(21,"2021-07-29","Electron","It's A Little Chile Up Here","U.S. Space Force (STP / Monolith)","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"Space Test Program Monolith satellite; return to flight after Flight 20."),
(22,"2021-11-18","Electron","Love At First Insight","BlackSky","Disclosed","LC-1A","Dedicated","Success","Attempted-recovered","","","",[WIKI],"BlackSky-14/-15. Stage 1 recovered; first helicopter tracking rehearsal."),
(23,"2021-12-09","Electron","A Data With Destiny","BlackSky","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"BlackSky Gen-2 -12/-13."),
(24,"2022-02-28","Electron","The Owl's Night Continues","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI],"StriX-beta. First launch from LC-1B (Pad B)."),
(25,"2022-04-02","Electron","Without Mission A Beat","BlackSky","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"BlackSky Gen-2 -14/-15."),
(26,"2022-05-02","Electron","There And Back Again","Alba Orbital; E-Space; Swarm; Unseenlabs; Spaceflight Inc.; others","Disclosed","LC-1A","Rideshare","Success","Attempted-recovered","","","",[WIKI],"34 satellites. First mid-air helicopter capture of a returning stage: booster caught, then released due to unexpected load, and recovered from the ocean. Mission itself fully successful."),
(27,"2022-06-28","Electron","CAPSTONE","NASA; Advanced Space; Rocket Lab (Lunar Photon)","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI],"First Rocket Lab lunar mission; CAPSTONE delivered to NRHO transfer via Lunar Photon."),
(28,"2022-07-13","Electron","Wise One Looks Ahead","NRO (NROL-162)","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI],"RASR-3."),
(29,"2022-08-04","Electron","Antipodean Adventure","NRO (NROL-199)","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI],"RASR-4."),
(30,"2022-09-15","Electron","The Owl Spreads Its Wings","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI],"StriX-1."),
(31,"2022-10-07","Electron","It Argos Up From Here","General Atomics / NOAA / CNES","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI],"GAzelle carrying Argos-4 Advanced Data Collection System."),
(32,"2022-11-04","Electron","Catch Me If You Can","Swedish National Space Agency; OHB Sweden","Disclosed","LC-1B","Dedicated","Success","Attempted-recovered","","","",[WIKI],"MATS atmospheric satellite. Helicopter capture aborted due to loss of telemetry lock during descent; stage recovered from ocean. Mission successful."),
(33,"2023-01-24","Electron","Virginia Is For Launch Lovers","HawkEye 360","Disclosed","LC-2","Dedicated","Success","None attempted","","","",[WIKI,K25],"First Electron launch from U.S. soil (Wallops/MARS). HawkEye 360 Cluster 6."),
(34,"2023-03-16","Electron","Stronger Together","Capella Space","Disclosed","LC-2","Dedicated","Success","None attempted","","","",[WIKI,K25],"Capella-9 and -10."),
(35,"2023-03-24","Electron","The Beat Goes On","BlackSky","Disclosed","LC-1B","Dedicated","Success","Attempted-recovered","","","",[WIKI,K25],"BlackSky Gen-2 -18/-19. Stage 1 splashdown and recovery."),
(36,"2023-05-08","Electron","Rocket Like A Hurricane","NASA (TROPICS)","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"2x TROPICS CubeSats."),
(37,"2023-05-26","Electron","Coming To A Storm Near You","NASA (TROPICS)","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"Final 2x TROPICS CubeSats."),
(38,"2023-06-18","HASTE","Scout's Arrow","Dynetics (Leidos) for U.S. DoD","Disclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,K25],"Maiden HASTE suborbital flight. DYNAMO-A payload details classified."),
(39,"2023-07-18","Electron","Baby Come Back","Telesat; Spire Global; NASA (Starling)","Disclosed","LC-1B","Rideshare","Success","Attempted-recovered","","","",[WIKI,K25],"Telesat LEO-3, 2x Lemur-2, 4x NASA Starling. Stage 1 recovered."),
(40,"2023-08-23","Electron","We Love The Nightlife","Capella Space","Disclosed","LC-1B","Dedicated","Success","Attempted-recovered","","","",[WIKI,K25],"Acadia-1. Stage 1 recovered."),
(41,"2023-09-19","Electron","We Will Never Desert You","Capella Space","Disclosed","LC-1B","Dedicated","Failure","None attempted","","","",[WIKI,K25],"Stage-2 power failure shortly after stage separation; Acadia-2 lost. Electron's most recent in-flight failure."),
(42,"2023-12-15","Electron","The Moon God Awakens","iQPS","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"QPS-SAR-5 (Tsukuyomi-I). Return to flight after Flight 41; first iQPS mission."),
(43,"2024-01-31","Electron","Four Of A Kind","Spire Global; NorthStar Earth & Space","Disclosed","LC-1B","Dedicated","Success","Attempted-recovered","","","",[WIKI,K25],"4x NorthStar Skylark space-situational-awareness satellites built by Spire. Stage 1 recovered."),
(44,"2024-02-19","Electron","On Closer Inspection","Astroscale Japan","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"ADRAS-J debris-inspection demonstrator."),
(45,"2024-03-13","Electron","Owl Night Long","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"StriX-3."),
(46,"2024-03-21","Electron","Live And Let Fly","NRO (NROL-123)","Disclosed","LC-2","Dedicated","Success","None attempted","","","",[WIKI,K25],"NRO RASR-5 under USSF Rocket Systems Launch Program."),
(47,"2024-04-23","Electron","Beginning Of The Swarm","KAIST (South Korea); NASA","Disclosed","LC-1B","Rideshare","Success","None attempted","","","",[WIKI,K25],"NEONSAT-1 plus NASA ACS3 solar-sail demo."),
(48,"2024-05-25","Electron","Ready, Aim, PREFIRE","NASA","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"PREFIRE-1 (first of two polar-radiant-energy CubeSats)."),
(49,"2024-06-05","Electron","PREFIRE And Ice","NASA","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"PREFIRE-2."),
(50,"2024-06-20","Electron","No Time Toulouse","Kineis","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"First 5 of 25 Kineis IoT satellites."),
(51,"2024-08-02","Electron","Owl For One, One For Owl","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"StriX-4."),
(52,"2024-08-11","Electron","A Sky Full Of SARs","Capella Space","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"Acadia-3."),
(53,"2024-09-20","Electron","Kineis Killed The RadIoT Star","Kineis","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"Kineis satellites 6-10."),
(54,"2024-11-05","Electron","Changes In Latitudes, Changes In Attitudes","Undisclosed","Undisclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"Payload 'Protosat-1'. Best inference: E-Space constellation prototype - medium confidence, based on later confirmed E-Space Electron activity (Flight 70) and the prototype naming. Rocket Lab did not name the customer."),
(55,"2024-11-24","HASTE","HASTE A La Vista","Leidos (MACH-TB program) for U.S. DoD","Disclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,K25],"First of four HASTE missions under the Leidos MACH-TB (Multi-Service Advanced Capability Hypersonic Test Bed) task order. Payload classified."),
(56,"2024-11-25","Electron","Ice AIS Baby","Kineis","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"Kineis satellites 11-15."),
(57,"2024-12-14","HASTE","Stonehenge","Undisclosed","Undisclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,K25],"Best inference: U.S. or allied government hypersonic test customer given HASTE profile and Wallops range use - medium confidence. Rocket Lab described it as a confidential customer."),
(58,"2024-12-21","Electron","Owl The Way Up","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"StriX-2."),
(59,"2025-02-08","Electron","IoT 4 You And Me","Kineis","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"Kineis satellites 16-20."),
(60,"2025-02-18","Electron","Fasten Your Space Belts","BlackSky","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"First BlackSky Gen-3 satellite."),
(61,"2025-03-15","Electron","The Lightning God Reigns","iQPS","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"QPS-SAR-9 (Sususaki)."),
(62,"2025-03-18","Electron","High Five","Kineis","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"Kineis satellites 21-25; completed the 25-satellite constellation."),
(63,"2025-03-26","Electron","Finding Hot Wildfires Near You","OroraTech","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"8x OroraTech OTC-P1 wildfire-detection satellites."),
(64,"2025-05-17","Electron","The Sea God Sees","iQPS","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"QPS-SAR-10 (Watatsumi-I)."),
(65,"2025-06-02","Electron","Full Stream Ahead","BlackSky","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"BlackSky Gen-3."),
(66,"2025-06-11","Electron","The Mountain God Guards","iQPS","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"QPS-SAR-11 (Yamatsumi-I)."),
(67,"2025-06-26","Electron","Get The Hawk Outta Here","HawkEye 360","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI,K25],"HawkEye 360 Cluster 12 (3 sats) plus Kestrel-0A hosted payload."),
(68,"2025-06-28","Electron","Symphony In The Stars","EchoStar","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"Lyra Block 1-2 direct-to-device demo satellite."),
(69,"2025-08-05","Electron","The Harvest Goddess Thrives","iQPS","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"QPS-SAR-12 (Kushinada-I)."),
(70,"2025-08-23","Electron","Live, Laugh, Launch","E-Space","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"Calistus A-E sustainable-constellation prototypes."),
(71,"2025-09-23","HASTE","Jenna","Undisclosed","Undisclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,K25],"Best inference: U.S. DoD hypersonic test customer, plausibly under MACH-TB or a DIU task order - medium confidence, based on HASTE profile and Wallops range. Customer and payload not disclosed."),
(72,"2025-10-01","HASTE","Justin","Undisclosed","Undisclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,K25],"Best inference: U.S. DoD hypersonic test customer - medium confidence, same reasoning as Flight 71. Flown 8 days after 'Jenna', suggesting a paired test campaign."),
(73,"2025-10-14","Electron","Owl New World","Synspective","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"StriX-5."),
(74,"2025-11-05","Electron","The Nation God Navigates","iQPS","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"QPS-SAR-14."),
(75,"2025-11-18","HASTE","Prometheus Run","U.S. Defense Innovation Unit (DIU); JHU APL","Disclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,K25],"Government primary payload from Johns Hopkins APL plus secondary payloads."),
(76,"2025-11-20","Electron","Follow My Speed","Undisclosed (confidential commercial constellation operator)","Undisclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,K25],"Payload identified by trackers as a BlackSky Gen-3 satellite - high confidence that the end customer is BlackSky; Rocket Lab marketed the mission under a confidential-customer label."),
(77,"2025-12-14","Electron","RAISE And Shine","JAXA","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"RAISE-4 innovative-satellite technology demonstration."),
(78,"2025-12-18","Electron","Don't Be Such A Square","U.S. Space Force (STP-S30)","Disclosed","LC-2","Dedicated","Success","None attempted","","","",[WIKI,K25],"DISKSat and rideshare payloads under Space Test Program."),
(79,"2025-12-21","Electron","The Wisdom God Guides","iQPS","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,K25],"QPS-SAR-15. Seventh completed iQPS mission per Rocket Lab's July 2026 tally."),
(80,"2026-01-22","Electron","The Cosmos Will See You Now","Open Cosmos","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,RL],"2x Open Cosmos satellites."),
(81,"2026-01-30","Electron","Bridging The Swarm","KAIST (South Korea)","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,RL],"NEONSAT-1A."),
(82,"2026-02-28","HASTE","That's Not A Knife","U.S. Defense Innovation Unit (DIU); Hypersonix","Disclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,RL],"DART AE scramjet vehicle for Hypersonix under a DIU agreement."),
(83,"2026-03-05","Electron","Insight At Speed Is A Friend Indeed","Undisclosed (confidential commercial constellation operator)","Undisclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,RL],"Payload identified by trackers as a BlackSky Gen-3 satellite - high confidence the end customer is BlackSky."),
(84,"2026-03-20","Electron","Eight Days A Week","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,RL],"StriX-6."),
(85,"2026-03-28","Electron","Daughter Of The Stars","European Space Agency","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,RL],"2x Celeste Pathfinder A satellites."),
(86,"2026-04-22","HASTE","Bubbles","Undisclosed","Undisclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,RL],"Best inference: U.S. DoD hypersonic test customer, plausibly a MACH-TB follow-on - medium confidence, based on HASTE profile and Wallops range."),
(87,"2026-04-23","Electron","Kakushin Rising","JAXA","Disclosed","LC-1A","Rideshare","Success","None attempted","","","",[WIKI,RL],"Rideshare of 8 spacecraft under JAXA's innovative satellite technology demonstration program."),
(88,"2026-05-22","Electron","Viva La StriX","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,RL],"StriX-7."),
(89,"2026-06-11","HASTE","Curveball","Undisclosed","Undisclosed","LC-2 (MARS)","Dedicated","Success","None attempted","","","",[WIKI,RL],"Reported as the first HASTE flight to reach roughly 200 km altitude. Best inference: U.S. DoD hypersonic test customer - medium confidence."),
(90,"2026-06-19","Electron","VICTUS HAZE","U.S. Space Force Space Systems Command (TacRS-4)","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,RL],"Victus Haze tactically responsive space mission; Rocket Lab-built Pioneer-class spacecraft."),
(91,"2026-06-26","Electron","Ten Owl Of Ten","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,RL],"StriX-8. Completed the 2024 ten-launch Synspective contract."),
(92,"2026-08-06","Electron","The Grain Goddess Provides","iQPS","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,RL],"QPS-SAR-13. Follows a 2026-06-30 launch abort at first-stage ignition for an iQPS mission; iQPS then guided to NET August 2026."),
(93,"2026-08-20","Electron","The Lightning God Defends","iQPS","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,RL],"QPS-SAR-18. Rocket Lab release described it as Electron's 93rd mission."),
(94,"2026-09-02","Electron","Owl Around The World","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,RL],"StriX-9. Rocket Lab release: Electron's 94th mission."),
(95,"2026-09-11","Electron","Happily Ever Faster","BlackSky","Disclosed","LC-1A","Dedicated","Success","None attempted","","","",[WIKI,RL],"BlackSky Gen-3. Rocket Lab release: Electron's 95th mission and 16th Electron mission of 2026 - this confirms Rocket Lab counts HASTE flights within its Electron mission tally."),
(96,"2026-09-19","Electron","Owl By The Dozen","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,RL],"StriX-10. Rocket Lab release: Electron's 96th mission. First flight under the renewed Synspective multi-launch agreement."),
(97,"2026-09-26","Electron","Owlright, Owlright, Owlright","Synspective","Disclosed","LC-1B","Dedicated","Success","None attempted","","","",[WIKI,RL],"StriX-12. Rocket Lab release: Electron's 97th mission. Most recent Rocket Lab launch as of this run (2026-10-12)."),
]

HDR = ["Flight #","Launch Date (UTC)","Vehicle","Mission Name","Customer(s)","Customer Disclosure",
       "Launch Site","Dedicated / Rideshare","Outcome","Recovery","Contract Announcement Date",
       "Revenue - Disclosed ($)","Revenue - Estimated ($)","Direct Mission Costs ($)","Sources","Notes"]

out = "/home/user/rklb-launch-tracker/data/completed_launches.csv"
with open(out,"w",newline="") as f:
    w = csv.writer(f)
    w.writerow(HDR)
    for (fl,date,veh,mis,cust,disc,site,dr,outc,rec,cad,revd,cost,srcs,notes) in R:
        if fl == 1:
            rev_est = ""            # in-house test flight, no customer revenue
            basis = "No launch revenue - in-house test flight with no customer payload."
        else:
            rev_est = est_rev(date,veh)
            basis = est_basis(date)
        w.writerow([fl,date,veh,mis,cust,disc,site,dr,outc,rec,cad,revd,rev_est,cost,
                    " | ".join(srcs), notes + " || REVENUE BASIS: " + basis])
print("rows:", len(R))
