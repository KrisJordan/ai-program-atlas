"""Observe WPI business-AI distribution without mistaking pool totals for minima."""

import importlib
from fractions import Fraction
from atlas.adapters.cmu_bs.common import requirement, text, slug

common = importlib.import_module("atlas.adapters.wpi-ai-bs.common")
PROGRAM_ID = "wpi-business-analytics-applied-ai-bs"
TITLE = "Business Analytics & Applied AI"
SOURCES = [
    "https://wpi.cleancatalog.net/business/business-analytics-and-applied-ai-major",
    "https://www.wpi.edu/academics/study/business-analytics-applied-ai-bs",
]


def req(key, title, **kw):
    return requirement(PROGRAM_ID, key, title, PROGRAM_ID + "-catalog", **kw)


def parse(html):
    _, detail = common.document(html, "Business Analytics and Applied AI Major")
    top = [
        p
        for p in common.sections(detail)
        if not p.find_parent("div", class_="paragraph--type--degree-section")
    ]
    headings = {text(p.find(["h3", "h4"])): p for p in top if p.find(["h3", "h4"])}
    needed = [
        "Mathematics and Science Requirements",
        "Computer Science",
        "Basic Science",
        "Business Foundation",
        "Technical and AI Foundation",
        "Analytics Foundation",
        "Business Analytics and Applied AI Electives",
        "MQP",
        "Additional Notes:",
        "BS/MS Rules for Graduate Business Degree",
        "Transfer Students and Transfer Credit",
    ]
    if any(h not in headings for h in needed):
        raise ValueError("Business AI section missing")
    body = text(detail)
    guards = [
        "Select a total of six electives",
        "Each course may only count in one slot",
        "may not double major in Marketing Analytics",
        "accepted into a graduate business program",
        "prior written permission",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Business AI constraint changed")
    courses = common.rows(detail, PROGRAM_ID + "-catalog")
    requirements = []
    math = req(
        "math",
        "Mathematics",
        credits=5 / 3,
        category="mathematics",
        summary="2/3 calculus, 2/3 statistics, 1/3 linear algebra. Named courses are recommendations; equivalent preparation is allowed.",
    )
    requirements.append(math)
    for i, g in enumerate(detail.find_all("article", class_="node--type-elective-group")):
        b = g.find("button")
        label = text(b.find("span")) if b and b.find("span") else ""
        if label.startswith("Recommended:"):
            c = g.find("span", class_="field--name-field-elective-credits")
            amount = float(Fraction(text(c))) if c else None
            requirements.append(
                req(
                    "math-" + str(i),
                    label.split(" - ")[0],
                    kind="choose_credits",
                    credits=amount,
                    parent=math["id"],
                    category="mathematics",
                    course_ids=list(common.rows(g, PROGRAM_ID + "-catalog")),
                    summary="Recommended course options; approved equivalents may satisfy this area.",
                )
            )
    for heading, key, expected in [
        ("Computer Science", "cs", 1),
        ("Business Foundation", "business", 5),
        ("Technical and AI Foundation", "technical", 4),
        ("Analytics Foundation", "analytics", 4),
    ]:
        parent = req(key, heading, category="foundations" if key in ("cs", "business") else "ai_ml")
        requirements.append(parent)
        groups = headings[heading].find_all("article", class_="node--type-elective-group")
        if len(groups) != expected:
            raise ValueError("Slot structure changed: " + heading)
        for i, g in enumerate(groups):
            label = text(g.find("button").find("span"))
            pool = common.rows(g, PROGRAM_ID + "-catalog")
            requirements.append(
                req(
                    key + "-" + str(i + 1),
                    heading + " slot " + str(i + 1),
                    kind="choose_courses",
                    count=1,
                    parent=parent["id"],
                    course_ids=list(pool),
                    summary=label,
                )
            )
    requirements.append(
        req(
            "science",
            "Basic science",
            kind="note",
            category="foundations",
            summary="Eligible prefixes: BB, CH, GE, PH. The program page does not state a credit quantity; it is unresolved.",
        )
    )
    electives = req(
        "electives",
        "Six electives across three categories",
        kind="choose_courses",
        count=6,
        category="electives",
    )
    requirements.append(electives)
    configs = [
        (
            "Business Analytics Applications (Select at least 3)",
            "applications",
            3,
            "At least three courses in business analytics applications.",
        ),
        (
            "Computing Technologies, Data and Mathematical Sciences (Maximum 3)",
            "computing",
            None,
            "At most three: CS3000+ except CS3043; DS/MA2000+; CS2119 or MIS2300.",
        ),
        (
            "Business and Entrepreneurship (Maximum 2):",
            "entrepreneurship",
            None,
            "At most two: previously unused OBC courses, BUS1020/BUS2020, ETR courses, or MIS3010.",
        ),
    ]
    for prefix, key, count, summary in configs:
        p = next((p for p in top if common.description(p).startswith(prefix)), None)
        if p is None:
            raise ValueError("Elective category changed")
        pool_ids = list(common.rows(p, PROGRAM_ID + "-catalog"))
        electives["course_ids"] = list(dict.fromkeys(electives["course_ids"] + pool_ids))
        requirements.append(
            req(
                "electives-" + key,
                prefix,
                kind="choose_courses" if count else "note",
                count=count,
                parent=electives["id"],
                category="electives",
                course_ids=pool_ids,
                summary=summary,
            )
        )
    for key, title, summary in [
        (
            "mqp",
            "Major Qualifying Project",
            "Required senior capstone supervised by full-time Business School faculty who teach analytics, AI or STEM.",
        ),
        (
            "overlap",
            "Overlap and double-major restrictions",
            "Each course fills only one program slot. A simultaneous Marketing Analytics major is prohibited.",
        ),
        (
            "graduate",
            "Graduate-course substitutions",
            "WPI limits on graduate credit apply. Admission to a graduate business program must precede graduate business courses; undergraduate versions do not satisfy corresponding graduate requirements.",
        ),
        (
            "transfer",
            "Transfer after matriculation",
            "Off-campus study after WPI matriculation needs prior written permission for transferable credit.",
        ),
    ]:
        requirements.append(req(key, title, kind="note", summary=summary))
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
            "Observed program-specific distribution; university degree policies and unspecified basic-science quantity remain unresolved. Displayed elective-table subtotals sum option pools and are not requirement minima."
        ],
    )


metadata = importlib.import_module("atlas.adapters.wpi-ai-bs.course_metadata")
metadata.attach(globals(), ["CS 2119", "CS 4341", "CS 4342", "MIS 3730", "MIS 3787"])

policies = importlib.import_module("atlas.adapters.wpi-ai-bs.degree_policies")
policies.attach(globals())

SOURCES.append("https://www.wpi.edu/academics/departments/humanities-arts/resources")

from atlas.adapters import wpi_policy_followup as followup

def parse_registrar_graduation(html):
    return followup.parse_graduation(html, PROGRAM_ID)

SOURCES.append(followup.GRADUATION_URL)
SOURCE_PARSERS[followup.GRADUATION_URL] = parse_registrar_graduation

def parse_business_bsms_faq(html):
    return followup.parse_business_bsms(html, PROGRAM_ID)

SOURCES.append(followup.BSMS_URL)
SOURCE_PARSERS[followup.BSMS_URL] = parse_business_bsms_faq


# Subject observations are independent of requirement slots and pool membership.
from atlas.adapters.wpi_degree_subjects import observe as observe_subjects
parse = observe_subjects(parse)
SOURCE_PARSERS = {url: observe_subjects(parser) for url, parser in SOURCE_PARSERS.items()}
