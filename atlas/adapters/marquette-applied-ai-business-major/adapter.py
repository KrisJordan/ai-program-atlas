"""Observe CourseLeaf tables and policy constraints; never certify a refresh."""

import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import course, requirement, slug, text

PROGRAM_ID = "marquette-applied-ai-business-major"
TITLE = "Applied Artificial Intelligence in Business"
BASE = "https://bulletin.marquette.edu"
CATALOG = BASE + "/business-administration/applied-artificial-intelligence/"
POLICIES = {
    "grades": (BASE + "/business-administration/policies/grade-minimums/", "Grade Minimums"),
    "declare": (
        BASE + "/business-administration/policies/declaration-major/",
        "Declaration of Major",
    ),
    "graduation": (BASE + "/policies/graduation/undergraduate/", "Graduation - Undergraduate"),
    "uni-declare": (
        BASE + "/policies/major-declaration/",
        "Major and Minor Declaration - Undergraduate",
    ),
    "crnc": (BASE + "/business-administration/policies/crnc-option/", "CR/NC Option"),
}
SOURCES = [CATALOG] + [u for u, _ in POLICIES.values()]


def candidate(courses=(), requirements=()):
    return dict(
        id=PROGRAM_ID,
        title=TITLE,
        award_level="other",
        program_kind="additional_major",
        catalog_year=None,
        curriculum_status="partial",
        courses=list(courses),
        requirements=list(requirements),
        notes=["Observed source component; requires review and does not certify the host degree."],
    )


def req(key, title, source=None, **kwargs):
    return requirement(
        PROGRAM_ID, key, title, source or PROGRAM_ID + "-catalog", unit="semester_hours", **kwargs
    )


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if not main or not main.find("h1") or text(main.find("h1")) != TITLE + ", Major":
        raise ValueError("Marquette major heading changed")
    section = main.find(id="requirementstextcontainer")
    if not section or "must pair this major with an additional primary major" not in text(section):
        raise ValueError("Additional-major eligibility missing")
    tables = section.find_all("table", class_="sc_courselist")
    if len(tables) != 2:
        raise ValueError("Major/focus tables changed")
    courses = {}
    for table in tables:
        for row in table.find_all("tr"):
            cc = row.find("td", class_="codecol")
            if not cc:
                continue
            link = cc.find("a")
            cells = row.find_all("td", recursive=False)
            if not link or len(cells) < 3:
                raise ValueError("Malformed course row")
            code = text(link)
            hours = text(cells[-1])
            credits = float(hours) if re.fullmatch(r"\d+(?:\.\d+)?", hours) else None
            courses[code] = course(
                code,
                text(cells[1]),
                PROGRAM_ID + "-catalog",
                urljoin(BASE, link["href"]),
                institution="marquette",
                unit="semester_hours",
                credits=credits,
            )
    requirements = []
    root = req(
        "total", "Additional major including shared primary-major credit", kind="all", credits=None
    )
    requirements.append(root)
    electives = None
    for row in tables[0].find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        label = text(cells[0])
        hours = text(cells[-1])
        value = float(hours) if hours.isdigit() else None
        if "listsum" in row.get("class", []):
            root["credits"] = value
            continue
        cc = row.find("td", class_="codecol")
        if cc:
            c = courses[text(cc)]
            if cc.find(class_="blockindent"):
                if not electives:
                    raise ValueError("Elective course before choice rule")
                electives["course_ids"].append(c["id"])
            else:
                requirements.append(
                    req(
                        "required-" + slug(c["code"]),
                        c["name"],
                        parent=root["id"],
                        course_ids=[c["id"]],
                        credits=c["credits"],
                    )
                )
        elif "Upper Division Business Electives" in label:
            requirements.append(
                req(
                    "primary-shared",
                    "Shared upper-division primary-major credit",
                    kind="choose_credits",
                    credits=value,
                    parent=root["id"],
                    summary="Completed in the required primary business major; this credit is included in the additional-major total.",
                )
            )
        elif "Disruptive Tech or Machine Learning Focus" in label:
            requirements.append(
                req(
                    "focus",
                    "Choose one focus",
                    kind="alternative",
                    count=1,
                    credits=value,
                    parent=root["id"],
                )
            )
        elif "Complete two of the following electives" in label:
            electives = req(
                "electives",
                "Choose two business AI electives",
                kind="choose_courses",
                count=2,
                credits=value,
                parent=root["id"],
            )
            requirements.append(electives)
        else:
            raise ValueError("Unrecognized major requirement: " + label)
    group = None
    for row in tables[1].find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        label = text(cells[0])
        cc = row.find("td", class_="codecol")
        if cc:
            if not group:
                raise ValueError("Focus course outside focus")
            group["course_ids"].append(courses[text(cc)]["id"])
        elif label in ("Disruptive Tech", "Machine Learning"):
            group = req(
                "focus-" + slug(label.removeprefix("Or ")),
                label.removeprefix("Or "),
                parent=PROGRAM_ID + "-focus",
            )
            requirements.append(group)
        elif label not in ("Choose one of the following focus areas:", "Or"):
            raise ValueError("Unrecognized focus: " + label)
    if (
        root["credits"] is None
        or electives is None
        or len([r for r in requirements if r["parent_id"] == PROGRAM_ID + "-focus"]) != 2
    ):
        raise ValueError("Incomplete major rules")
    requirements.append(
        req(
            "eligibility",
            "Primary business major required",
            kind="note",
            summary="This is an additional major paired with an eligible primary major in the College of Business Administration.",
        )
    )
    result = candidate(courses.values(), requirements)
    year = re.search(r"(20\d{2})-(\d{2}) Edition", text(soup))
    result["catalog_year"] = year[1] + "-20" + year[2] if year else None
    return result


def parse_policy(html, key):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    expected = POLICIES[key][1]
    if not main or not main.find("h1") or text(main.find("h1")) != expected:
        raise ValueError("Policy heading changed")
    body = text(main)
    source = PROGRAM_ID + "-" + key
    rules = {
        "graduation": [
            (
                "major-gpa",
                "Major GPA",
                "minimum GPA of 2.000",
                "The major requires a GPA of at least 2.000.",
            ),
            (
                "major-residence",
                "Major residence",
                "one-half of credits in the major",
                "At least half of major credits must be completed at Marquette; degree-wide residency rules also apply.",
            ),
        ],
        "uni-declare": [
            (
                "university-declaration",
                "University major declaration and residence",
                "minimum of 15 credits in the major",
                "Only degree-seeking students may declare; Business students must declare before junior year. The current curriculum at declaration normally applies. At least 15 major credits must be completed at Marquette.",
            )
        ],
        "grades": [
            (
                "minimum-grade",
                "Major course grades",
                "grade of C or higher",
                "All major requirements and electives, including introductory core courses, require C or higher. Credit is not awarded twice for a repeated course except distinct variable-topic sections.",
            )
        ],
        "crnc": [
            (
                "letter-grading",
                "Major courses cannot use CR/NC",
                "only general elective credits",
                "CR/NC is restricted to general electives; it cannot satisfy major requirements.",
            )
        ],
        "declare": [
            (
                "eligible-primary",
                "Eligible primary majors",
                "must accompany",
                "Pair with accounting, business economics, finance, human resources, information systems, marketing, operations and supply chain management, or real estate. Business administration does not permit a second business major.",
            ),
            (
                "sharing",
                "Credit sharing across business majors",
                "minimum of 30 credits",
                "Requirements and upper-division electives may be shared across majors, with at least 30 upper-division credits for two majors. Sharing never reduces degree credit totals.",
            ),
            (
                "international",
                "International business content",
                "At least one course with International Business content",
                "At least one course with international business content is required, within or outside the declared business majors.",
            ),
            (
                "declaration",
                "Declaration and major limit",
                "maximum of three business majors",
                "Students should declare before senior-year advising and registration; a maximum of three business majors is permitted.",
            ),
        ],
    }
    requirements = []
    for rid, title, guard, summary in rules[key]:
        if guard not in body:
            raise ValueError("Policy clause missing: " + guard)
        requirements.append(req(rid, title, source, kind="note", summary=summary))
    return candidate(requirements=requirements)


SOURCE_PARSERS = {
    CATALOG: parse,
    **{
        url: (lambda html, key=key: parse_policy(html, key))
        for key, (url, title) in POLICIES.items()
    },
}


from atlas.adapters.additional_business_metadata import register
register(PROGRAM_ID, SOURCES, SOURCE_PARSERS)
