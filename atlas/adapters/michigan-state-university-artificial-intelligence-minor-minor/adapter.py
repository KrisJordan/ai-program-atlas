"""Extract the official MSU AI minor table and local admission/overlap policies."""

import re

from bs4 import BeautifulSoup

PROGRAM_ID = "michigan-state-university-artificial-intelligence-minor-minor"
SOURCES = ("https://reg.msu.edu/ACADEMICPROGRAMS/ProgramDetail.aspx?PType=MNUN&Program=AINTL_MNUN",)
SOURCE_ID = PROGRAM_ID + "-official"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def req(suffix, title, kind, ids=(), credits=None, count=None, summary=""):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": None if suffix == "total" else PROGRAM_ID + "-total",
        "title": title,
        "kind": kind,
        "course_ids": list(ids),
        "credits": credits,
        "count": count,
        "credit_unit": "unknown",
        "category": "other",
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
    }


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find(id="MainContent_lblProg")
    content = soup.find(id="MainContent_divDesc")
    if heading is None or text(heading) != "Minor in Artificial Intelligence" or content is None:
        raise ValueError("Expected MSU AI minor catalog identity")
    body = text(content)
    total = re.search(r"Complete a minimum of (\d+) credits", body)
    grade = re.search(
        r"completion of Computer Science and Engineering (\d+) and (\d+) with a minimum grade in each of those two courses of (\d+\.\d+)",
        body,
    )
    if total is None or grade is None:
        raise ValueError("Minor total or entrance grade rule missing")
    guards = [
        "other than the Bachelor of Science Degree in Computer Science",
        "Bachelor of Science Degree in Computer Engineering",
        "Bachelor of Science Degree in Computational Data Science",
        "Bachelor of Science Degree in Data Science",
        "not available to students with a Minor in Computer Science",
        "With the approval of the department and college",
        "may also be used to satisfy",
        "must apply to the Department of Computer Science and Engineering",
        "Enrollment may be limited",
        "Calculus I is an implied component",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Minor eligibility, overlap or preparation rules changed")
    table = content.find("table")
    if table is None:
        raise ValueError("Minor course table missing")
    courses, groups = [], []
    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        value = text(row)
        group = re.search(r"(All|One) of the following courses \((\d+) credits\)", value)
        if group:
            groups.append(
                {
                    "kind": "all" if group[1] == "All" else "choose_courses",
                    "credits": int(group[2]),
                    "ids": [],
                }
            )
            continue
        if len(cells) != 5 or not re.fullmatch(r"[A-Z]+", text(cells[1])):
            continue
        if not groups:
            raise ValueError("Course outside requirement group")
        subject, number, name, credit = [text(c) for c in cells[1:]]
        if not number.isdigit() or not credit.isdigit():
            raise ValueError("Unrecognized course number or credit")
        code = subject + " " + number
        cid = "msu-" + subject.lower() + "-" + number
        groups[-1]["ids"].append(cid)
        courses.append(
            {
                "id": cid,
                "code": code,
                "name": name,
                "description": None,
                "prerequisites": None,
                "credits": int(credit),
                "credit_unit": "unknown",
                "category": "human_context"
                if code == "CSE 300"
                else "mathematics"
                if subject == "MTH"
                else "ai_ml"
                if int(number) >= 345
                else "foundations",
                "source_id": SOURCE_ID,
                "url": SOURCES[0],
                "public_site": None,
                "syllabus": None,
            }
        )
    if [g["kind"] for g in groups] != ["all", "choose_courses"] or any(
        not g["ids"] for g in groups
    ):
        raise ValueError("Expected required and choose-one course groups")
    if len(courses) != len({c["id"] for c in courses}):
        raise ValueError("Duplicate course row")
    requirements = [req("total", "Minimum minor credits", "all", credits=int(total[1]))]
    for suffix, title, group in zip(
        ["required", "choice"], ["Required courses", "AI elective"], groups
    ):
        requirements.append(
            req(
                suffix,
                title,
                group["kind"],
                group["ids"],
                credits=group["credits"],
                count=1 if group["kind"] == "choose_courses" else None,
            )
        )
    requirements += [
        req(
            "admission",
            "Application and entrance grades",
            "note",
            summary=f"Apply to Computer Science and Engineering. CSE {grade[1]} and CSE {grade[2]} each require at least {grade[3]} for acceptance; enrollment may be limited.",
        ),
        req(
            "eligibility",
            "Eligible bachelor students and exclusions",
            "note",
            summary="Available to MSU bachelor students except CS, Computer Engineering, Computational Data Science and Data Science BS students; unavailable with the CS minor.",
        ),
        req(
            "overlap",
            "Bachelor-degree overlap approval",
            "note",
            summary="Minor courses may also satisfy the bachelor's degree with approval from the administering department and college.",
        ),
        req(
            "calculus",
            "Implied Calculus I preparation",
            "note",
            summary="Calculus I is an implied component because it is a prerequisite for a required minor course. No course code or added credits are specified here.",
        ),
    ]
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence",
        "award_level": "minor",
        "program_kind": "minor",
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
    }


POLICY_URL = "https://reg.msu.edu/AcademicPrograms/Text.aspx?Section=110"
POLICY_ID = PROGRAM_ID + "-undergraduate-policy"
SOURCES += (POLICY_URL,)


def parse_policy(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    section = soup.find(id="s261")
    if section is None or "Selecting a Minor" not in text(section):
        raise ValueError("MSU minor policy section missing")
    value = text(section)
    minimum = re.search(r"minimum number of credits for a minor is (\d+)", value)
    if minimum is None or any(
        fragment not in value
        for fragment in [
            "awarded in conjunction with the primary undergraduate degree",
            "same name represented by the minor",
            "do not count for a course taken to satisfy another university, college, or major requirement",
        ]
    ):
        raise ValueError("MSU general minor rules changed")
    row = req(
        "university-policy",
        "University minor relationship and credit policy",
        "note",
        summary=f"A minor accompanies the primary undergraduate degree and is unavailable with a same-named major. University minimum is {minimum[1]} credits; this program's published minimum governs. Any required unique credits must be explicitly identified in the catalog and cannot also satisfy university, college or major requirements.",
    )
    row["source_id"] = POLICY_ID
    row["parent_id"] = None
    return {"id": PROGRAM_ID, "requirements": [row]}


SOURCE_PARSERS = {POLICY_URL: parse_policy}


# Bounded metadata review: observations do not certify a curriculum audit.
from functools import partial as _metadata_partial
from atlas.adapters.small_complete_metadata_batch2 import CONFIG as _metadata_config, parse_metadata as _parse_metadata

SOURCE_PARSERS = globals().get("SOURCE_PARSERS", {})
for _key in ['msu-231', 'msu-232', 'msu-260', 'msu-300', 'msu-331', 'msu-402', 'msu-404', 'msu-440']:
    _cfg = _metadata_config[_key]
    if _cfg["url"] not in SOURCES:
        SOURCES = list(SOURCES) + [_cfg["url"]]
    SOURCE_PARSERS[_cfg["url"]] = _metadata_partial(_parse_metadata, key=_key)
