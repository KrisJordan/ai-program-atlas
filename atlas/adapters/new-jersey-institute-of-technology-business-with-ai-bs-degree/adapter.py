"""Read NJIT's published Business with AI degree plan, including open GER slots."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "new-jersey-institute-of-technology-business-with-ai-bs-degree"
SOURCES = (
    "https://catalog.njit.edu/undergraduate/management/management/business-with-ai-bs/",
    "https://management.njit.edu/bachelors-science-business-ai",
)
SOURCE_ID = PROGRAM_ID + "-official"


def text(n):
    return " ".join(n.get_text(" ", strip=True).split())


def req(suffix, title, kind="all", parent=None, credits=None, course_ids=(), summary=""):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": parent,
        "title": title,
        "kind": kind,
        "count": None,
        "credits": credits,
        "credit_unit": "semester_hours",
        "category": "other",
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
        "course_ids": list(course_ids),
    }


def parse(html):
    s = BeautifulSoup(html, "html.parser")
    h = s.find(lambda n: n.name == "h1" and text(n) == "Business with AI")
    table = s.find("table", class_="sc_plangrid")
    if h is None or text(h) != "Business with AI" or table is None:
        raise ValueError("Expected NJIT degree plan")
    total = re.search(r"\((\d+) credit minimum\)", text(s))
    if total is None:
        raise ValueError("Degree minimum missing")
    requirements = [
        req(
            "total",
            "Published degree minimum",
            credits=int(total[1]),
            summary="Official plan of study; generic GER and free-elective rows require linked rules. Full university and school graduation policies remain under review.",
        )
    ]
    courses = []
    term = None
    year = None
    slot = 0
    for row in table.find_all("tr"):
        classes = row.get("class", [])
        if "plangridyear" in classes:
            year = text(row)
            continue
        if "plangridterm" in classes:
            label = text(row.find("th"))
            term = req(
                "term-" + str(len([r for r in requirements if "-term-" in r["id"]]) + 1),
                year + " — " + label,
                parent=requirements[0]["id"],
                summary="Published suggested term placement; not a prerequisite or unique offering guarantee.",
            )
            requirements.append(term)
            continue
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        if "plangridsum" in classes:
            continue
        if "plangridtotal" in classes:
            continue
        hours = row.find("td", class_="hourscol")
        if hours is None or not re.fullmatch(r"\d+", text(hours)):
            raise ValueError("Unrecognized plan row credit")
        credits = int(text(hours))
        codecell = row.find("td", class_="codecol")
        anchor = codecell.find("a", class_="code") if codecell else None
        if term is None:
            raise ValueError("Plan row outside semester")
        if anchor:
            code = text(anchor)
            title = row.find("td", class_="titlecol")
            if title is None or not re.fullmatch(r"[A-Z]+ (\d+|SEM)", code):
                raise ValueError("Unrecognized course row")
            cid = "njit-" + code.lower().replace(" ", "-")
            courses.append(
                {
                    "id": cid,
                    "code": code,
                    "name": text(title),
                    "description": None,
                    "prerequisites": None,
                    "credits": credits,
                    "credit_unit": "semester_hours",
                    "category": "other",
                    "source_id": SOURCE_ID,
                    "url": urljoin(SOURCES[0], anchor["href"]).replace(" ", "%20"),
                    "public_site": None,
                    "syllabus": None,
                }
            )
            term["course_ids"].append(cid)
        else:
            if codecell is None:
                raise ValueError("Unrecognized non-course plan row")
            slot += 1
            label = text(codecell)
            requirements.append(
                req(
                    "slot-" + str(slot),
                    label,
                    "note",
                    term["id"],
                    credits=credits,
                    summary="Published open curriculum slot. Approved options and applicable general-education rules must be consulted separately.",
                )
            )
    if not courses or len({c["id"] for c in courses}) != len(courses):
        raise ValueError("Missing or duplicate named courses")
    return {
        "id": PROGRAM_ID,
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
    }


def parse_award(html):
    from atlas.adapters.final_discovery_common import parse_claims

    return parse_claims(
        html,
        program_id=PROGRAM_ID,
        title="Business with AI",
        award="BS",
        kind="degree",
        heading="What is Business with AI",
        claims=["Bachelor of Science in Business with AI"],
    )


SOURCE_PARSERS = {SOURCES[0]: parse, SOURCES[1]: parse_award}

from atlas.adapters.njit_degree_policies import SOURCE_PARSERS as POLICY_PARSERS
SOURCE_PARSERS.update(POLICY_PARSERS)
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.njit_science_options import SOURCE_PARSERS as SCIENCE_PARSERS
SOURCE_PARSERS.update(SCIENCE_PARSERS)
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.njit_required_course_reviews import SOURCE_PARSERS as REQUIRED_PARSERS
SOURCE_PARSERS.update(REQUIRED_PARSERS)
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.njit_science_subject_reviews import register as register_science_subjects
register_science_subjects(SOURCE_PARSERS)

from functools import partial
from atlas.adapters.njit_humanities_subject_reviews import URL as HUMANITIES_URL, combine as combine_humanities
SOURCE_PARSERS[HUMANITIES_URL] = partial(combine_humanities, SOURCE_PARSERS[HUMANITIES_URL])

from atlas.adapters.njit_history_subject_reviews import URL as HISTORY_URL, parse as parse_history
SOURCE_PARSERS[HISTORY_URL] = parse_history
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.njit_seminar_art_reviews import SOURCE_PARSERS as SEMINAR_ART_PARSERS
SOURCE_PARSERS.update(SEMINAR_ART_PARSERS)
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.njit_arts_communication_reviews import URL as ARTS_URL, combine as combine_arts
SOURCE_PARSERS[ARTS_URL] = partial(combine_arts, SOURCE_PARSERS[ARTS_URL])
SOURCES = tuple(SOURCE_PARSERS)
