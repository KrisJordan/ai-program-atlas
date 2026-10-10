"""All eleven official AI concentration distributions, observed per source."""

import importlib
import re
from fractions import Fraction
from atlas.adapters.cmu_bs.common import course, requirement, text, slug

common = importlib.import_module("atlas.adapters.wpi-ai-bs.common")
PID = "wpi-ai-bs"
BASE = "https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-"
CONCENTRATIONS = {
    "advanced-ai": ("Advanced AI Methods and Technologies", "advanced-ai-methods-and"),
    "environment": ("Built and Natural Environment", "built-and-natural"),
    "business": ("Business Applications", "business-applications"),
    "ece": ("Electrical and Computer Engineering", "electrical-and-computer"),
    "experience": ("Experience Design", "experience-design"),
    "biotechnology": ("Life Sciences and Biotechnology", "life-sciences-and-0"),
    "biochemistry": ("Life Sciences and Molecular Biochemistry", "life-sciences-and"),
    "optimization": ("Optimization and Decision Theory", "optimization-and"),
    "robotics": ("Robotics Engineering", "robotics-engineering"),
    "social-policy": ("Social Science and Policy Concentration", "social-science-and"),
    "chemical": ("Sustainable Chemical Production", "sustainable-chemical"),
}
NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "six": 6}


def candidate(courses, requirements):
    return dict(
        id=PID,
        title="Artificial Intelligence",
        award_level="BS",
        program_kind="degree",
        catalog_year=None,
        curriculum_status="partial",
        courses=list(courses),
        requirements=requirements,
        notes=[
            "One observed concentration component, not a degree completeness claim. Choose exactly one whole concentration; disciplinary electives may use other concentration pools."
        ],
    )


def parse(html, key):
    name, suffix = CONCENTRATIONS[key]
    _, detail = common.document(html, "Artificial Intelligence Major with Concentration in " + name)
    source = PID + "-concentration-" + key

    def req(rid, title, **kw):
        return requirement(PID, "concentration-" + key + "-" + rid, title, source, **kw)

    body = text(detail)
    if "Associated Degree Artificial Intelligence Major" not in body:
        raise ValueError("Concentration parent association changed")
    if not re.search(r"(?:6 courses|6/3 units)", body):
        raise ValueError("Six-course concentration scope missing")
    courses = common.rows(detail, source)
    root = req(
        "total",
        name,
        kind="choose_courses",
        count=6,
        credits=2,
        course_ids=list(courses),
        summary="Six distinct courses in this concentration; all local bin and exclusion rules apply.",
    )
    requirements = [root]
    parts = [
        p
        for p in common.sections(detail)
        if not p.find_parent("div", class_="paragraph--type--degree-section")
    ]
    for i, p in enumerate(parts):
        label = common.description(p)
        pool = common.rows(p, source)
        groups = p.find_all("article", class_="node--type-elective-group")
        # Named graduate course options use an elective-group wrapper instead of class rows.
        for g in groups:
            button = g.find("button")
            lab = text(button.find("span")) if button and button.find("span") else ""
            match = re.fullmatch(r"(IMGD \d+): (.+)", lab)
            if match:
                credits = g.find("span", class_="field--name-field-elective-credits")
                amount = float(Fraction(text(credits))) if credits else None
                c = course(
                    match[1], match[2], source, BASE + suffix, credits=amount, institution="wpi"
                )
                pool[c["id"]] = c
                courses[c["id"]] = c
                root["course_ids"].append(c["id"])
        if not label:
            raise ValueError("Unlabeled top-level concentration section")
        if label.startswith("Required"):
            rule = req(
                "section-" + str(i), label, kind="all", parent=root["id"], course_ids=list(pool)
            )
            for j, g in enumerate(groups):
                options = common.rows(g, source)
                if options:
                    rule["course_ids"] = [c for c in rule["course_ids"] if c not in options]
                    requirements.append(
                        req(
                            "required-alternative-" + str(j),
                            "Choose one probability course",
                            kind="choose_courses",
                            count=1,
                            parent=rule["id"],
                            course_ids=list(options),
                        )
                    )
            requirements.append(rule)
        elif re.match(r"Choose (?:at least )?(one|two|three)\b", label, re.I):
            word = re.match(r"Choose (?:at least )?(one|two|three)", label, re.I)[1].lower()
            requirements.append(
                req(
                    "section-" + str(i),
                    label,
                    kind="choose_courses",
                    count=NUMBERS[word],
                    parent=root["id"],
                    course_ids=list(pool),
                    summary=label
                    + (
                        " Minimum, within the six-course concentration."
                        if "at least" in label.lower()
                        else ""
                    ),
                )
            )
        elif label.startswith("Choose remaining"):
            requirements.append(
                req(
                    "section-" + str(i),
                    "Remaining-course options",
                    kind="note",
                    parent=root["id"],
                    course_ids=list(pool),
                    summary="Use this pool for courses remaining after the required minimums.",
                )
            )
        elif label.startswith("Or choose remaining"):
            if "graduate CS and DS courses from the Core AI Bins" not in label:
                raise ValueError("Advanced graduate option changed")
            requirements.append(
                req(
                    "graduate",
                    "Graduate CS/DS alternative",
                    kind="note",
                    parent=root["id"],
                    summary="Advanced undergraduates may fill remaining courses from graduate CS/DS courses in MS-AI core bins; a separately sourced pool is provided.",
                )
            )
        elif label.startswith("Note: Only one of CS 2301 or CS 2303"):
            requirements.append(
                req(
                    "systems-exclusion",
                    "Systems programming exclusion",
                    kind="note",
                    parent=root["id"],
                    summary="Only one of CS2301 and CS2303 counts toward degree requirements.",
                )
            )
        elif label.startswith("Including from Special Topics"):
            requirements.append(
                req(
                    "special-topics",
                    "AI-relevant special topics",
                    kind="note",
                    parent=root["id"],
                    course_ids=list(pool),
                    summary="These special-topic options qualify only when the topic is relevant to the AI degree.",
                )
            )
        else:
            raise ValueError("Unknown concentration clause: " + label)
    # Local prose constraints are outside the tables.
    extra = {
        "environment": [
            (
                "CE 2000 may be used",
                "preparation",
                "CE2000 is recommended before CE2001 and may count as science, but cannot count among the six concentration courses.",
            )
        ],
        "biochemistry": [
            (
                "cannot be counted towards the 6 courses",
                "preparation",
                "CH1010/CH1020 are recommended preparation for CH1030 and may count as science, but cannot count among the six concentration courses.",
            )
        ],
        "chemical": [
            (
                "cannot be counted towards the 6 courses",
                "preparation",
                "CH1010/CH1020/CH1030 are recommended preparation; they may count as science or electives, but cannot count among the six concentration courses.",
            )
        ],
        "experience": [
            (
                "At least 2 courses must be at the 3000-level or higher",
                "advanced",
                "At least two concentration courses must be at 3000 level or above.",
            )
        ],
        "biotechnology": [
            (
                "At least one course must be at the 4000 level",
                "advanced",
                "At least one concentration course must be at 4000 level.",
            )
        ],
        "social-policy": [
            (
                "At least one course must be at the 4000 level",
                "advanced",
                "At least one concentration course must be at 4000 level.",
            )
        ],
        "robotics": [
            (
                "RBE 3100 does not count",
                "advanced-option",
                "The final course may be any RBE3000+ course, including graduate courses, except RBE3100.",
            )
        ],
        "optimization": [
            (
                "beyond those taken to meet the core AI requirements",
                "core-overlap",
                "The six concentration courses are additional to those used for AI core requirements.",
            )
        ],
        "advanced-ai": [
            (
                "beyond those taken to meet the core AI requirements",
                "core-overlap",
                "The six concentration courses are additional to those used for AI core requirements.",
            )
        ],
        "business": [
            (
                "BUS 2080 or OIE 2081",
                "analytics-alternative",
                "BUS2080 and OIE2081 appear as alternatives within the analytics-content pool, not as two required courses.",
            )
        ],
    }
    for guard, rid, summary in extra.get(key, []):
        if guard not in body:
            raise ValueError("Local concentration constraint missing: " + guard)
        requirements.append(
            req(rid, rid.replace("-", " ").title(), kind="note", parent=root["id"], summary=summary)
        )
    if key == "social-policy":
        # Special-topic rows extend the preceding minimum-three pool, subject to topic relevance.
        minimum = next(r for r in requirements if r["count"] == 3)
        special = next(r for r in requirements if r["id"].endswith("-special-topics"))
        minimum["course_ids"] += special["course_ids"]
        minimum["summary"] += " AI-relevant special topics also qualify."
    return candidate(courses.values(), requirements)


def attach(namespace):
    for key, (_, suffix) in CONCENTRATIONS.items():
        url = BASE + suffix
        namespace["SOURCES"].append(url)
        namespace["SOURCE_PARSERS"][url] = lambda html, key=key: parse(html, key)
    # Reuse the independently parsed advanced-concentration graduate core pool, rebinding provenance.
    adv = importlib.import_module("atlas.adapters.wpi-ai-advanced-methods-concentration.adapter")

    def graduate(html):
        r = adv.parse_graduate(html)
        for c in r["courses"]:
            c["source_id"] = PID + "-graduate-core"
        for rule in r["requirements"]:
            rule["id"] = PID + "-concentration-advanced-ai-graduate-pool"
            rule["source_id"] = PID + "-graduate-core"
        return candidate(r["courses"], r["requirements"])

    namespace["SOURCES"].append(adv.GRAD)
    namespace["SOURCE_PARSERS"][adv.GRAD] = graduate
