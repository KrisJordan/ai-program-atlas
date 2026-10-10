"""Observed Purdue college pools and overlap rules; never a completeness audit."""

import hashlib
import re

from bs4 import BeautifulSoup

BASE = "https://www.purdue.edu/science/Current_Students/"
CULTURE_URL = BASE + "all_current_approved_courses.php"
GENED_URL = BASE + "general_education_elective_list.php"
EXPERIENCE_URL = (
    BASE + "curriculum_and_degree_requirements/language-and-culture-experiential-requirement.html"
)
OVERLAP_URL = BASE + "curriculum_and_degree_requirements/not-recommended-course-list.html"
PREFIX = "purdue-ai-bs"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def note(suffix, title, source, summary, parent=None, ids=()):
    return {
        "id": PREFIX + "-" + suffix,
        "parent_id": parent,
        "title": title,
        "kind": "note",
        "count": None,
        "credits": None,
        "credit_unit": "semester_hours",
        "category": "human_context",
        "source_id": source,
        "source_text": None,
        "summary": summary,
        "course_ids": list(ids),
    }


def parse_pool(html, *, culture):
    soup = BeautifulSoup(html, "html.parser")
    expected = (
        "Comprehensive Culture Course List"
        if culture
        else "Comprehensive General Education Elective List"
    )
    if not any(text(h) == expected for h in soup.find_all("h1")):
        raise ValueError("Expected comprehensive Purdue pool heading")
    table = soup.find("table", id="example")
    if table is None:
        raise ValueError("Comprehensive course table missing")
    headers = [text(h) for h in table.find("tr").find_all("th")]
    if headers[:3] != ["Subject", "Number", "Keyword/Title"] or headers[-1:] != ["Level"]:
        raise ValueError("Purdue pool column structure changed")
    source = "purdue-science-culture-pool" if culture else "purdue-science-general-education-pool"
    url = CULTURE_URL if culture else GENED_URL
    courses = {}
    for tr in table.find_all("tr"):
        cells = tr.find_all("td", recursive=False)
        if not cells or not any(text(c) for c in cells):
            continue
        if len(cells) != 6:
            raise ValueError("Unexpected Purdue pool row")
        subject = text(cells[0]).split(" - ")[0]
        number, name = text(cells[1]), text(cells[2])
        if not re.fullmatch(r"[A-Z]+", subject) or not re.fullmatch(r"\d{5}", number) or not name:
            raise ValueError("Invalid Purdue course identity")
        code = subject + " " + number
        # Repeatable numbers have distinct approved titles. Exact identities share IDs across pools.
        identifier = (
            "purdue-" + slug(code) + "-pool-" + hashlib.sha256(name.encode()).hexdigest()[:12]
        )
        courses[identifier] = {
            "id": identifier,
            "code": code,
            "name": name,
            "description": None,
            "prerequisites": None,
            "credits": None,
            "credit_unit": "semester_hours",
            "category": "human_context",
            "source_id": source,
            "url": url,
            "public_site": None,
            "syllabus": None,
        }
    if not courses:
        raise ValueError("Empty comprehensive Purdue pool")
    kind = "culture" if culture else "general-education"
    row = note(
        kind + "-approved-pool",
        expected,
        source,
        "Published title-specific approved pool, subject to the governing selection, level, business-subject and overlap rules as applicable. An unlisted course requires individual review of its description and syllabus. Level and semester columns are not credits or guaranteed offerings.",
        PREFIX + "-college-core-" + ("language-and-culture" if culture else kind),
        courses,
    )
    return {
        "id": PREFIX,
        "courses": list(courses.values()),
        "requirements": [row],
        "curriculum_status": "partial",
    }


def parse_culture(html):
    return parse_pool(html, culture=True)


def parse_gened(html):
    return parse_pool(html, culture=False)


def parse_overlap(html):
    soup = BeautifulSoup(html, "html.parser")
    if not any(
        text(h) == "College of Science Not Recommended Course List"
        for h in soup.find_all(["h1", "h2"])
    ):
        raise ValueError("Purdue overlap heading missing")
    if (
        "Only one instance of an overlapping content course will apply toward graduation requirements"
        not in text(soup)
    ):
        raise ValueError("Purdue overlapping-credit rule changed")
    rows = []
    for table in soup.find_all("table"):
        if [text(h) for h in table.find("tr").find_all("th")] != [
            "College Major / Subject",
            "Course Area",
            "Overlapping Courses",
        ]:
            continue
        for tr in table.find_all("tr"):
            cells = tr.find_all("td", recursive=False)
            if len(cells) == 3 and text(cells[0]) == "All Majors":
                area, codes = text(cells[1]), text(cells[2])
                if not re.search(r"\b[A-Z]+ \d", codes):
                    raise ValueError("Overlap identifiers missing")
                rows.append(
                    note(
                        "overlap-" + str(len(rows) + 1),
                        area + " overlapping credit",
                        "purdue-science-overlap",
                        "Only one overlapping-content instance applies toward graduation in this published group: "
                        + codes
                        + ". Preserve any paired-course combination and campus qualifications as printed; this is a credit restriction, not an additional course requirement.",
                    )
                )
    if not rows:
        raise ValueError("No all-major overlapping course groups")
    return {"id": PREFIX, "requirements": rows, "curriculum_status": "partial"}


def parse_experience(html):
    soup = BeautifulSoup(html, "html.parser")
    value = text(soup)
    if not any(
        text(h) == "Language and Culture Experiential Guidelines"
        for h in soup.find_all(["h1", "h2"])
    ):
        raise ValueError("Purdue experiential heading missing")
    waiver = re.search(
        r"Fall (\d{4}) catalog terms and forward - maximum (\w+) credits of (\w+) required credits",
        value,
    )
    short = re.search(
        r"minimum (\w+) \((\d+)\) days containing a minimum (\d+)-credit course", value
    )
    if not waiver or not short or "outside the United States" not in value:
        raise ValueError("Study abroad cohort/duration conditions missing")
    row = note(
        "study-abroad-detail",
        "Study abroad approval and documentation",
        "purdue-science-language-experience",
        f"From Fall {waiver[1]}, approved study abroad may waive at most {waiver[2]} of {waiver[3]} culture credits. Experience must occur outside the US; the printed short-program minimum is {short[2]} days with a {short[3]}-credit course. Review the cited additional approved program routes, immersion, contract and reflection conditions.",
        PREFIX + "-college-core-language-and-culture",
    )
    return {"id": PREFIX, "requirements": [row], "curriculum_status": "partial"}
