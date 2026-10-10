"""Purdue BA admissions identity parser; does not claim catalog coverage."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "purdue-ai-ba"

SOURCES = (
    "https://admissions.purdue.edu/majors/artificial-intelligence/",
    "https://www.cla.purdue.edu/academic/philosophy/students/undergraduate/majors/artificial-intelligence/index.html",
    "https://www.cs.purdue.edu/academic-programs/courses/canonical/cs10100.html",
    "https://www.cs.purdue.edu/academic-programs/courses/canonical/cs180.html",
    "https://www.cs.purdue.edu/academic-programs/courses/canonical/cs182.html",
)
DEPARTMENT_SOURCE_ID = "purdue-ai-ba-department"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if (
        h1 is None
        or " ".join(h1.get_text(" ", strip=True).split())
        != "Artificial Intelligence (Liberal Arts)"
    ):
        raise ValueError("Expected Purdue Liberal Arts AI admissions heading")
    quick = soup.find(re.compile("^h[2-4]$"), string=re.compile(r"^Quick Facts$"))
    if quick is None:
        raise ValueError("Quick Facts missing")
    facts = " ".join(quick.find_next("ul").get_text(" ", strip=True).split())
    if "Degree: Bachelor of Arts" not in facts or "West Lafayette" not in facts:
        raise ValueError("BA award/campus not confirmed by Quick Facts")
    plan = soup.find("a", string=re.compile("Explore Plan of Study"))
    if plan is None:
        raise ValueError("Catalog plan link missing")
    return {
        "id": "purdue-ai-ba",
        "title": "Artificial Intelligence (Liberal Arts)",
        "award_level": "BA",
        "program_kind": "degree",
        "hosting_unit": "College of Liberal Arts",
        "catalog_year": None,
        "curriculum_status": "pending",
        "courses": [],
        "requirements": [],
        "links": [
            {"kind": "overview", "url": SOURCES[0], "label": "Official BA admissions overview"},
            {
                "kind": "catalog",
                "url": urljoin(SOURCES[0], plan["href"]),
                "label": "Official plan of study (access blocked during pilot)",
            },
        ],
        "notes": [
            "Identity and BA award verified from admissions Quick Facts; course-level requirements await catalog access."
        ],
    }


def parse_department(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    normalize = lambda node: " ".join(node.get_text(" ", strip=True).split())
    h1 = soup.find("h1")
    if not h1 or normalize(h1) != "Artificial Intelligence":
        raise ValueError("Expected Purdue department AI heading")
    heading = next((h for h in soup.find_all("h2") if normalize(h) == "Plan of Study"), None)
    if heading is None:
        raise ValueError("BA plan section missing")
    paragraph = heading.find_next_sibling("p")
    match = (
        re.search(
            r"BA in AI degree requires (\d+) credit hours in philosophy, with an additional (\d+) credit hours in CS",
            normalize(paragraph),
        )
        if paragraph
        else None
    )
    if not match:
        raise ValueError("BA subject totals missing")
    listing = paragraph.find_next_sibling("ul")
    if listing is None:
        raise ValueError("BA required CS course list missing")
    courses = []
    for li in listing.find_all("li", recursive=False):
        item = re.fullmatch(r"(CS \d{5}):\s*(.+)", normalize(li))
        if item is None:
            raise ValueError("Unrecognized BA CS course")
        code, title = item.groups()
        courses.append(
            {
                "id": "purdue-" + code.lower().replace(" ", "-"),
                "code": code,
                "name": title,
                "description": None,
                "prerequisites": None,
                "credits": None,
                "credit_unit": "semester_hours",
                "category": "ai_ml" if code == "CS 24300" else "foundations",
                "source_id": DEPARTMENT_SOURCE_ID,
                "url": SOURCES[1],
                "public_site": None,
                "syllabus": None,
            }
        )
    if not courses:
        raise ValueError("BA course list empty")
    philosophy_count = re.search(r"includes (\d+) specialized philosophy courses", normalize(soup))
    requirements = []
    for subject, credits, category in [
        ("philosophy", int(match[1]), "human_context"),
        ("cs", int(match[2]), "foundations"),
    ]:
        requirements.append(
            {
                "id": PROGRAM_ID + "-" + subject,
                "parent_id": None,
                "title": "Philosophy coursework"
                if subject == "philosophy"
                else "Required computer science courses",
                "kind": ("choose_courses" if philosophy_count else "choose_credits")
                if subject == "philosophy"
                else "all",
                "count": int(philosophy_count[1])
                if subject == "philosophy" and philosophy_count
                else None,
                "credits": credits,
                "credit_unit": "semester_hours",
                "category": category,
                "source_id": DEPARTMENT_SOURCE_ID,
                "source_text": None,
                "summary": "Philosophy options await full plan inspection."
                if subject == "philosophy"
                else "Complete the department's listed CS courses; individual credits are not stated here.",
                "course_ids": [] if subject == "philosophy" else [c["id"] for c in courses],
            }
        )
    return {
        "id": PROGRAM_ID,
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
    }


SOURCE_PARSERS = {SOURCES[1]: parse_department}

AI_REQUIREMENT_URL = "https://www.purdue.edu/newsroom/2026/Q3/purdues-ai-competency-graduation-requirement-begins-in-every-undergraduate-degree-program/"


def parse_university_ai(html):
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    value = " ".join(soup.get_text(" ", strip=True).split())
    if h1 is None or "AI competency graduation requirement begins" not in h1.get_text(
        " ", strip=True
    ):
        raise ValueError("University AI requirement heading missing")
    date = re.search(r"August 19, (\d{4})", value)
    span = re.search(r"Courses range from (one|two|three) to (four|five) credit hours each", value)
    if not date or not span or "Beginning with this fall’s incoming class" not in value:
        raise ValueError("University AI requirement cohort/credit evidence missing")
    row = {
        "id": PROGRAM_ID + "-university-ai-competency",
        "parent_id": None,
        "title": "University AI working competency",
        "kind": "note",
        "count": None,
        "credits": None,
        "credit_unit": "semester_hours",
        "category": "ai_ml",
        "source_id": "purdue-university-ai-competency",
        "source_text": None,
        "summary": f"Required AI-focused coursework applies to the incoming Fall {date[1]} cohort. Approved courses span {span[1]} to {span[2]} credit hours; the specific course fulfilling this major's competency is not verified. Do not add this range to major credits.",
        "course_ids": [],
    }
    return {"id": PROGRAM_ID, "requirements": [row], "curriculum_status": "partial"}


SOURCES += (AI_REQUIREMENT_URL,)
SOURCE_PARSERS[AI_REQUIREMENT_URL] = parse_university_ai
