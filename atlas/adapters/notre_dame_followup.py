"""Rerunnable observations of ND's differing catalog and college-policy sources."""

import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from atlas.adapters.business_society_minors import course, requirement, clean

CATALOG_URL = "https://catalog.nd.edu/undergraduate/business/-analytics-operations/ai-analytics-in-business/index.html"
COLLEGE_URL = "https://catalog.nd.edu/undergraduate/business/"


def text(n):
    return clean(n.get_text(" ", strip=True))


def parse_catalog(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    h = soup.find("h1")
    if h is None or text(h) != "AI Analytics in Business":
        raise ValueError("ND catalog program heading changed")
    tables = soup.find_all("table", class_="sc_courselist")
    if len(tables) != 1:
        raise ValueError("ND catalog requirement table inventory changed")
    source = pid + "-catalog"
    courses = []
    groups = []
    current = None
    for row in tables[0].find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        first = text(cells[0])
        number = text(cells[-1])
        if "areaheader" in row.get("class", []):
            if first == "Core Courses":
                suffix = "core"
                summary = "Catalog core-course observation; compare with the current Mendoza page before adopting a changed inventory."
            else:
                m = re.fullmatch(
                    r"AI & Analytics Core Electives \(choose (\d+) credits from ITAO\):", first
                )
                if not m:
                    raise ValueError("Catalog ITAO elective restriction changed shape")
                suffix = "electives"
                summary = (
                    "Catalog elective observation: "
                    + m[1]
                    + " credits from ITAO within the listed elective block. The current program page differs; this is not an automatically merged approved pool."
                )
            if not number.isdigit():
                raise ValueError("Catalog group hours missing")
            current = requirement(
                pid,
                "catalog-observed-" + suffix,
                first,
                source,
                [],
                kind="note",
                credits=int(number),
                summary=summary,
            )
            groups.append(current)
        elif row.find("a", class_="code"):
            if current is None:
                raise ValueError("Catalog course outside a group")
            a = row.find("a", class_="code")
            code = text(a)
            if not re.fullmatch(r"[A-Z]+ \d{5}", code):
                raise ValueError("Catalog course code changed")
            amount = float(number) if re.fullmatch(r"\d+(?:\.\d+)?", number) else None
            c = course(code, text(cells[1]), pid, source, urljoin(CATALOG_URL, a["href"]), amount)
            courses.append(c)
            current["course_ids"].append(c["id"])
        elif "Total Hours" in first:
            if not number.isdigit():
                raise ValueError("Catalog total changed")
            groups.append(
                requirement(
                    pid,
                    "catalog-observed-total",
                    "Catalog total observation",
                    source,
                    [],
                    kind="note",
                    credits=int(number),
                    summary="Source-specific total; not an additional block to add to the primary curriculum.",
                )
            )
    if len(groups) != 3 or not all(g["course_ids"] for g in groups[:2]):
        raise ValueError("ND catalog group inventory incomplete")
    return dict(id=pid, curriculum_status="partial", courses=courses, requirements=groups)


def parse_college(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    paragraph = next((p for p in soup.find_all("p") if text(p).startswith("Pass-Fail.")), None)
    if paragraph is None:
        raise ValueError("Mendoza Pass-Fail paragraph missing")
    value = text(paragraph)
    required = [
        "permission from their academic advisor",
        "approval of the assistant dean",
        "juniors and seniors",
        "Only non-business elective courses",
        "other than the first course taken in a minor track",
        "first six days",
        "irrevocable",
    ]
    if any(t not in value for t in required):
        raise ValueError("Mendoza grading policy changed")
    r = requirement(
        pid,
        "college-pass-fail-observation",
        "Mendoza pass-fail wording — applicability unresolved",
        pid + "-college-policy",
        [],
        kind="note",
        summary="The BBA paragraph permits juniors/seniors one non-business elective per term with academic-adviser permission and assistant-dean approval, selected in the first six days and irrevocable. It excludes business/required/second-major/minor courses but parenthetically excepts a first minor-track course. This source-specific observation does not override the university code or grant an AI-minor exception, especially for students outside Mendoza.",
    )
    return dict(id=pid, curriculum_status="partial", courses=[], requirements=[r])


def inspect_additional_electives(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    button = next(
        (
            b
            for b in soup.find_all("button")
            if text(b) == "Additional approved electives across Notre Dame"
        ),
        None,
    )
    if button is None:
        raise ValueError("Additional approved-electives control missing")
    block = button.find_parent(class_="accordion")
    content = block.find(class_="accordion__content") if block else None
    if content is None:
        raise ValueError("Additional approved-electives content container missing")
    if text(content) or content.find(["a", "iframe", "object", "embed"]):
        raise ValueError("Additional elective content is now present; inventory requires review")
    return requirement(
        pid,
        "additional-pool-observation",
        "Additional approved-elective section is empty",
        pid + "-curriculum",
        [],
        kind="note",
        summary="The public additional-approved-electives accordion contains an empty content container. No finite additional pool or approval rule can be verified from this section; it is not evidence that no additional electives exist.",
    )
