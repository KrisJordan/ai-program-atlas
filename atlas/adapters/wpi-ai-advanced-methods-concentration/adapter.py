"""Local concentration and its expressly permitted graduate CS/DS option pool."""

import importlib
import re
from atlas.adapters.cmu_bs.common import requirement, text

common = importlib.import_module("atlas.adapters.wpi-ai-bs.common")
PROGRAM_ID = "wpi-ai-advanced-methods-concentration"
TITLE = "Artificial Intelligence — Advanced AI Methods and Technologies concentration"
CATALOG = "https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-advanced-ai-methods-and"
GRAD = "https://wpi-grad.cleancatalog.net/artificial-intelligence/ms-in-artificial-intelligence"
SOURCES = [
    CATALOG,
    GRAD,
    "https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major",
]


def result(courses, requirements):
    return dict(
        id=PROGRAM_ID,
        title=TITLE,
        award_level="concentration",
        program_kind="concentration",
        catalog_year=None,
        curriculum_status="partial",
        courses=list(courses),
        requirements=requirements,
        notes=[
            "Component observations only; not a completeness audit. Undergraduate amounts are WPI units (one course is 1/3 unit); graduate amounts retain their source credit values without unit conversion."
        ],
    )


def req(key, title, **kw):
    source = kw.pop("source", PROGRAM_ID + "-catalog")
    return requirement(PROGRAM_ID, key, title, source, **kw)


def parse(html):
    soup, detail = common.document(
        html,
        "Artificial Intelligence Major with Concentration in Advanced AI Methods and Technologies",
    )
    body = text(detail)
    if (
        "beyond those taken to meet the core AI requirements" not in body
        or "Associated Degree Artificial Intelligence Major" not in body
    ):
        raise ValueError("Concentration relationship changed")
    match = re.search(r"must take (\d+) courses", body)
    if not match:
        raise ValueError("Concentration total missing")
    root = req(
        "total",
        "Concentration courses beyond the AI core",
        kind="choose_courses",
        count=int(match[1]),
        summary="Six distinct courses beyond the parent AI core; this inventory does not certify the host BS degree.",
    )
    courses = common.rows(detail, PROGRAM_ID + "-catalog")
    requirements = [root]
    expected = [
        "Choose at least three courses from:",
        "Choose remaining courses from:",
        "Or choose remaining course from:",
        "Note: Only one of CS 2301 or CS 2303",
    ]
    parts = common.sections(detail)
    if len(parts) != 4 or any(
        not common.description(p).startswith(e) for p, e in zip(parts, expected)
    ):
        raise ValueError("Concentration section structure changed")
    for key, title, p, count in [
        ("priority", "At least three from the advanced AI pool", parts[0], 3),
        ("remaining", "Remaining courses: undergraduate options", parts[1], None),
    ]:
        requirements.append(
            req(
                key,
                title,
                kind="choose_courses" if count else "note",
                count=count,
                parent=root["id"],
                course_ids=list(common.rows(p, PROGRAM_ID + "-catalog")),
                summary="Minimum of three courses."
                if count
                else "Optional pool for remaining courses; graduate options are also permitted.",
            )
        )
    if (
        "graduate CS and DS courses from the Core AI Bins of the MS in AI degree"
        not in common.description(parts[2])
    ):
        raise ValueError("Graduate alternative changed")
    requirements.append(
        req(
            "graduate-option",
            "Graduate alternative for advanced undergraduates",
            kind="note",
            parent=root["id"],
            summary="Remaining courses may be graduate CS/DS courses in the MS-AI core bins; see the separately sourced eligible pool.",
        )
    )
    requirements.append(
        req(
            "systems-overlap",
            "Systems programming exclusion",
            kind="note",
            summary="Only one of CS 2301 and CS 2303 may count toward the degree.",
        )
    )
    return result(courses.values(), requirements)


def parse_graduate(html):
    _, detail = common.document(html, "M.S. in Artificial Intelligence")
    core = next(
        (
            p
            for p in common.sections(detail)
            if p.find(["h2", "h3", "h4"]) and text(p.find(["h2", "h3", "h4"])) == "Core Courses:"
        ),
        None,
    )
    if core is None or "five core MS-AI bins" not in common.description(core):
        raise ValueError("MS core bins changed")
    courses = common.rows(
        core,
        PROGRAM_ID + "-graduate-core",
        base="https://wpi-grad.cleancatalog.net",
        unit="unknown",
    )
    courses = {k: c for k, c in courses.items() if re.search(r"\b(?:CS|DS)\b", c["code"])}
    if not courses:
        raise ValueError("Eligible graduate CS/DS courses missing")
    return result(
        courses.values(),
        [
            req(
                "graduate-pool",
                "Eligible graduate CS/DS core-bin options",
                source=PROGRAM_ID + "-graduate-core",
                kind="note",
                course_ids=list(courses),
                summary="Options for the concentration’s remaining-course graduate alternative; advanced undergraduates only. Graduate credits are not converted into undergraduate units.",
            )
        ],
    )


SOURCE_PARSERS = {CATALOG: parse, GRAD: parse_graduate}


def parse_parent(html):
    _, detail = common.document(html, "Artificial Intelligence Major")
    body = text(detail)
    guards = [
        "one and only one concentration",
        "6 distinct courses",
        "student's chosen concentration",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Parent concentration constraints changed")
    return result(
        [],
        [
            req(
                "parent-scope",
                "Parent AI degree relationship",
                source=PROGRAM_ID + "-parent",
                kind="note",
                summary="The AI BS requires exactly one concentration of six distinct courses, and its MQP must apply AI within that concentration. Completeness of this local concentration does not certify the host BS degree.",
            )
        ],
    )


SOURCE_PARSERS[SOURCES[2]] = parse_parent
