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
