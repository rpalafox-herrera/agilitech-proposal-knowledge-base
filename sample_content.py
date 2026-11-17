"""Invented proposal records for a university demonstration, never company history.

Agilitech's public website supplies industry and service vocabulary only. Every
project, date, amount, quantity, duration and labor estimate below is fictional.
No real client identities or customer documents are included.
"""

SOURCE_URLS = {
    "renewable_energy": "https://www.agilitechgroup.com/our-industries/renewable-energy/",
    "water_wastewater": "https://www.agilitechgroup.com/our-industries/water-waste-water/",
    "food_beverage": "https://www.agilitechgroup.com/our-industries/food-and-beverage/",
    "manufacturing": "https://www.agilitechgroup.com/our-industries/manufacturing/",
    "mining": "https://www.agilitechgroup.com/our-industries/mining/",
    "construction": "https://www.agilitechgroup.com/our-services/electrical-construction/",
    "engineering": "https://www.agilitechgroup.com/our-services/engineering/",
    "automation": "https://www.agilitechgroup.com/our-services/control-system-automation-and-software-development/",
}


def _sample(slug, title, industry, project_type, discipline, year, budget, weeks,
            hours, scope, deliverables, assumptions):
    """Build consistently labeled, searchable text without manufacturing clients."""
    full_title = f"FICTIONAL UNIVERSITY DEMO - {title}"
    text = (
        f"{full_title}\n\n"
        "FICTIONAL UNIVERSITY DEMO. This document is synthetic training data for "
        "a student project. It is not an Agilitech proposal, completed project, "
        "quotation, engineering design, or performance claim. All project details "
        "and numbers are invented. No client is identified.\n\n"
        f"Fictional proposal year: {year}\nIndustry: {industry}\n"
        f"Project type: {project_type}\nEngineering discipline: {discipline}\n"
        "Client name: Unknown / not supplied\n\n"
        f"Hypothetical scope\n{scope}\n\n"
        f"Hypothetical deliverables\n{deliverables}\n\n"
        "Invented planning figures\n"
        f"Illustrative proposed budget: USD {budget:,.0f}\n"
        f"Illustrative planned duration: {weeks} weeks\n"
        f"Illustrative engineering labor estimate: {hours:,} hours\n"
        "These figures are fabricated proposal assumptions, not actual costs, "
        "savings, results, commitments, or validated estimates.\n\n"
        f"Hypothetical assumptions and exclusions\n{assumptions}\n\n"
        "Public website industry and service categories inspired this exercise "
        "only. Real historical proposals and confidential information were not used.\n"
    )
    return {
        "filename": f"fictional_{slug}.txt",
        "title": full_title,
        "industry": industry,
        "project_type": project_type,
        "engineering_discipline": discipline,
        "proposal_year": year,
        "client_name": "",
        "description": f"Fictional university demo: {title.lower()}. All figures and project details are invented.",
        "text": text,
        "budget_usd": budget,
        "duration_weeks": weeks,
        "engineering_hours": hours,
    }


SAMPLES = [
    _sample(
        "water_recovery_2007", "Process Water Recovery Study",
        "Water/Wastewater", "Feasibility study", "Process", 2007,
        185_000, 12, 920,
        "Evaluate a fictional water recovery loop with screening, sand filtration "
        "and ultraviolet disinfection. The exercise assumes a non-potable process "
        "water stream of 40,000 gallons per day; this capacity is invented.",
        "Prepare a process flow diagram, preliminary equipment list, water balance, "
        "and comparison of two hypothetical treatment arrangements.",
        "Actual feed-water quality, reuse requirements, permits and site conditions "
        "are unknown. No recovery rate or water quality outcome is guaranteed.",
    ),
    _sample(
        "electrical_construction_2010", "Packaging Plant Electrical Upgrade",
        "Manufacturing", "Electrical construction", "Electrical", 2010,
        740_000, 18, 1_600,
        "Plan fictional industrial electrical construction for a packaging area, "
        "including switchgear coordination, cable routing, grounding and motor "
        "control center connections for 12 assumed motors.",
        "Develop a single-line diagram, cable schedule, installation work packages, "
        "and a proposed commissioning checklist.",
        "Motor loads and quantities are invented. Existing drawings, utility data "
        "and shutdown windows would require verification before real design work.",
    ),
    _sample(
        "cip_controls_2012", "Beverage Cleaning Controls Modernization",
        "Food & Beverage", "Automation upgrade", "Controls and Automation", 2012,
        420_000, 16, 1_250,
        "Describe a fictional clean-in-place (CIP) controls upgrade for three "
        "assumed tanks and a valve cluster. Include operator interface screens, "
        "sequence documentation and PLC programming in the demonstration scope.",
        "Produce a control narrative, input/output list, operator screen mockups, "
        "and a hypothetical factory acceptance test plan.",
        "Cleaning recipes, hygienic criteria and acceptance limits are unknown. "
        "The demo does not claim food safety validation or production improvement.",
    ),
    _sample(
        "mining_dust_2014", "Mineral Handling Dust Collection Study",
        "Mining", "Engineering study", "Mechanical", 2014,
        265_000, 14, 1_100,
        "Assess hypothetical dust collection around two fictional conveyor "
        "transfer points. Compare duct layouts and model airflow for an invented "
        "downstream mineral processing area.",
        "Prepare a conceptual collection layout, fan selection comparison and "
        "maintenance access review for the fictional facility.",
        "Dust properties, measured emissions and site constraints are unknown. "
        "No compliance status or emission reduction percentage is asserted.",
    ),
    _sample(
        "pump_station_2016", "Wastewater Pump Station Controls Renewal",
        "Water/Wastewater", "Controls modernization", "Controls and Automation", 2016,
        560_000, 20, 1_800,
        "Propose fictional SCADA visibility, level instrumentation and alarm "
        "rationalization for a wastewater pump station with four assumed pumps. "
        "Provide planned loop checks and startup support as classroom examples.",
        "Prepare an alarm register, instrument list, control panel drawings and "
        "a hypothetical site acceptance test script.",
        "Pump capacities and operating conditions are unknown. The assumed pump "
        "count and all planning figures are synthetic, with no reliability claim.",
    ),
    _sample(
        "solar_installation_2018", "Warehouse Rooftop Solar Installation",
        "Renewable Energy", "Solar installation", "Electrical", 2018,
        1_380_000, 24, 2_100,
        "Outline a fictional solar installation for a warehouse roof with an "
        "assumed 600 kW DC array. Include conceptual electrical design, structural "
        "review coordination, utility coordination and commissioning planning.",
        "Prepare a conceptual array layout, single-line diagram, permitting "
        "document list and illustrative construction schedule.",
        "Array capacity is invented. Roof suitability, tariffs and interconnection "
        "conditions are unknown. No generation, payback or savings is promised.",
    ),
    _sample(
        "food_piping_2020", "Food Processing Utility Piping Layout",
        "Food & Beverage", "Facility upgrade", "Mechanical", 2020,
        930_000, 22, 2_400,
        "Create a fictional utility piping arrangement for a food processing "
        "expansion. The example includes 180 meters of assumed pipe routing, "
        "equipment access review, a laser scanning allowance and 3D coordination.",
        "Prepare a conceptual piping model, equipment arrangement, preliminary "
        "materials list and installation sequencing notes.",
        "Routing length, equipment positions and utility demands are invented. "
        "Detailed sanitary design and pressure calculations are outside this demo.",
    ),
    _sample(
        "battery_microgrid_2022", "Industrial Battery and Microgrid Concept",
        "Renewable Energy", "Microgrid feasibility", "Electrical", 2022,
        2_150_000, 28, 2_900,
        "Explore a fictional microgrid concept integrating solar, a hypothetical "
        "1 MWh battery and selected warehouse loads. Compare assumed grid-tied "
        "operating scenarios and outline energy management interfaces.",
        "Produce a conceptual system diagram, scenario comparison, equipment "
        "interface list and proposed commissioning approach.",
        "Battery size is invented; load profiles, tariffs, outage requirements "
        "and system studies are unknown. No backup duration or ROI is claimed.",
    ),
    _sample(
        "manufacturing_scada_2024", "Manufacturing SCADA and Alarm Refresh",
        "Manufacturing", "Automation upgrade", "Controls and Automation", 2024,
        610_000, 18, 1_750,
        "Describe a fictional SCADA refresh for an industrial mixing line. "
        "Include operator screen redesign, alarm documentation and a training "
        "plan for eight hypothetical operator stations.",
        "Prepare screen prototypes, a tag register, an alarm review workbook "
        "and a factory acceptance test checklist.",
        "Station count and effort are invented. Existing controls platforms, "
        "cybersecurity requirements and measured downtime are unknown.",
    ),
    _sample(
        "ev_charging_2026", "Commercial Fleet Charging Concept",
        "Commercial", "EV charging infrastructure", "Electrical", 2026,
        875_000, 20, 1_950,
        "Develop a fictional EV charging concept for a commercial fleet yard "
        "with 16 assumed Level 2 charging ports. Include demand management, "
        "utility service coordination and preliminary equipment placement.",
        "Prepare a conceptual site plan, load assumptions register, single-line "
        "diagram and an illustrative procurement sequence.",
        "Port quantity is invented. Vehicle duty cycles and service capacity "
        "are unknown; no charging time, energy saving or project approval is claimed.",
    ),
]


# The original ten hand-written examples remain stable for tutorials and tests.
# The larger classroom archive is deterministic, has no real clients, and fills
# each industry to exactly two invented proposals per year from 2007 to 2026.
_BRANCHES = [
    ("Water/Wastewater", "water", 140_000, [
        ("Cooling Loop Water Recovery Review", "Feasibility study", "Process",
         "compare a fictional water recovery loop, screening arrangement and non-potable reuse alternatives",
         "a water balance, conceptual process flow diagram and assumptions register"),
        ("Pump Station Instrumentation Package", "Controls modernization", "Controls and Automation",
         "outline level instrumentation, pump permissives and SCADA alarm visibility for an assumed pump station",
         "an instrument list, control narrative and illustrative loop-check plan"),
        ("Treatment Yard Utility Piping Concept", "Facility upgrade", "Mechanical",
         "coordinate invented utility piping routes and equipment access for an illustrative treatment yard",
         "a conceptual piping layout, access review and preliminary material schedule"),
        ("Filtration Skid Electrical Coordination", "Electrical construction", "Electrical",
         "plan electrical service routing and motor control connections for hypothetical filtration skids",
         "a single-line concept, cable schedule and installation sequence"),
        ("Tank Farm Flow Metering Review", "Engineering study", "Process",
         "compare fictional flow metering locations and sample collection points around a process water tank farm",
         "a metering concept, sampling point list and preliminary equipment comparison"),
        ("Wastewater Control Panel Renewal", "Panel fabrication", "Controls and Automation",
         "describe hypothetical control panel interfaces, operator displays and renewal sequencing",
         "panel drawing concepts, an input/output schedule and acceptance-test outline"),
    ]),
    ("Renewable Energy", "renewable", 420_000, [
        ("Solar Canopy Installation Concept", "Solar installation", "Electrical",
         "outline a fictional solar installation with conceptual array placement and electrical interconnection planning",
         "an array concept, single-line diagram and illustrative permitting document list"),
        ("Battery Dispatch Controls Review", "Automation upgrade", "Controls and Automation",
         "compare invented battery dispatch modes and energy management interface requirements",
         "a control narrative, operating scenario comparison and interface schedule"),
        ("Microgrid Load Coordination Study", "Microgrid feasibility", "Electrical",
         "review assumed microgrid load groups and compare illustrative grid-connected operating arrangements",
         "a conceptual system diagram, load assumptions register and coordination notes"),
        ("Energy Facility Cable Routing Package", "Electrical construction", "Electrical",
         "plan fictional industrial electrical construction cable routes and grounding interfaces for energy equipment",
         "a routing concept, cable quantities register and proposed inspection checklist"),
        ("Renewable Site Equipment Layout", "Engineering study", "Mechanical",
         "coordinate hypothetical equipment clearances, maintenance access and mechanical arrangement for a renewable energy yard",
         "an equipment layout, access study and preliminary procurement schedule"),
        ("Solar Monitoring Panel Concept", "Panel fabrication", "Controls and Automation",
         "describe invented solar monitoring signals, data display screens and control panel interfaces",
         "a signal register, panel drawing concepts and illustrative commissioning sequence"),
    ]),
    ("Manufacturing", "manufacturing", 225_000, [
        ("Assembly Line Electrical Expansion", "Electrical construction", "Electrical",
         "plan fictional industrial electrical construction for assumed assembly-line loads, grounding and cable routing",
         "a single-line concept, load register and installation work packages"),
        ("Mixing Line SCADA Modernization", "Automation upgrade", "Controls and Automation",
         "describe hypothetical SCADA screens, alarm organization and operator training for an industrial mixing line",
         "screen concepts, a tag schedule and factory acceptance-test outline"),
        ("Production Utility Piping Survey", "Engineering study", "Mechanical",
         "review invented utility piping routes, equipment clearances and maintenance access around production equipment",
         "a conceptual piping layout, survey assumptions and material comparison"),
        ("Motor Control Center Renewal", "Facility upgrade", "Electrical",
         "compare assumed motor control center replacement sequences and temporary power interfaces",
         "a renewal concept, shutdown assumptions register and proposed startup checklist"),
        ("Process Skid Instrumentation Package", "Controls modernization", "Controls and Automation",
         "outline fictional process-skid instrumentation, interlocks and operator display requirements",
         "an input/output list, control narrative and loop-check worksheet"),
        ("Factory Equipment Arrangement Concept", "Feasibility study", "Mechanical",
         "coordinate assumed equipment positions, access paths and installation sequences for a manufacturing area",
         "an arrangement concept, access review and illustrative construction schedule"),
    ]),
    ("Food & Beverage", "food_beverage", 190_000, [
        ("Beverage Batch Controls Refresh", "Automation upgrade", "Controls and Automation",
         "describe fictional beverage batching sequences, operator screens and alarm review activities",
         "a control narrative, screen concepts and illustrative acceptance-test plan"),
        ("Cleaning Utility Distribution Study", "Engineering study", "Mechanical",
         "compare hypothetical clean-in-place utility distribution layouts and equipment maintenance access",
         "a utility piping concept, equipment assumptions and installation sequence"),
        ("Packaging Hall Electrical Package", "Electrical construction", "Electrical",
         "plan fictional industrial electrical construction for assumed packaging equipment loads and service routing",
         "a load register, single-line concept and proposed inspection checklist"),
        ("Food Process Instrument Renewal", "Controls modernization", "Controls and Automation",
         "outline invented process instrumentation, signal interfaces and operator visibility for a food processing area",
         "an instrument list, interface schedule and loop-check outline"),
        ("Cold Utility Equipment Coordination", "Facility upgrade", "Mechanical",
         "coordinate hypothetical utility equipment placement, piping interfaces and access clearances",
         "a conceptual equipment arrangement, utility assumptions and procurement comparison"),
        ("Tank Transfer Sequencing Concept", "Feasibility study", "Process",
         "compare invented tank transfer sequences, valve routing concepts and operator handoff requirements",
         "a process flow concept, valve schedule and operating assumptions register"),
    ]),
    ("Mining", "mining", 245_000, [
        ("Conveyor Transfer Dust Collection", "Engineering study", "Mechanical",
         "compare fictional dust collection duct layouts and maintenance access at assumed conveyor transfer points",
         "a collection concept, fan comparison and access review"),
        ("Mineral Handling Controls Upgrade", "Automation upgrade", "Controls and Automation",
         "describe hypothetical conveyor permissives, level signals and operator alarm displays for mineral handling",
         "a control narrative, signal schedule and illustrative factory-test checklist"),
        ("Crusher Area Electrical Renewal", "Electrical construction", "Electrical",
         "plan fictional industrial electrical construction routes and motor control interfaces around assumed crushing equipment",
         "a single-line concept, cable register and proposed installation sequence"),
        ("Process Water Reuse Screening", "Feasibility study", "Process",
         "review invented water recovery alternatives and non-potable reuse arrangements for a mineral processing area",
         "a conceptual water balance, equipment comparison and assumptions register"),
        ("Material Yard Equipment Layout", "Facility upgrade", "Mechanical",
         "coordinate fictional equipment clearances, material flow and maintenance access in an assumed handling yard",
         "an equipment arrangement, access review and illustrative sequencing plan"),
        ("Slurry Instrumentation Coordination", "Controls modernization", "Controls and Automation",
         "outline hypothetical metering signals, alarm groups and control panel interfaces for an assumed slurry loop",
         "an instrument register, control interface concept and loop-check worksheet"),
    ]),
    ("Commercial", "commercial", 165_000, [
        ("Fleet Yard Charging Expansion", "EV charging infrastructure", "Electrical",
         "outline a fictional commercial fleet charging layout, demand management concept and utility interface",
         "a conceptual site plan, load assumptions register and equipment schedule"),
        ("Building Service Electrical Review", "Engineering study", "Electrical",
         "compare hypothetical building service arrangements, distribution routing and assumed equipment loads",
         "a single-line concept, load register and coordination notes"),
        ("Commercial Mechanical Room Layout", "Facility upgrade", "Mechanical",
         "coordinate invented utility equipment clearances, piping interfaces and maintenance access within a mechanical room",
         "a conceptual arrangement, access review and preliminary material list"),
        ("Site Lighting Controls Modernization", "Automation upgrade", "Controls and Automation",
         "describe fictional lighting control zones, operator interfaces and alarm visibility for an illustrative site",
         "a controls concept, signal register and acceptance-test outline"),
        ("Facility Power Renewal Package", "Electrical construction", "Electrical",
         "plan fictional industrial electrical construction sequences for assumed commercial facility power distribution",
         "installation work packages, a cable schedule and startup assumptions"),
        ("Utility Monitoring Panel Concept", "Panel fabrication", "Controls and Automation",
         "describe hypothetical utility monitoring signals, panel interfaces and operator display requirements",
         "panel drawing concepts, an input/output list and illustrative commissioning plan"),
    ]),
]


def _expanded_archive():
    archive = list(SAMPLES)
    for industry, slug, base_budget, topics in _BRANCHES:
        existing = [s for s in SAMPLES if s["industry"] == industry]
        scenario = 0
        for year in range(2007, 2027):
            occupied = sum(s["proposal_year"] == year for s in existing)
            for annual_slot in range(occupied, 2):
                topic, project_type, discipline, scope, deliverables = topics[scenario % len(topics)]
                package = "A" if annual_slot == 0 else "B"
                quantity = 3 + (scenario * 5 + year) % 19
                budget = base_budget + (year - 2007) * 12_500 + (scenario % 9) * 37_500
                weeks = 8 + (scenario * 3 + year) % 25
                hours = 480 + (scenario * 145 + (year - 2007) * 35) % 3_600
                archive.append(_sample(
                    f"archive_{slug}_{year}_{package.lower()}",
                    f"{topic} {year} Study {package}", industry, project_type,
                    discipline, year, budget, weeks, hours,
                    f"For fictional study package {package} in {year}, {scope}. "
                    f"The classroom scenario assumes {quantity} equipment or interface review items. "
                    "That count is invented and does not describe an actual facility.",
                    f"Prepare {deliverables}. Compare the base arrangement with an alternative "
                    f"for the {quantity} assumed review items, documenting unresolved site questions.",
                    "All project identities, quantities, budgets, dates, schedules and labor estimates "
                    "are fictional classroom assumptions. Client identity, site conditions, actual "
                    "equipment ratings, utility data, regulatory requirements and acceptance criteria "
                    "are unknown. No performance, savings, compliance or completion claim is made.",
                ))
                scenario += 1
    return archive


# Keep the starter library realistic enough to browse without overwhelming a
# beginner. The original ten records remain, plus four extra fictional records
# per industry (24 additions, 34 records total). The generation recipe above
# deliberately supports a much larger stress-test archive, but that is not the
# default demo collection.
_FULL_ARCHIVE_SAMPLES = _expanded_archive()
ARCHIVE_SAMPLES = list(SAMPLES)
for _industry in sorted({sample["industry"] for sample in SAMPLES}):
    ARCHIVE_SAMPLES.extend([
        sample for sample in _FULL_ARCHIVE_SAMPLES
        if sample["industry"] == _industry and sample["filename"].startswith("fictional_archive_")
    ][:4])
