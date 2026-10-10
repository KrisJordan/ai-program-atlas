"""Observe Georgia's AI emphasis and explicit modifications to the parent BS."""

import re

from bs4 import BeautifulSoup

PROGRAM_ID = "georgia-ai-emphasis"
SOURCES = ("https://cs.uga.edu/artificial-intelligence-area-emphasis",)
SOURCE_ID = PROGRAM_ID + "-requirements"


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
    body = text(soup)
    if not any(text(h) == "Artificial Intelligence Area of Emphasis" for h in soup.find_all("h1")):
        raise ValueError("Expected Georgia AI emphasis heading")
    h = next((h for h in soup.find_all("h4") if text(h) == "Specific Requirements:"), None)
    content = h.find_next_sibling("p") if h else None
    special = next((h for h in soup.find_all("h4") if text(h) == "Special considerations:"), None)
    special = special.find_next_sibling("p") if special else None
    if content is None or special is None:
        raise ValueError("Emphasis requirement sections missing")
    intro = text(content)
    required = re.search(r"following (\w+) courses:", intro)
    selection = re.search(r"minimum of (\d+) courses from the following:", intro)
    numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    if required is None or required[1] not in numbers or selection is None:
        raise ValueError("Required/elective counts missing")
    count = numbers[required[1]]
    elective_count = int(selection[1])
    courses = []
    for a in content.find_all("a", href=True):
        m = re.fullmatch(r"(CSCI(?:\([A-Z]+\))? \d{4}(?:/\d{4})?)\s*-\s*(.+)", text(a))
        if m is None:
            raise ValueError("Unrecognized emphasis course link")
        code, name = m.groups()
        cid = "georgia-" + re.sub(r"[^a-z0-9]+", "-", code.lower())
        courses.append(
            {
                "id": cid,
                "code": code,
                "name": name,
                "description": None,
                "prerequisites": None,
                "credits": None,
                "credit_unit": "unknown",
                "category": "ai_ml",
                "source_id": SOURCE_ID,
                "url": a["href"],
                "public_site": None,
                "syllabus": None,
            }
        )
    if len(courses) <= count or len(courses) != len({c["id"] for c in courses}):
        raise ValueError("Missing or duplicate emphasis options")
    guards = [
        "CSCI 4900/6900",
        "Subject to prior approval",
        "special topic must be related to artificial intelligence",
        "will also earn a bachelor's degree in Computer Science",
        "degree will not be accredited by ABET",
        "student must still fulfill all other major requirements",
        "count toward the student's 12 hours of major electives",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Emphasis approval, degree relationship or overlap rule changed")
    waived = []
    for code, name in re.findall(
        r"(CSCI \d{4}(?:/\d{4})?) - (.*?)(?= CSCI | The student)", text(special)
    ):
        waived.append(code + ": " + name)
    if len(waived) != 3 or "NOT required" not in text(special):
        raise ValueError("Parent-degree exceptions changed")
    requirements = [
        req(
            "total",
            "AI emphasis requirements",
            "all",
            summary="Complete the listed required courses and at least the specified number of AI options.",
        ),
        req(
            "required",
            "Required AI courses",
            "all",
            [c["id"] for c in courses[:count]],
            count=count,
        ),
        req(
            "electives",
            f"At least {elective_count} AI electives",
            "choose_courses",
            [c["id"] for c in courses[count:]],
            count=elective_count,
            summary="This is a minimum selection; further qualifying electives may count toward the parent degree.",
        ),
        req(
            "topic-approval",
            "Special topics approval",
            "note",
            summary="CSCI 4900/6900 requires prior approval and an artificial-intelligence-related topic.",
        ),
        req(
            "waivers",
            "Conditional parent-degree exceptions",
            "note",
            summary="After all AI emphasis requirements are fulfilled, these parent-degree requirements are waived: "
            + "; ".join(waived)
            + ". All other major requirements remain in force.",
        ),
        req(
            "elective-overlap",
            "Parent major-elective counting",
            "note",
            summary="AI emphasis electives count toward the parent's 12-hour major-elective requirement; do not add them as a second credit total.",
        ),
        req(
            "relationship",
            "CS bachelor degree and accreditation distinction",
            "note",
            summary="This emphasis accompanies a Computer Science bachelor degree. The department states that the modified AI track does not meet ABET accreditation requirements; the regular CS degree is separately described as accredited.",
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


DEGREE_URL = "https://www.cs.uga.edu/bachelor-science-computer-science"
GRADE_ID = PROGRAM_ID + "-degree-policy"
SOURCES += (DEGREE_URL,)


def parse_degree_policy(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if not any(text(h) == "Bachelor of Science in Computer Science" for h in soup.find_all("h1")):
        raise ValueError("Georgia CS degree heading missing")
    grade = re.search(
        r"All major-related coursework and associated prerequisites must be fulfilled with grades of ([A-Z][+-]?) \((\d+\.\d+)\) or higher",
        body,
    )
    if grade is None:
        raise ValueError("Georgia grade policy missing")
    row = req(
        "grade-policy",
        "Grade minimum for major-related coursework",
        "note",
        summary=f"Major-related coursework and associated prerequisites require {grade[1]} ({grade[2]}) or higher. This includes the AI emphasis within the CS degree.",
    )
    row["parent_id"] = None
    row["source_id"] = GRADE_ID
    return {"id": PROGRAM_ID, "requirements": [row]}


SOURCE_PARSERS = {DEGREE_URL: parse_degree_policy}
