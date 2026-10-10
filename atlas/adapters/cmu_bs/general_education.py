"""SCS catalog distributions, finite option pools, and exclusion lists."""

import re
from bs4 import BeautifulSoup
from .common import course, requirement, text

URL = (
    "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/general-education/"
)
PID = "cmu-bs-ai"
SOURCE = PID + "-general-education"


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find(id="textcontainer") or soup
    if not any(text(h) == "SCS General Education" for h in soup.find_all("h1")):
        raise ValueError("CMU general-education heading missing")
    tables = main.find_all("table", class_="sc_courselist")
    if len(tables) != 10:
        raise ValueError("CMU general-education table inventory changed")
    for i, label in [
        (4, "Category 1 ("),
        (5, "Category 1A ("),
        (6, "Category 2 ("),
        (7, "Category 3 ("),
    ]:
        if not text(tables[i]).startswith(label):
            raise ValueError("CMU breadth pool identity changed")
    words = text(main)
    for phrase in [
        "minimum of 36 units",
        "at least four undergraduate courses",
        "9 units or more for each course",
        "at least one course must have a laboratory component",
        "at least two courses must be from the same department",
        "minimum of 63 units",
        "Complete three courses, one each",
        "Complete 3 non-technical undergraduate courses",
        "advisor approval",
        "SCS General Education Committee",
    ]:
        if phrase not in words:
            raise ValueError("CMU general-education distribution changed: " + phrase)
    courses = {}
    reqs = []

    def add(key, title, **kwargs):
        r = requirement(PID, "gened-" + key, title, SOURCE, **kwargs)
        reqs.append(r)
        return r

    def rows(table, category="human_context", register=True):
        ids = []
        for row in table.find_all("tr"):
            cell = row.find("td", class_="codecol")
            if cell is None:
                continue
            code = text(cell)
            if not re.fullmatch(r"\d{2}-\d{3}", code):
                raise ValueError("CMU general-education course code changed")
            cells = row.find_all("td", recursive=False)
            name = cells[1].get_text("\n", strip=True).splitlines()[0]
            value = text(cells[-1])
            credits = float(value) if re.fullmatch(r"\d+(?:\.\d+)?", value) else None
            c = course(code, name, SOURCE, URL, category, credits)
            ids.append(c["id"])
            if register:
                courses.setdefault(c["id"], c)
        return ids

    science = add(
        "science",
        "Science/engineering distribution",
        category="mathematics",
        kind="choose_courses",
        count=4,
        credits=36,
        summary="At least four undergraduate science/engineering courses totaling at least 36 units, each normally nine or more units. Include a lab and at least two courses in one department. This is the distribution underlying the degree-page 36-unit total, not an additional 36 units.",
    )
    add(
        "science-scope",
        "Eligible science/engineering departments and approvals",
        category="mathematics",
        kind="note",
        parent=science["id"],
        summary="Eligible departments: biology 03, biomedical engineering 42, chemical engineering 06, chemistry 09, civil/environmental engineering 12, electrical/computer engineering 18, materials 27, mechanical engineering 24 and physics 33, subject to exclusions and listed additions. New courses require adviser and SCS General Education Committee review.",
    )
    add(
        "lab",
        "Laboratory requirement",
        category="mathematics",
        kind="choose_courses",
        count=1,
        parent=science["id"],
        course_ids=rows(tables[0], "mathematics"),
        summary="Include one approved laboratory option within the science distribution. 02-261/02-262 may pair with biology for the same-department rule; 03-118 needs another 3+ unit course; the three-unit 09-101 lab must combine with 09-105.",
    )
    excluded = rows(tables[1], register=False)
    add(
        "science-exclusions",
        "Science exclusions",
        category="mathematics",
        kind="note",
        parent=science["id"],
        summary="SCS-crosslisted MCS/CIT courses and IDeATe courses are excluded; Engineering & Public Policy requires an explicit addition. Excluded codes: "
        + ", ".join(c.removeprefix("cmu-") for c in excluded)
        + ".",
    )
    add(
        "science-additions",
        "Additional approved science options",
        category="mathematics",
        kind="note",
        parent=science["id"],
        course_ids=rows(tables[2], "mathematics"),
        summary="These courses supplement eligible departmental offerings; they are options, not additional required courses.",
    )
    humanities = add(
        "humanities",
        "Humanities/arts distribution",
        category="human_context",
        credits=63,
        summary="At least 63 units across writing, breadth and unrestricted approved humanities/arts electives. This implements the degree-page humanities total and is not additive to it.",
    )
    writing = add(
        "writing",
        "First-year writing alternatives",
        category="human_context",
        kind="alternative",
        count=1,
        credits=9,
        parent=humanities["id"],
    )
    ids = rows(tables[3])
    mini = [i for i in ids if i in ["cmu-76-106", "cmu-76-107", "cmu-76-108"]]
    full = [i for i in ids if i not in mini]
    if len(mini) != 3 or len(full) != 2:
        raise ValueError("CMU writing alternatives changed")
    add(
        "writing-full",
        "Full-course writing option",
        category="human_context",
        kind="choose_courses",
        count=1,
        parent=writing["id"],
        course_ids=full,
        summary="Choose one full writing course; 76-102 is invitation-only.",
    )
    add(
        "writing-minis",
        "Writing mini-course option",
        category="human_context",
        kind="choose_courses",
        count=2,
        credits=9,
        parent=writing["id"],
        course_ids=mini,
        summary="Choose two of the three 4.5-unit writing mini-courses.",
    )
    breadth = add(
        "breadth",
        "Humanities breadth",
        category="human_context",
        credits=27,
        parent=humanities["id"],
        summary="Three courses, one in each of categories 1A, 2 and 3, at least nine units per category. AI uses category 1A instead of category 1.",
    )
    for i, key, title in [
        (5, "1a", "Cognitive studies (AI Category 1A)"),
        (6, "2", "Economic, political and social institutions"),
        (7, "3", "Cultural analysis"),
    ]:
        add(
            "category-" + key,
            title,
            category="human_context",
            kind="choose_courses",
            count=1,
            credits=9,
            parent=breadth["id"],
            course_ids=rows(tables[i]),
        )
    electives = add(
        "humanities-electives",
        "Humanities/arts electives",
        category="human_context",
        kind="choose_courses",
        count=3,
        credits=27,
        parent=humanities["id"],
        summary="Three nontechnical undergraduate Dietrich/CFA courses, normally at least nine units each, plus specifically approved external additions. Two mini-courses totaling at least nine units may combine with adviser approval in consultation with the SCS associate dean. Departmental breadth is encouraged, not required.",
    )
    add(
        "humanities-exclusions",
        "Humanities/arts exclusions",
        category="human_context",
        kind="note",
        parent=electives["id"],
        summary="Courses with computer-science or mathematics prerequisites generally do not qualify. Explicit excluded codes: "
        + ", ".join(c.removeprefix("cmu-") for c in rows(tables[8], register=False))
        + ".",
    )
    add(
        "humanities-additions",
        "Additional approved humanities/arts options",
        category="human_context",
        kind="note",
        parent=electives["id"],
        course_ids=rows(tables[9]),
        summary="Additional eligible options, not mandatory courses. 70-352 requires combination with a 6+ unit humanities/arts course. New DC/CFA/TSB courses require adviser and SCS General Education Committee approval.",
    )
    return {
        "id": PID,
        "curriculum_status": "partial",
        "catalog_year": (
            re.search(r"(20\d{2}[-–]20\d{2})\s+Catalog", text(soup))[1]
            if re.search(r"(20\d{2}[-–]20\d{2})\s+Catalog", text(soup))
            else None
        ),
        "courses": list(courses.values()),
        "requirements": reqs,
        "notes": [
            "Catalog finite lists are dated July 2026; linked current lists are separate sources. No completeness certification is emitted. Category 1 pools for other majors and explicitly excluded courses are not presented as positive AI course options."
        ],
    }
