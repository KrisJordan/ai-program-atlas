"""Penn State bulletin curriculum table parser, including OR-row semantics."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "penn-state-ai-engineering-minor"

SOURCES = (
    "https://bulletins.psu.edu/undergraduate/colleges/engineering/artificial-intelligence-engineering-minor/",
    "https://bulletins.psu.edu/university-course-descriptions/undergraduate/a-i/",
    "https://bulletins.psu.edu/university-course-descriptions/undergraduate/cmpsc/",
    "https://bulletins.psu.edu/university-course-descriptions/undergraduate/ee/",
)
PREFIX = "penn-state-ai-engineering-minor"
SOURCE_ID = PREFIX + "-catalog"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def req(suffix, title, kind, ids=(), count=None, credits=None, summary=""):
    return {
        "id": PREFIX + "-" + suffix,
        "parent_id": None if suffix == "total" else PREFIX + "-total",
        "title": title,
        "kind": kind,
        "count": count,
        "credits": credits,
        "credit_unit": "semester_hours",
        "category": "ai_ml" if suffix in {"prescribed", "ml-choice"} else "other",
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
        "course_ids": list(ids),
    }


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1 or text(h1) != "Artificial Intelligence Engineering, Minor":
        raise ValueError("Expected Penn State AI Engineering minor heading")
    year = re.search(r"(\d{4}-\d{4}) edition of the Undergraduate Bulletin", text(soup))
    total_table = soup.find("table", class_="tbl_programrequirements")
    table = soup.find("table", class_="sc_courselist")
    if total_table is None or table is None:
        raise ValueError("Minor requirement tables missing")
    total = next(
        (
            text(r.find_all("td")[-1])
            for r in total_table.find_all("tr")
            if "Requirements for the Minor" in text(r)
        ),
        None,
    )
    if total is None or not total.isdigit():
        raise ValueError("Minor credit total missing")
    page_text = text(soup)
    required_fragments = [
        "C or better",
        "at least six credits",
        "must be unique",
        "CMPSC 121",
        "DS 120",
        "CMPSC 131",
        "CMPSC 122",
        "CMPSC 132",
        "at least 3 at the 400-level",
    ]
    if any(fragment not in page_text for fragment in required_fragments):
        raise ValueError("Minor entrance, overlap or supporting rules changed; review required")
    courses, prescribed, ml = [], [], []
    section, supporting = None, None
    for row in table.find_all("tr"):
        if "areaheader" in row.get("class", []):
            section = text(row)
            continue
        if "areasubheader" in row.get("class", []):
            continue
        cells = row.find_all("td", recursive=False)
        link = row.find("a", class_="code")
        if link:
            code = text(link)
            if not re.fullmatch(r"[A-Z-]+ \d+[A-Z]?", code):
                raise ValueError("Unrecognized course code")
            hours = row.find("td", class_="hourscol")
            credits = (
                float(text(hours))
                if hours and re.fullmatch(r"\d+(?:\.\d+)?", text(hours))
                else None
            )
            cid = "penn-state-" + re.sub(r"[^a-z0-9]+", "-", code.lower())
            courses.append(
                {
                    "id": cid,
                    "code": code,
                    "name": text(cells[1]),
                    "description": None,
                    "prerequisites": None,
                    "credits": credits,
                    "credit_unit": "semester_hours",
                    "category": "systems" if code == "A-I 410" else "ai_ml",
                    "source_id": SOURCE_ID,
                    "url": urljoin(SOURCES[0], link["href"]),
                    "public_site": None,
                    "syllabus": None,
                }
            )
            if section == "Prescribed Courses":
                prescribed.append(cid)
            elif section == "Additional Courses":
                if ml and "orclass" not in row.get("class", []):
                    raise ValueError("Additional Courses changed; review conjunction semantics")
                ml.append(cid)
            else:
                raise ValueError("Course found in unhandled minor requirement section")
        elif section == "Supporting Courses and Related Areas" and "Department List" in text(row):
            hours = row.find("td", class_="hourscol")
            supporting = int(text(hours)) if hours and text(hours).isdigit() else None
    if not prescribed or len(ml) < 2 or supporting is None:
        raise ValueError("Incomplete minor requirement structure")
    requirements = [
        req(
            "total",
            "Minor requirements",
            "all",
            credits=int(total),
            summary="Complete the prescribed, alternative and supporting requirements.",
        ),
        req("prescribed", "Prescribed courses", "all", prescribed),
        req(
            "ml-choice",
            "Machine learning alternative",
            "alternative",
            ml,
            count=1,
            credits=next(c["credits"] for c in courses if c["id"] == ml[0]),
            summary="Complete one machine-learning alternative.",
        ),
        req(
            "supporting",
            "Department-list electives",
            "choose_credits",
            credits=supporting,
            summary="Department-list courses not required by the major; at least three credits at 400-level. List not extracted.",
        ),
        req(
            "grade-overlap",
            "Grade and overlap rules",
            "note",
            summary="C or better in all minor courses; six minor credits must be unique from prescribed major courses.",
        ),
        req(
            "entrance",
            "Entrance requirements",
            "note",
            summary="Complete ((CMPSC 121 and DS 120) or CMPSC 131), plus either CMPSC 122 or CMPSC 132. Entrance credits are not added to the 18-credit minor total.",
        ),
    ]
    return {
        "id": PREFIX,
        "title": text(h1),
        "award_level": "minor",
        "program_kind": "minor",
        "catalog_year": year.group(1) if year else None,
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
        "notes": [
            "Department-list elective options are not enumerated on the inspected bulletin page; course prerequisites may add preparation outside the minor total."
        ],
    }


def parse_subject(html: str, subject: str, codes: set[str], url: str) -> dict:
    """Observe metadata from permitted subject catalogs, without copying descriptions."""
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1 or text(h1) != subject:
        raise ValueError("Expected subject catalog heading")
    courses = []
    for block in soup.find_all("div", class_="courseblock"):
        code_node = block.find(class_="course_code")
        if code_node is None or text(code_node) not in codes:
            continue
        code = text(code_node)
        title = block.find(class_="course_codetitle")
        credit = block.find(class_="course_credits")
        if title is None or credit is None:
            raise ValueError("Course title or credits missing")
        amount = re.fullmatch(r"(\d+(?:\.\d+)?) Credits?", text(credit))
        if amount is None:
            raise ValueError("Unrecognized course credit format")
        prerequisites = []
        for extra in block.find_all(class_="courseblockextra"):
            value = text(extra)
            if value.startswith("Enforced Prerequisite at Enrollment:"):
                prerequisites.append(value.split(":", 1)[1].strip())
        source_id = "penn-state-" + url.rstrip("/").rsplit("/", 1)[-1] + "-subject"
        courses.append(
            {
                "id": "penn-state-" + re.sub(r"[^a-z0-9]+", "-", code.lower()),
                "code": code,
                "name": re.sub(r"^" + re.escape(code) + r":\s*", "", text(title)),
                "credits": float(amount.group(1)),
                "credit_unit": "semester_hours",
                "prerequisites": "; ".join(prerequisites) or None,
                "description": None,
                "category": "systems" if code == "A-I 410" else "ai_ml",
                "source_id": source_id,
                "url": url + "#cb-" + code.replace(" ", ""),
                "public_site": None,
                "syllabus": None,
            }
        )
    if {c["code"] for c in courses} != codes or len(courses) != len(codes):
        raise ValueError("Expected minor course blocks missing or duplicated")
    return {"id": PROGRAM_ID, "courses": courses}


def parse_ai(html: str) -> dict:
    return parse_subject(html, "Artificial Intelligence (A-I)", {"A-I 305", "A-I 410"}, SOURCES[1])


def parse_cmpsc(html: str) -> dict:
    return parse_subject(html, "Computer Science (CMPSC)", {"CMPSC 445", "CMPSC 448"}, SOURCES[2])


def parse_ee(html: str) -> dict:
    return parse_subject(html, "Electrical Engineering (EE)", {"EE 456"}, SOURCES[3])


SOURCE_PARSERS = {SOURCES[1]: parse_ai, SOURCES[2]: parse_cmpsc, SOURCES[3]: parse_ee}


from atlas.adapters.penn_state_minor_followup import DIRECTORY, FAQ, parse_directory, parse_faq

SOURCES += (DIRECTORY, FAQ)
SOURCE_PARSERS.update({DIRECTORY: parse_directory, FAQ: parse_faq})
