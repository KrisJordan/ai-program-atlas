"""Extract Ohio State's AI specialization tables and selection policies."""

import re

from bs4 import BeautifulSoup

PROGRAM_ID = "ohio-state-ai-specialization"
SOURCES = ("https://cse.osu.edu/bscse-and-bscis-specializations",)
SOURCE_ID = PROGRAM_ID + "-official"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def req(suffix, title, kind, ids=(), count=None, summary=""):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": None if suffix == "total" else PROGRAM_ID + "-total",
        "title": title,
        "kind": kind,
        "count": count,
        "credits": None,
        "credit_unit": "unknown",
        "category": "ai_ml",
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
        "course_ids": list(ids),
    }


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.find("h1")
    if heading is None or text(heading) != "BSCSE and BSCIS Specializations":
        raise ValueError("Expected Ohio State specialization heading")
    body = text(soup)
    guards = [
        "All CSE and BSCIS majors are required to take a specialization",
        "only available to undergraduates by petition",
        "time of application to the major",
        "To change specializations, please contact your academic advisor",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Specialization relationship or petition rules changed")
    area = next(
        (
            d
            for d in soup.find_all("details")
            if d.find("summary") and text(d.find("summary")) == "Artificial Intelligence"
        ),
        None,
    )
    if area is None:
        raise ValueError("AI accordion missing")
    tables = area.find_all("table")
    captions = [text(t.find("caption")) if t.find("caption") else "" for t in tables]
    if captions != ["Required Courses", "Pick Two of the Following Courses"]:
        raise ValueError("AI selection rule changed")
    courses = []
    groups = []
    for table in tables:
        ids = []
        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if not cells:
                continue
            if len(cells) != 4:
                raise ValueError("AI course table columns changed")
            code, name, amount, prerequisites = [text(c) for c in cells]
            if not re.fullmatch(r"CSE \d{4}", code) or not amount.isdigit():
                raise ValueError("Unknown AI course/credit format")
            code = code.rstrip("*")
            cid = "ohio-state-" + code.lower().replace(" ", "-")
            ids.append(cid)
            courses.append(
                {
                    "id": cid,
                    "code": code,
                    "name": name,
                    "description": None,
                    "prerequisites": prerequisites or None,
                    "credits": int(amount),
                    "credit_unit": "unknown",
                    "category": "ai_ml",
                    "source_id": SOURCE_ID,
                    "url": SOURCES[0],
                    "public_site": None,
                    "syllabus": None,
                }
            )
        if not ids:
            raise ValueError("Empty AI requirement table")
        groups.append(ids)
    if len(courses) != len({c["id"] for c in courses}):
        raise ValueError("Duplicate AI course")
    requirements = [
        req(
            "total",
            "AI specialization",
            "all",
            summary="Complete the required course and two listed options. Credits vary if the four-credit capstone is selected.",
        ),
        req("required", "Required AI course", "all", groups[0]),
        req("choice", "Choose two AI options", "choose_courses", groups[1], count=2),
        req(
            "relationship",
            "Parent degree and specialization selection",
            "note",
            summary="A specialization is required within BSCSE or BSCIS; students typically select it when applying to the major and contact an advisor to change it.",
        ),
        req(
            "prerequisites",
            "Course enrollment conditions",
            "note",
            summary="Meet the prerequisites and enrollment restrictions attached to each listed course. An asterisk on a listed course denotes undergraduate petition eligibility; none of the inspected AI rows is starred.",
        ),
    ]
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence",
        "award_level": "concentration",
        "program_kind": "concentration",
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
    }


CSE_URL = "https://cse.osu.edu/prospective-students/undergrad/majors/bs-cse-program-information"
CIS_URL = "https://cse.osu.edu/prospective-students/undergrad/majors/bs-cis-program-information"
SOURCES += (CSE_URL, CIS_URL)


def parse_parent(html: str, kind: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    match = re.search(
        r"Overall, each student must have (\d+) credit hours of technical elective coursework, of which (\d+) hours must be in CSE",
        body,
    )
    if match is None or f"All BS {kind} students must choose a specialization option" not in body:
        raise ValueError("Parent technical-elective relationship changed")
    row = req(
        "parent-" + kind.lower(),
        "Relationship to BS " + kind + " technical electives",
        "note",
        summary=f"The specialization supplies part of the BS {kind} technical electives. The parent degree requires {match[1]} technical-elective hours, including {match[2]} CSE hours; these are parent totals, not additional AI-specialization credits.",
    )
    row["source_id"] = PROGRAM_ID + "-" + kind.lower() + "-parent"
    row["parent_id"] = None
    rows = [row]
    if kind == "CIS":
        if (
            "Linear Algebra is still required for the AI specialization as it is a prerequisite for CSE 3521"
            not in body
        ):
            raise ValueError("BS CIS AI linear-algebra rule changed")
        extra = req(
            "cis-linear-algebra",
            "BS CIS AI preparation exception",
            "note",
            summary="Linear algebra remains required for the AI specialization through CSE 3521 prerequisites even though the general BS CIS core replaces MATH 2568. Use the listed CSE 3521 alternatives; no waiver is inferred.",
        )
        extra["source_id"] = row["source_id"]
        extra["parent_id"] = None
        rows.append(extra)
    return {"id": PROGRAM_ID, "requirements": rows}


def parse_cse(html: str) -> dict:
    return parse_parent(html, "CSE")


def parse_cis(html: str) -> dict:
    return parse_parent(html, "CIS")


SOURCE_PARSERS = {CSE_URL: parse_cse, CIS_URL: parse_cis}
