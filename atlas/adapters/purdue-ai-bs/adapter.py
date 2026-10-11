"""Purdue's Fall-2026 AI major page: observed curriculum, never a seed replay."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "purdue-ai-bs"

SOURCES = (
    "https://www.cs.purdue.edu/undergraduate/curriculum/bachelor-ai.html",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/college-of-science-core-requirements.html",
    "https://www.cs.purdue.edu/academic-programs/courses/canonical/cs180.html",
    "https://www.cs.purdue.edu/academic-programs/courses/canonical/cs182.html",
    "https://www.cs.purdue.edu/academic-programs/courses/canonical/cs37300.html",
)
COLLEGE_SOURCE_ID = "purdue-science-core"
SOURCE_ID = "purdue-ai-bs-curriculum"
PREFIX = "purdue-ai-bs"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def key(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def category(code):
    if code.startswith(("MA ", "STAT ")):
        return "mathematics"
    if code.startswith(("PHIL ", "PSY ")):
        return "human_context"
    if code in {"CS 24300", "CS 37300", "CS 47100", "CS 47700", "CS 57700", "CS 57800"}:
        return "ai_ml"
    if code in {"CS 34800", "CS 44800", "CS 52900"}:
        return "systems"
    return (
        "foundations"
        if code in {"CS 17600", "CS 18000", "CS 18200", "CS 25300", "CS 38100", "CS 48300"}
        else "applications"
    )


def course(code, name, credits, href):
    return {
        "id": "purdue-" + key(code),
        "code": code,
        "name": name,
        "description": None,
        "prerequisites": None,
        "credits": credits,
        "credit_unit": "semester_hours",
        "category": category(code),
        "source_id": SOURCE_ID,
        "url": urljoin(SOURCES[0], href),
        "public_site": None,
        "syllabus": None,
    }


def requirement(
    suffix, title, kind, ids=(), *, parent=None, count=None, credits=None, summary="", cat="other"
):
    return {
        "id": PREFIX + "-" + suffix,
        "parent_id": parent,
        "title": title,
        "kind": kind,
        "count": count,
        "credits": credits,
        "credit_unit": "semester_hours",
        "category": cat,
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
        "course_ids": list(ids),
    }


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1 or not re.fullmatch(
        r"Artificial Intelligence Degree Requirements\s*[-–]\s*Fall (\d{4}) to Present", text(h1)
    ):
        raise ValueError("Expected Purdue AI degree curriculum heading")
    year = re.search(r"Fall (\d{4})", text(h1)).group(1)
    table = next(
        (
            t
            for t in soup.find_all("table")
            if t.find("caption") and "Core Requirements" in text(t.find("caption"))
        ),
        None,
    )
    if table is None:
        raise ValueError("Purdue AI core requirements table missing")
    caption = text(table.find("caption"))
    requirements = [requirement("core", "Core requirements", "all", summary=caption)]
    courses = {}
    required = []
    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 3:
            continue
        links = cells[0].find_all("a")
        codes = [text(a) for a in links]
        names = re.split(r"\s+or\s+", text(cells[1]), flags=re.IGNORECASE)
        raw = text(cells[2])
        amounts = raw.split("/")
        if not codes or len(names) != len(codes):
            raise ValueError("Unrecognized core course alternatives")
        ids = []
        for i, (code, name, anchor) in enumerate(zip(codes, names, links)):
            if not re.fullmatch(r"[A-Z]+ \d{5}", code):
                raise ValueError("Unrecognized Purdue course code")
            credit_text = amounts[i] if len(amounts) == len(codes) else raw
            credits = float(credit_text) if re.fullmatch(r"\d+(?:\.\d+)?", credit_text) else None
            item = course(code, name, credits, anchor.get("href", ""))
            courses[item["id"]] = item
            ids.append(item["id"])
        if len(ids) > 1:
            requirements.append(
                requirement(
                    "core-" + key(codes[0]),
                    " / ".join(codes),
                    "alternative",
                    ids,
                    parent=PREFIX + "-core",
                    count=1,
                    credits=float(raw) if raw.isdigit() else None,
                    summary="Complete one of these alternatives.",
                    cat=category(codes[0]),
                )
            )
        else:
            required.extend(ids)
    if not courses:
        raise ValueError("No core courses extracted")
    requirements[0]["course_ids"] = required
    expected = {"CS Selective I": 2, "CS Selective II": 1, "Philosophy Selective": 1}
    for label, count in expected.items():
        heading = soup.find("h3", string=re.compile(re.escape(label) + r"\s*\("))
        if not heading:
            raise ValueError(f"Missing {label}")
        credit_match = re.search(r"\((\d+) credits\)", text(heading), re.IGNORECASE)
        ul = heading.find_next("ul")
        if not credit_match or ul is None:
            raise ValueError(f"Malformed {label}")
        directive = heading.find_next("p")
        choice = (
            re.search(r"Choose (one|two|three|\d+)", text(directive), re.IGNORECASE)
            if directive
            else None
        )
        if choice is None:
            raise ValueError(f"Missing selection count for {label}")
        raw_count = choice.group(1).lower()
        count = (
            int(raw_count) if raw_count.isdigit() else {"one": 1, "two": 2, "three": 3}[raw_count]
        )
        rid = PREFIX + "-" + key(label)
        ids, nlp = [], []
        for li in ul.find_all("li", recursive=False):
            anchor = li.find("a")
            if anchor is None:
                raise ValueError("Selective without a course link")
            code = text(anchor)
            name = re.sub(r"^[*\s-]+", "", text(li).removeprefix(code))
            name = re.sub(r"\s+OR$", "", name, flags=re.IGNORECASE)
            item = course(code, name, None, anchor.get("href", ""))
            courses[item["id"]] = item
            (nlp if code in {"CS 47700", "CS 57700"} else ids).append(item["id"])
        requirements.append(
            requirement(
                key(label),
                label,
                "choose_courses",
                ids,
                count=count,
                credits=int(credit_match.group(1)),
                summary=f"Choose {count} course option(s), including any nested alternative as one option.",
                cat="human_context" if label.startswith("Philosophy") else "electives",
            )
        )
        if nlp:
            requirements.append(
                requirement(
                    "nlp-alternative",
                    "NLP course alternative",
                    "alternative",
                    nlp,
                    parent=rid,
                    count=1,
                    summary="The undergraduate and graduate NLP courses are one selective option.",
                    cat="ai_ml",
                )
            )
    cap = soup.find("h3", string=re.compile("Capstone Requirement for Artificial Intelligence"))
    if cap is None:
        raise ValueError("Missing AI capstone requirement")
    cap_note = cap.find_next("p")
    cap_codes = re.findall(r"CS \d{5}", text(cap_note)) if cap_note else []
    if cap_codes != ["CS 37300", "CS 38100", "CS 47100"] or "C or better" not in text(cap_note):
        raise ValueError("Capstone prerequisites changed; manual review required")
    requirements.append(
        requirement(
            "capstone",
            "Capstone experience",
            "alternative",
            count=1,
            credits=3,
            summary="Choose one approved capstone route; CS 37300, CS 38100 and CS 47100 require C or better before starting.",
            cat="applications",
        )
    )
    for i, li in enumerate(cap.find_next("ul").find_all("li", recursive=False)):
        amount = re.search(r"(?:Credit Hours|Credits):\s*(\d+(?:\.\d+)?)", text(li))
        if not amount or float(amount.group(1)) != 3:
            raise ValueError("Capstone credits changed; manual review required")
        anchor = li.find("a")
        ids = []
        if anchor:
            code = text(anchor)
            name = re.split(r"Credit Hours:", text(li).removeprefix(code).strip(" -\u00a0"))[
                0
            ].strip()
            item = course(code, name, 3, anchor.get("href", ""))
            item["prerequisites"] = (
                "CS 37300, CS 38100 and CS 47100, each with C or better, before the capstone."
            )
            courses[item["id"]] = item
            ids = [item["id"]]
            title = name
        else:
            wording = text(li).lower()
            title = next(
                (
                    label
                    for needle, label in [
                        ("unpaid research", "Pre-approved unpaid AI research"),
                        ("honors project", "Pre-approved AI honors project"),
                        ("ai forge", "Pre-approved AI Forge project"),
                    ]
                    if needle in wording
                ),
                None,
            )
            if title is None:
                raise ValueError("Unrecognized capstone route; manual review required")
        requirements.append(
            requirement(
                "capstone-route-" + str(i + 1),
                title,
                "all" if ids else "note",
                ids,
                parent=PREFIX + "-capstone",
                credits=3,
                summary=title,
                cat="applications",
            )
        )
    if "all major required courses" in text(soup):
        requirements.extend(parse_major_policies(html)["requirements"])
    return {
        "id": PREFIX,
        "title": "Artificial Intelligence, BS",
        "award_level": "BS",
        "program_kind": "degree",
        "catalog_year": None,
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": requirements,
        "notes": [
            f"Curriculum applies from Fall {year}; catalog edition was not independently accessible.",
            "Department major requirements only; college and university degree requirements are not fully extracted.",
            "Core credits are a range; individual elective credits remain unknown unless directly stated. Categories are editorial classifications.",
        ],
    }


def parse_college_core(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1 or text(h1) != "College of Science Core Curriculum Requirements":
        raise ValueError("Expected College of Science core heading")
    introduction = next(
        (
            p
            for p in soup.find_all("p")
            if "requires the completion of approved coursework" in text(p)
        ),
        None,
    )
    listing = introduction.find_next_sibling("ul") if introduction else None
    if listing is None:
        raise ValueError("College core areas missing")
    requirements = [
        requirement(
            "college-core",
            "College of Science core",
            "all",
            summary="Approved coursework and/or experiential learning across the college core areas; alternatives and overlap rules await review.",
        )
    ]
    for li in listing.find_all("li", recursive=False):
        anchor = li.find("a", href=True)
        if anchor is None or not text(anchor):
            raise ValueError("College core area link missing")
        title = text(anchor)
        requirements.append(
            requirement(
                "college-core-" + key(title),
                title,
                "note",
                parent=PREFIX + "-college-core",
                summary="Required college core area; linked options are not yet mapped. May overlap major requirements; do not add credits.",
            )
        )
    if len(requirements) < 2:
        raise ValueError("College core areas empty")
    for row in requirements:
        row["source_id"] = COLLEGE_SOURCE_ID
    return {"id": PROGRAM_ID, "requirements": requirements, "curriculum_status": "partial"}


SOURCE_PARSERS = {SOURCES[1]: parse_college_core}

# College detail observations are candidates; the reviewer retains the policy audit.
SCIENCE_BASE = "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/"
DETAIL_URLS = {
    "writing": SCIENCE_BASE + "approved-courses-in-technical-writing.html",
    "great-issues": SCIENCE_BASE + "Great%20Issues%20Courses.php",
    "language": SCIENCE_BASE + "current-students-page1.html",
    "general-education": SCIENCE_BASE + "general-education.html",
}


def detail_page(html, expected):
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if h1 is None or text(h1) != expected:
        raise ValueError("Unexpected Purdue college detail heading")
    return h1.parent


def parse_writing_courses(html):
    page = detail_page(html, "Approved courses in Technical Writing and Presenting")
    pools = {"writing": [], "presentation": [], "combined": []}
    courses = {}
    section = None
    for p in page.find_all("p", recursive=False):
        value = text(p)
        if value.startswith("Approved courses in Technical"):
            section = (
                "combined"
                if "Writing and Technical Presentation" in value
                else ("writing" if "Writing:" in value else "presentation")
            )
            continue
        if not section:
            continue
        expiry = re.search(
            r"(?:approval effective through(?: Spring,)?|approved Fall, \d{4} - Spring,) (\d{4})",
            value,
        )
        if expiry and int(expiry[1]) < 2026:
            continue
        item = re.fullmatch(r"([A-Z]+ \d{5})\s*:?[ ]+(.+)", value)
        if item is None:
            continue
        code, title = item.groups()
        title = re.sub(r"\s*\((?:formerly |approval effective through).+\)$", "", title)
        c = course(code, title, None, DETAIL_URLS["writing"])
        c["source_id"] = "purdue-science-writing"
        c["category"] = "human_context"
        # Two ENGL 42400 titles are printed. Retain both source observations as aliases.
        if c["id"] in courses and courses[c["id"]]["name"] != title:
            courses[c["id"]]["name"] += " / " + title
        else:
            courses[c["id"]] = c
        if c["id"] not in pools[section]:
            pools[section].append(c["id"])
    if any(not pool for pool in pools.values()):
        raise ValueError("Writing/presentation course pools incomplete")
    reqs = []
    for section, ids in pools.items():
        row = requirement(
            "writing-detail-" + section,
            "Approved " + section + " courses",
            "note",
            ids,
            parent=PREFIX + "-college-core-technical-writing-and-technical-presentation",
            summary="Source course pool. Combined courses satisfy both components; separate writing and presentation choices or approved experience are alternatives. University oral communication approvals also satisfy presentation.",
            cat="human_context",
        )
        row["source_id"] = "purdue-science-writing"
        reqs.append(row)
    return {
        "id": PROGRAM_ID,
        "courses": list(courses.values()),
        "requirements": reqs,
        "curriculum_status": "partial",
    }


def parse_great_issues(html):
    page = detail_page(html, "Great Issues in Science")
    table = page.find("table", id="example")
    if table is None or [text(t) for t in table.find("thead").find_all("th")] != [
        "Subject",
        "Number",
        "Keyword/Title",
        "UCORE",
        "Semester",
        "Level",
    ]:
        raise ValueError("Great Issues approved-course table changed")
    courses = []
    for tr in table.find("tbody").find_all("tr"):
        cells = [text(td) for td in tr.find_all("td", recursive=False)]
        if len(cells) != 6 or not re.fullmatch(r"\d{5}[A-Z]*", cells[1]):
            raise ValueError("Unexpected Great Issues course row")
        code = cells[0].split(" - ")[0] + " " + cells[1]
        name = cells[2].rstrip("*").strip()
        if not name:
            raise ValueError("Great Issues title missing")
        c = course(code, name, None, DETAIL_URLS["great-issues"])
        # Variable-title approvals are distinct; code alone must not merge them.
        c["id"] += "-" + key(name)
        c["source_id"] = "purdue-science-great-issues"
        c["category"] = "human_context"
        courses.append(c)
    if not courses:
        raise ValueError("Great Issues course table empty")
    row = requirement(
        "great-issues-detail-pool",
        "Approved Great Issues titles",
        "note",
        [c["id"] for c in courses],
        parent=PREFIX + "-college-core-great-issues",
        summary="Only the listed titles are approved, including variable-title courses. The Level column is a course level, not credits; listed semesters are not approval expiry dates.",
        cat="human_context",
    )
    row["source_id"] = "purdue-science-great-issues"
    return {
        "id": PROGRAM_ID,
        "courses": courses,
        "requirements": [row],
        "curriculum_status": "partial",
    }


def parse_language_options(html):
    page = detail_page(html, "Fall 2023 and Forward Language and Culture Options")
    headings = [
        p for p in page.find_all("p", recursive=False) if re.fullmatch(r"Option \d+:", text(p))
    ]
    if [text(p) for p in headings] != [f"Option {i}:" for i in range(1, 6)]:
        raise ValueError("Language/culture routes changed")
    rows = []
    for p in headings:
        option = int(re.search(r"\d+", text(p))[0])
        chunks = []
        for sibling in p.find_next_siblings():
            if sibling.name == "p" and text(sibling):
                break
            if sibling.name == "ul":
                chunks.append(text(sibling))
        value = " ".join(chunks)
        # Extract actual numeric course/experience facts without replaying the seed policy.
        amounts = re.findall(r"\((\d+)\)|minimum (\d+)-credit|minimum (\d+)-credit hour", value)
        observed = [int(next(x for x in groups if x)) for groups in amounts]
        if not value or not observed:
            raise ValueError("Language route conditions missing")
        row = requirement(
            "language-detail-option-" + str(option),
            "Language and culture option " + str(option),
            "note",
            parent=PREFIX + "-college-core-language-and-culture",
            summary=f"Published option {option}; explicitly stated numeric course/experience values: {', '.join(map(str, observed))}. Review the cited option's course, waiver and eligibility conditions before updating the curated rule.",
            cat="human_context",
        )
        row["source_id"] = "purdue-science-language"
        rows.append(row)
    return {"id": PROGRAM_ID, "requirements": rows, "curriculum_status": "partial"}


def parse_general_education(html):
    page = detail_page(html, "General Education Requirement")
    value = text(page)
    found = re.search(r"completing (\w+) courses \((\d+) credits\)", value)
    if not found or found[1] not in {"three", "four", "five"}:
        raise ValueError("General education selection rule missing")
    row = requirement(
        "college-core-general-education",
        "General Education",
        "choose_courses",
        count={"three": 3, "four": 4, "five": 5}[found[1]],
        credits=int(found[2]),
        parent=PREFIX + "-college-core",
        summary="Select from the college-approved general education list; subject limits, prohibited overlaps and excluded courses require review.",
        cat="human_context",
    )
    row["source_id"] = "purdue-science-general-education"
    return {"id": PROGRAM_ID, "requirements": [row], "curriculum_status": "partial"}


SOURCES += tuple(DETAIL_URLS.values())
SOURCE_PARSERS.update(
    {
        DETAIL_URLS["writing"]: parse_writing_courses,
        DETAIL_URLS["great-issues"]: parse_great_issues,
        DETAIL_URLS["language"]: parse_language_options,
        DETAIL_URLS["general-education"]: parse_general_education,
    }
)

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

# Policy-only sources remain available for provenance/change detection.
SOURCES += (
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/Freshmen%20Composition%20Requirement.html",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/TWTP%20Requirement.html",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/approved-courses-in-teambuilding-and-collaboration.html",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/earning-requirements-through-experience.html",
    "https://www.purdue.edu/science/Current_Students/general_education_elective_list.php",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/multidisciplinary-experience.html",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/laboratory-science.html",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/approved-sequences-in-laboratory-science.html",
    "https://www.purdue.edu/science/Current_Students/curriculum_and_degree_requirements/index.html",
)

from atlas.adapters import purdue_college_pools as college_pools

SOURCES += (college_pools.CULTURE_URL, college_pools.EXPERIENCE_URL, college_pools.OVERLAP_URL)
SOURCE_PARSERS.update(
    {
        college_pools.CULTURE_URL: college_pools.parse_culture,
        college_pools.GENED_URL: college_pools.parse_gened,
        college_pools.EXPERIENCE_URL: college_pools.parse_experience,
        college_pools.OVERLAP_URL: college_pools.parse_overlap,
    }
)

# Term offering directory supports reviewed metadata, not additional major requirements.
SOURCES += ("https://www.cla.purdue.edu/academic/philosophy/students/undergraduate/courses-new.html",)


def parse_major_policies(html):
    value = text(BeautifulSoup(html, "html.parser"))
    clauses = ["all major required courses", "all major electives (selectives)",
               "their pre-requisites, regardless of department", "grade of C or better",
               "100 and 200 level core courses", "before the student enters",
               "300 or 400 level CS coursework", "pre-approved Study Abroad coursework",
               "additional prerequisites that must be met to be eligible"]
    if any(clause not in value for clause in clauses):
        raise ValueError("Purdue major grade/transfer/graduate policy changed")
    specs = [
        ("major-grades", "Major and prerequisite minimum grades",
         "All major required courses, selectives, and their prerequisites, regardless of department, require C or better. This grade rule does not turn every prerequisite into a separately counted degree requirement."),
        ("major-transfer", "Department transfer-credit restrictions",
         "Transfer credit, including regional-campus credit, for 100/200-level core courses is possible only when taken before entry to Purdue West Lafayette Computer Science. No 300/400-level CS transfer coursework is accepted except pre-approved study abroad."),
        ("graduate-selective-eligibility", "Graduate selective prerequisites",
         "Graduate-level selective courses may require additional prerequisites for enrollment; these are not waived by appearance in the undergraduate selective pool.")]
    return {"id": PROGRAM_ID, "requirements": [requirement(k, title, "note", summary=summary) for k, title, summary in specs]}

# Subject observations are independent of requirement/pool membership.
from atlas.adapters.west_degree_subjects import observe as observe_subjects
parse = observe_subjects(parse, PROGRAM_ID)
SOURCE_PARSERS = {url: observe_subjects(parser, PROGRAM_ID) for url, parser in SOURCE_PARSERS.items()}

# Dated departmental outlines observe content without claiming current catalog access.
from atlas.adapters import purdue_canonical_course_reviews
purdue_canonical_course_reviews.attach(globals())

# Full reviewed public handbook blocks add policy observations, never courses.
from atlas.adapters import purdue_science_policy_reviews
if set(purdue_science_policy_reviews.PARSERS) & set(SOURCE_PARSERS):
    raise ValueError("Purdue handbook source parser collision")
SOURCES += purdue_science_policy_reviews.SOURCES
SOURCE_PARSERS.update(purdue_science_policy_reviews.PARSERS)
