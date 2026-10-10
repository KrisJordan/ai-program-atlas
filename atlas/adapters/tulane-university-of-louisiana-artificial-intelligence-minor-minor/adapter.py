"""Observe Tulane's AI minor, including entrance and overlap conditions."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "tulane-university-of-louisiana-artificial-intelligence-minor-minor"
SOURCES = (
    "https://catalog.tulane.edu/science-engineering/computer-science/artificial-intelligence-minor/",
)
SOURCE_ID = PROGRAM_ID + "-official"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def key(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def req(suffix, title, kind, ids=(), credits=None, count=None, summary="", parent="total"):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": PROGRAM_ID + "-" + parent if parent else None,
        "title": title,
        "kind": kind,
        "course_ids": list(ids),
        "credits": credits,
        "count": count,
        "credit_unit": "unknown",
        "category": "other",
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
    }


def course(code, title, credits, url, category):
    return {
        "id": "tulane-" + key(code),
        "code": code,
        "name": title,
        "description": None,
        "prerequisites": None,
        "credits": credits,
        "credit_unit": "unknown",
        "category": category,
        "source_id": SOURCE_ID,
        "url": url,
        "public_site": None,
        "syllabus": None,
    }


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    heading = next(
        (h for h in soup.find_all("h1") if text(h) == "Artificial Intelligence Minor"), None
    )
    content = soup.find(id="requirementstextcontainer")
    if heading is None or text(heading) != "Artificial Intelligence Minor" or content is None:
        raise ValueError("Expected Tulane AI minor requirements")
    body = text(content)
    total = re.search(r"comprises of (\d+) courses, requiring (\d+) credits", body)
    gpa = re.search(r"cumulative GPA of (\d+\.\d+) or above", body)
    if total is None or gpa is None:
        raise ValueError("Minor total or GPA missing")
    guards = [
        "6000-level sections for these courses",
        "before declaring the minor",
        "only one course may overlap",
        "CMPS 2200",
        "4 (12 CR) extra",
        "may not fulfill the AI/Algorithms requirement",
        "advisor's and the departmental chair's signatures",
        "submitted to the Advising Office",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Minor substitution, entrance, overlap or declaration policy changed")
    table = content.find("table", class_="sc_courselist")
    if table is None:
        raise ValueError("Minor course table missing")
    courses, groups = {}, []
    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        if "areaheader" in row.get("class", []):
            title = text(row.find(class_="courselistcomment"))
            credits = text(row.find(class_="hourscol"))
            if not credits.isdigit():
                raise ValueError("Group credit total missing")
            groups.append({"title": title, "credits": int(credits), "ids": []})
            continue
        anchor = row.find("a", class_="code")
        if anchor is None or not groups:
            raise ValueError("Unrecognized course table row")
        code, title = text(anchor), text(cells[1])
        amount = text(row.find(class_="hourscol")) if row.find(class_="hourscol") else ""
        if not re.fullmatch(r"[A-Z]+ \d{4}", code) or (amount and not amount.isdigit()):
            raise ValueError("Unrecognized course code or credits")
        c = course(
            code,
            title,
            int(amount) if amount else None,
            urljoin(SOURCES[0], anchor["href"]),
            "foundations" if len(groups) == 1 else "ai_ml",
        )
        courses[c["id"]] = c
        groups[-1]["ids"].append(c["id"])
    if [g["title"] for g in groups] != [
        "Algorithms",
        "AI/ML Foundations",
        "AI/ML Electives (choose two)",
    ]:
        raise ValueError("Minor group inventory changed")
    requirements = [
        req(
            "total",
            "Minor courses and credits",
            "all",
            credits=int(total[2]),
            count=int(total[1]),
            parent=None,
        )
    ]
    for suffix, group in zip(["algorithms", "foundations", "electives"], groups):
        requirements.append(
            req(
                suffix,
                group["title"],
                "choose_courses" if suffix == "electives" else "all",
                group["ids"],
                credits=group["credits"],
                count=2 if suffix == "electives" else None,
            )
        )
    prereq_heading = next(
        (h for h in content.find_all("h3") if text(h) == "Academic Prerequisites"), None
    )
    listing = prereq_heading.find_next_sibling("ul") if prereq_heading else None
    if listing is None:
        raise ValueError("Declaration prerequisites missing")
    requirements.append(
        req(
            "prerequisites",
            "Before declaring: three prerequisite courses",
            "all",
            parent=None,
            summary="Complete the prerequisite sequence before declaring. These credits are outside the published 16-credit minor.",
        )
    )
    for index, li in enumerate(listing.find_all("li", recursive=False)):
        # Source cross-list CMPS/MATH 2170 is one course, not two separate requirements.
        fragments = re.split(r"\s+or\s+", text(li))
        ids = []
        for fragment in fragments:
            match = re.fullmatch(r"([A-Z]+(?:/[A-Z]+)? \d{4}) (.+) \((\d+) c\.h\.\)", fragment)
            if match is None:
                raise ValueError("Unrecognized prerequisite option")
            code, title, amount = match.groups()
            c = course(
                code,
                title,
                int(amount),
                SOURCES[0],
                "mathematics" if "2170" in code else "foundations",
            )
            courses[c["id"]] = c
            ids.append(c["id"])
        requirements.append(
            req(
                "prerequisite-" + str(index),
                "Prerequisite " + str(index + 1),
                "alternative" if len(ids) > 1 else "all",
                ids,
                count=1 if len(ids) > 1 else None,
                parent="prerequisites",
            )
        )
    requirements += [
        req(
            "graduate-sections",
            "6000-level section substitution",
            "note",
            summary="Corresponding 6000-level sections may satisfy AI/ML foundations and elective requirements, as indicated by footnote 1; no substitution is stated for Algorithms.",
        ),
        req(
            "gpa",
            "Minor cumulative GPA",
            "note",
            summary=f"Earn at least {gpa[1]} cumulative GPA across the five minor courses.",
        ),
        req(
            "overlap",
            "CS major overlap limit",
            "note",
            summary="CS BS and Coordinate CS majors may add this minor. Only CMPS 2200 may overlap; four additional non-overlapping courses totaling 12 credits are required. CS BS AI/Algorithms requirements cannot reuse minor courses.",
        ),
        req(
            "declaration",
            "Minor declaration approval",
            "note",
            summary="After prerequisite completion, submit a signed declaration form through the department for advisor and chair signatures, then to the Advising Office. The page's declaration paragraph calls it the computer science minor despite its AI heading; confirm form selection with the department.",
        ),
    ]
    year = re.search(r"(20\d\d-20\d\d) Edition", text(soup))
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence",
        "award_level": "minor",
        "program_kind": "minor",
        "catalog_year": year[1] if year else None,
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": requirements,
    }


from atlas.adapters.tulane_policies import NTC_URL, SSE_URL, parse_ntc, parse_sse

SOURCES += (NTC_URL, SSE_URL)


def parse_college(html):
    return parse_ntc(html, PROGRAM_ID)


def parse_school(html):
    return parse_sse(html, PROGRAM_ID)


SOURCE_PARSERS = {NTC_URL: parse_college, SSE_URL: parse_school}
