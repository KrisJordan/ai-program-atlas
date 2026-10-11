"""WPI AI degree distribution; linked general degree/concentration work stays partial."""

import importlib
from fractions import Fraction
from atlas.adapters.cmu_bs.common import requirement, text, slug

common = importlib.import_module("atlas.adapters.wpi-ai-bs.common")
PROGRAM_ID = "wpi-ai-bs"
TITLE = "Artificial Intelligence"
SOURCES = [
    "https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major",
    "https://www.wpi.edu/academics/study/artificial-intelligence-bs",
]


def req(key, title, **kw):
    return requirement(PROGRAM_ID, key, title, PROGRAM_ID + "-catalog", **kw)


def parse(html):
    _, detail = common.document(html, "Artificial Intelligence Major")
    parts = common.sections(detail)
    top = [p for p in parts if not p.find_parent("div", class_="paragraph--type--degree-section")]
    byhead = {text(p.find(["h3", "h4"])): p for p in top if p.find(["h3", "h4"])}
    headings = [
        "Degree Distribution Requirements for the Artificial Intelligence Major",
        "Computer Science Foundation",
        "Mathematical Sciences Foundation",
        "AI Core Courses",
        "AI Ethics and Social Implications",
        "Natural or Engineering Science",
        "Concentration",
        "Disciplinary AI Electives",
        "Major Qualifying Project (MQP)",
    ]
    if any(h not in byhead for h in headings):
        raise ValueError("AI degree section missing")
    body = text(detail)
    guards = [
        "one and only one concentration",
        "at least 4/3 units",
        "no more than 1/3 unit at the 1000 level",
        "Choose 8/3 units",
        "at least 2/3 units at the 4000-level",
        "6 distinct courses",
        "10 units program requirements",
    ]
    if any(g not in body for g in guards):
        raise ValueError("AI degree constraint changed")
    courses = common.rows(detail, PROGRAM_ID + "-catalog")
    requirements = []
    root = req(
        "distribution",
        "AI degree distribution",
        credits=10,
        summary="Ten WPI units of program distribution; standard university BS requirements also apply.",
    )
    requirements.append(root)
    requirements.append(
        req(
            "advanced",
            "Advanced-level coursework",
            kind="note",
            parent=root["id"],
            summary="At least 4/3 units across the degree must be at 4000 level or above.",
        )
    )
    cs = req("cs", "Computer science foundation", credits=1, parent=root["id"])
    requirements.append(cs)
    csrows = common.rows(byhead["Computer Science Foundation"], PROGRAM_ID + "-catalog")
    alg = [c["id"] for c in csrows.values() if c["code"] == "CS 2223"]
    if len(alg) != 1:
        raise ValueError("Algorithms requirement changed")
    requirements.append(
        req("algorithms", "Algorithms", parent=cs["id"], course_ids=alg, credits=1 / 3)
    )
    intro = req(
        "intro",
        "Introductory CS: choose two of three groups",
        kind="alternative",
        count=2,
        credits=2 / 3,
        parent=cs["id"],
        summary="Choose two groups, at most one 1000-level course (1/3 unit).",
    )
    requirements.append(intro)
    intro_parts = [
        p
        for p in common.sections(byhead["Computer Science Foundation"])
        if common.description(p).startswith("CS ")
    ]
    if len(intro_parts) != 3:
        raise ValueError("CS introductory alternatives changed")
    for i, p in enumerate(intro_parts):
        requirements.append(
            req(
                "intro-" + str(i + 1),
                common.description(p),
                kind="choose_courses",
                count=1,
                parent=intro["id"],
                course_ids=list(common.rows(p, PROGRAM_ID + "-catalog")),
            )
        )
    requirements.append(
        req(
            "cs-substitution",
            "CS proficiency substitutions",
            kind="note",
            parent=cs["id"],
            summary="Students who demonstrate proficiency may petition for a more advanced CS replacement. Recommended preparation for the Advanced AI concentration is CS1101/1102 then CS2102/2103.",
        )
    )
    math = req("math", "Mathematics foundation", parent=root["id"], credits=5 / 3)
    requirements.append(math)
    for i, g in enumerate(
        byhead["Mathematical Sciences Foundation"].find_all(
            "article", class_="node--type-elective-group"
        )
    ):
        label = text(g.find("button").find("span"))
        amount = float(Fraction(text(g.find("span", class_="field--name-field-elective-credits"))))
        requirements.append(
            req(
                "math-" + str(i + 1),
                label,
                kind="all" if label.startswith("Both ") else "choose_credits",
                credits=amount,
                parent=math["id"],
                course_ids=list(common.rows(g, PROGRAM_ID + "-catalog")),
                summary=label + "; use Mathematics department procedures for substitutions.",
            )
        )
    calculus = next((r for r in requirements if r["id"] == PROGRAM_ID + "-math-3"), None)
    if calculus is None:
        raise ValueError("Calculus group missing")
    for j, p in enumerate(common.sections(byhead["Mathematical Sciences Foundation"])):
        if common.description(p).startswith(("MA 1020 or MA 1021", "MA 1022 or MA 1120")):
            requirements.append(
                req(
                    "calculus-" + str(j),
                    common.description(p),
                    kind="choose_courses",
                    count=1,
                    parent=calculus["id"],
                    course_ids=list(common.rows(p, PROGRAM_ID + "-catalog")),
                )
            )
    core = req(
        "core",
        "AI core",
        kind="choose_credits",
        credits=8 / 3,
        parent=root["id"],
        summary="8/3 units from the core pool, subject to the required bins; at least 2/3 must be at 4000 level or above.",
    )
    requirements.append(core)
    bins = []
    for g in detail.find_all("article", class_="node--type-elective-group"):
        button = g.find("button")
        label = text(button.find("span")) if button else ""
        if label.startswith(
            ("AI Foundations:", "AI Overview:", "Machine Learning:", "Interaction and Reasoning:")
        ):
            pool = common.rows(g, PROGRAM_ID + "-catalog")
            core["course_ids"] += list(pool)
            count = 3 if label.startswith("AI Foundations:") else 1
            bins.append(
                req(
                    "core-" + slug(label.split(":")[0]),
                    label.split(":")[0],
                    kind="choose_courses",
                    count=count,
                    parent=core["id"],
                    course_ids=list(pool),
                    summary="Required minimum from this core bin.",
                )
            )
    if len(bins) != 4:
        raise ValueError("AI core bins changed")
    requirements += bins
    ethics = common.rows(byhead["AI Ethics and Social Implications"], PROGRAM_ID + "-catalog")
    requirements.append(
        req(
            "ethics",
            "AI ethics and social implications",
            kind="choose_credits",
            credits=1 / 3,
            parent=root["id"],
            category="human_context",
            course_ids=list(ethics),
        )
    )
    requirements.append(
        req(
            "science",
            "Natural or engineering science",
            kind="choose_credits",
            credits=2 / 3,
            parent=root["id"],
            category="foundations",
            summary="Eligible prefixes: AE, AREN, BB, BCB, BME, CE, CH, CHE, ECE, ES, GE, ME, NEU, PH, RBE. Overlap with concentration/electives requires additional distribution courses to retain ten program units.",
        )
    )
    requirements.append(
        req(
            "concentration",
            "Exactly one concentration",
            kind="alternative",
            count=1,
            credits=2,
            parent=root["id"],
            summary="Six distinct courses in exactly one published AI concentration. Each child inventory specifies its own course choices and restrictions.",
        )
    )
    requirements.append(
        req(
            "disciplinary",
            "Disciplinary AI electives",
            kind="choose_credits",
            credits=2 / 3,
            parent=root["id"],
            category="electives",
            summary="Choose from any AI concentration or AI core, subject to course prerequisites.",
        )
    )
    requirements.append(
        req(
            "mqp",
            "AI Major Qualifying Project",
            credits=1,
            parent=root["id"],
            category="applications",
            summary="Apply AI in the chosen concentration. A sole adviser must be AI core/collaborative faculty in that discipline; otherwise use AI and disciplinary co-advisers.",
        )
    )
    return dict(
        id=PROGRAM_ID,
        title=TITLE,
        award_level="BS",
        program_kind="degree",
        catalog_year=None,
        curriculum_status="partial",
        courses=list(courses.values()),
        requirements=requirements,
        notes=[
            "Program distribution observed; university BS requirements and all concentration inventories remain separate unresolved sources. WPI units remain fractional."
        ],
    )


metadata = importlib.import_module("atlas.adapters.wpi-ai-bs.course_metadata")
metadata.attach(globals(), ["CS 2119", "CS 4341", "CS 4342"])

concentrations = importlib.import_module("atlas.adapters.wpi-ai-bs.concentrations")
concentrations.attach(globals())

policies = importlib.import_module("atlas.adapters.wpi-ai-bs.degree_policies")
policies.attach(globals())

# Clarification source: directs transfer decisions to the HUA coordinator/catalog.
SOURCES.append("https://www.wpi.edu/academics/departments/humanities-arts/resources")

from atlas.adapters import wpi_policy_followup as followup

def parse_registrar_graduation(html):
    return followup.parse_graduation(html, PROGRAM_ID)

SOURCES.append(followup.GRADUATION_URL)
SOURCE_PARSERS[followup.GRADUATION_URL] = parse_registrar_graduation
