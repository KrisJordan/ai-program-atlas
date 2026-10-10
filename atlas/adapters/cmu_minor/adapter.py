"""Complete local AI minor inventory; parent degrees and course metadata are separate."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from atlas.adapters.cmu_bs.common import course, requirement, slug, text

PROGRAM_ID = "cmu-minor-ai"
SOURCES = [
    "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/minors/artificial-intelligence-minor/"
]
SOURCE = PROGRAM_ID + "-catalog"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup
    h1 = main.find("h1")
    if not h1 or text(h1) != "Artificial Intelligence, Minor":
        raise ValueError("CMU minor heading missing")
    content = soup.find(id="textcontainer") or soup.find("main") or soup
    year = re.search(r"(20\d{2})[-–](20\d{2})\s+Catalog", text(soup))
    if not year:
        raise ValueError("CMU catalog edition missing")
    labels = [
        "Prerequisites",
        "Required Core Courses",
        "Technical Electives",
        "Societal Aspects of AI",
        "Double Counting",
    ]
    headings = content.find_all("h4")
    if [text(h) for h in headings] != labels:
        raise ValueError("CMU minor section inventory changed")
    words = text(content)
    rules = [
        (r"minor consists of six courses", "Six-course total"),
        (r"not available to SCS students", "Non-SCS eligibility"),
        (r'"C" average in all prerequisite coursework', "Admission grade average"),
        (r"no later than the semester before they intend to graduate", "Application deadline"),
        (r"maximum one page", "Application statement"),
        (r"two of the following three cluster areas", "Distinct technical clusters"),
        (r"one of the following two cluster areas", "Societal cluster choice"),
        (r"Each course must be a minimum of 9 units", "Elective unit minimum"),
        (r"Two mini courses can be combined to form one 9 unit course", "Mini-course exception"),
        (r"at most,?\s*two courses\s*total", "Double-count limit"),
        (r"not counting the prerequisite courses", "Prerequisite overlap exception"),
        (r"all other majors and minors", "Aggregate overlap scope"),
    ]
    for pattern, label in rules:
        if not re.search(pattern, words, re.I):
            raise ValueError("CMU minor policy changed: " + label)
    courses = {}
    reqs = []

    def add(key, title, **kwargs):
        r = requirement(PROGRAM_ID, key, title, SOURCE, **kwargs)
        reqs.append(r)
        return r

    root = add(
        "minor",
        "Six-course AI minor",
        count=6,
        summary="Three core courses, two technical electives from distinct clusters, and one societal elective; prerequisite courses are additional.",
    )
    for heading in headings[:-1]:
        label = text(heading)
        table = heading.find_next_sibling("table")
        if table is None or "sc_courselist" not in table.get("class", []):
            raise ValueError("CMU minor table missing: " + label)
        is_pre = label == "Prerequisites"
        is_core = label == "Required Core Courses"
        category = (
            "foundations"
            if is_pre
            else "human_context"
            if label == "Societal Aspects of AI"
            else "ai_ml"
        )
        parent = add(
            slug(label),
            label,
            parent=None if is_pre else root["id"],
            category=category,
            kind="all" if is_pre or is_core else "choose_courses",
            count=4 if is_pre else 3 if is_core else 2 if label == "Technical Electives" else 1,
            summary=(
                "Complete one option in each of four prerequisite groups."
                if is_pre
                else "Complete probability plus 07-280 and 07-380."
                if is_core
                else "Select two distinct cluster children and one course in each, each at least 9 units."
                if label == "Technical Electives"
                else "Select one course from either cluster, at least 9 units; two mini courses may form one 9-unit course."
            ),
        )
        branch = None
        group_number = 0
        cluster_count = 0
        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            codecell = row.find("td", class_="codecol")
            if not codecell:
                comment = row.select_one(".courselistcomment")
                if comment and "Cluster" in text(comment):
                    cluster_count += 1
                    branch = add(
                        slug(label) + "-" + slug(text(comment)),
                        text(comment),
                        parent=parent["id"],
                        category=category,
                        kind="choose_courses",
                        count=1,
                        summary="Optional cluster branch: choose one eligible course of at least 9 units when selecting this cluster.",
                    )
                continue
            link = codecell.find("a")
            if not link or len(cells) < 2 or not re.fullmatch(r"\d{2}-\d{3}", text(link)):
                raise ValueError("CMU minor unexpected course row")
            code = text(link)
            hours = row.select_one(".hourscol")
            value = text(hours) if hours else ""
            credits = float(value) if re.fullmatch(r"\d+(?:\.\d+)?", value) else None
            item = course(
                code,
                text(cells[1]),
                SOURCE,
                urljoin(SOURCES[0], link.get("href", "")),
                category,
                credits,
            )
            courses[item["id"]] = item
            if is_pre or is_core:
                if "orclass" not in row.get("class", []):
                    group_number += 1
                    branch = add(
                        slug(label) + "-option-" + str(group_number),
                        "Prerequisite group " + str(group_number)
                        if is_pre
                        else "Core requirement " + str(group_number),
                        parent=parent["id"],
                        category=category,
                        kind="choose_courses",
                        count=1,
                    )
                if branch is None:
                    raise ValueError("CMU minor orphan alternative")
            if branch is None:
                raise ValueError("CMU minor course outside recognized group")
            branch["course_ids"].append(item["id"])
        if is_pre and group_number != 4 or is_core and group_number != 3:
            raise ValueError("CMU minor prerequisite/core group count changed")
        if (
            not is_pre
            and not is_core
            and cluster_count != (3 if label == "Technical Electives" else 2)
        ):
            raise ValueError("CMU minor elective cluster count changed")
    add(
        "eligibility",
        "Eligibility and admission",
        kind="note",
        category="other",
        summary="Unavailable to SCS students. Complete all four prerequisite groups and 07-280 with a C average, consult the program administrator, and apply with a statement of at most one page no later than the semester before graduation. Applications may use midterm grades.",
    )
    add(
        "mini-courses",
        "Mini-course combination",
        kind="note",
        category="human_context",
        summary="The societal-elective table permits two mini courses to combine as one 9-unit course; individual eligible mini courses are not named.",
    )
    add(
        "double-counting",
        "Double-counting limit",
        kind="note",
        category="other",
        summary="At most two courses from the six-course AI requirements may also count toward all other majors/minors combined. Prerequisites are excluded from this limit. Substantially overlapping majors require consultation with the program administrator.",
    )
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence, Minor",
        "award_level": "minor",
        "program_kind": "minor",
        "catalog_year": year.group(1) + "-" + year.group(2),
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": reqs,
        "notes": [
            "Complete published local minor requirement inventory, including admission prerequisites, distinct-cluster choices, mini-course exception and aggregate overlap cap. This does not certify a student's host degree. Individual course descriptions/prerequisites are a separate metadata gap; no verification timestamp is renewed."
        ],
    }


# A separate metadata candidate never certifies program requirements.
from atlas.adapters.cmu_bs.course_metadata import COURSE_SOURCE, parse_metadata

METADATA_CODES = (
    "15-121",
    "15-122",
    "21-112",
    "21-120",
    "21-259",
    "21-127",
    "21-128",
    "15-151",
    "21-240",
    "21-241",
    "15-259",
    "21-325",
    "21-425",
    "36-218",
    "36-225",
    "36-235",
    "07-280",
    "07-380",
    "15-386",
    "15-482",
    "15-494",
    "16-350",
    "16-362",
    "16-384",
    "85-213",
    "85-412",
    "85-419",
    "85-420",
    "85-472",
    "10-403",
    "10-405",
    "10-414",
    "10-417",
    "10-418",
    "10-422",
    "10-423",
    "10-424",
    "10-425",
    "11-441",
    "11-485",
    "15-388",
    "67-364",
    "36-401",
    "36-402",
    "11-411",
    "11-442",
    "11-492",
    "15-387",
    "15-463",
    "16-385",
    "85-370",
    "85-408",
    "05-317",
    "05-318",
    "05-391",
    "16-467",
    "16-161",
    "16-735",
    "17-200",
    "79-302",
    "80-249",
    "88-230",
    "88-275",
)
SOURCES.append(COURSE_SOURCE)
SOURCE_PARSERS = {
    COURSE_SOURCE: lambda html: parse_metadata(html, pid=PROGRAM_ID, codes=METADATA_CODES)
}


from atlas.adapters.cmu_bs.course_resources import register as register_course_resources

register_course_resources(PROGRAM_ID, SOURCES, SOURCE_PARSERS)
