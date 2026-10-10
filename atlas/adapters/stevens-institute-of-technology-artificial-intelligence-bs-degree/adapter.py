"""Read Stevens AI BS overview and hydrated catalog plan; reject HTTP placeholders."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "stevens-institute-of-technology-artificial-intelligence-bs-degree"
CATALOG = "https://stevens.catalog.prod.coursedog.com/programs/qT6Ld1CzBAhQsVKYFNVv"
PLAN = CATALOG + "/academic-plan-JKlwr"
RULES = CATALOG + "/requirements-and-concentrations-n90Np"
SOURCES = (
    "https://www.stevens.edu/program/bachelors-degree-in-artificial-intelligence",
    PLAN,
    RULES,
    CATALOG,
)


def text(n):
    return " ".join(n.get_text(" ", strip=True).split())


def requirement(
    suffix,
    title,
    kind="note",
    ids=(),
    parent=None,
    credits=None,
    summary="",
    source="plan",
    count=None,
):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": parent,
        "title": title,
        "kind": kind,
        "count": count,
        "credits": credits,
        "credit_unit": "unknown",
        "category": "other",
        "source_id": PROGRAM_ID + "-" + source,
        "source_text": None,
        "summary": summary,
        "course_ids": list(ids),
    }


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if "Bachelor of Science in Artificial Intelligence" not in body or not soup.find(
        lambda n: n.name == "h1" and "Artificial Intelligence" in text(n)
    ):
        raise ValueError("Explicit AI BS identity missing")
    m = re.search(r"(two)-semester senior design capstone", body)
    if not m:
        raise ValueError("Two-semester capstone statement changed")
    return {
        "id": PROGRAM_ID,
        "award_level": "BS",
        "curriculum_status": "partial",
        "requirements": [
            requirement(
                "overview-capstone",
                "Senior design capstone",
                summary="The official overview states a two-semester senior design capstone applying AI to practical problems.",
                source="official",
            )
        ],
    }


def parse_plan(html):
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find(
        lambda n: n.name == "h1" and text(n) == "Bachelor of Science in Artificial Intelligence"
    ):
        raise ValueError("Expected catalog BS heading")
    panels = soup.find_all("div", id=re.compile(r"^Semester.*-panel$"))
    if len(panels) != 8:
        raise ValueError("Expected eight semester panels")
    courses = []
    rules = []
    totals = set()
    root = requirement(
        "plan-root",
        "Standard academic plan",
        "all",
        summary="Published semester plan; requirements and general university policies must also be applied.",
    )
    rules.append(root)
    for i, panel in enumerate(panels, 1):
        label = panel.find("label", string=lambda x: x and x.strip() == "Total Degree Credits")
        if label is None:
            raise ValueError("Degree total label missing")
        total = text(label.find_next_sibling())
        if not total.isdigit():
            raise ValueError("Degree total unresolved")
        totals.add(int(total))
        term = requirement("term-" + str(i), "Semester " + str(i), "all", parent=root["id"])
        rules.append(term)
        for j, li in enumerate(panel.find_all("li"), 1):
            raw = text(li)
            anchors = li.find_all("a", href=re.compile(r"/courses/"))
            if not anchors:
                if "undefined" in raw or raw.strip("- ") == "":
                    raise ValueError("Unhydrated catalog placeholder")
                rules.append(
                    requirement(
                        f"slot-{i}-{j}",
                        raw,
                        parent=term["id"],
                        summary="Published open plan slot; see the separate program requirement policies.",
                    )
                )
                continue
            matches = re.findall(r"([A-Z]+ \d+)\s*-\s*(.*?)\s*\((\d+) cr\)", raw)
            if len(matches) != len(anchors):
                raise ValueError("Unhydrated or changed catalog course row")
            ids = []
            for (code, name, credit), a in zip(matches, anchors):
                if text(a) != code:
                    raise ValueError("Unhydrated course code")
                cid = "stevens-" + code.lower().replace(" ", "-")
                ids.append(cid)
                courses.append(
                    {
                        "id": cid,
                        "code": code,
                        "name": name,
                        "description": None,
                        "prerequisites": None,
                        "credits": int(credit),
                        "credit_unit": "unknown",
                        "category": "mathematics"
                        if code.startswith("MA ")
                        else "human_context"
                        if code.startswith(("HASS", "HST", "HSSC", "HPL"))
                        else "ai_ml"
                        if any(w in name.lower() for w in ["intelligence", "learning", " ai"])
                        else "foundations"
                        if code.startswith("CS ")
                        else "other",
                        "source_id": PROGRAM_ID + "-plan",
                        "url": urljoin(PLAN, a["href"]),
                        "public_site": None,
                        "syllabus": None,
                    }
                )
            if len(ids) > 1:
                if " OR " not in raw:
                    raise ValueError("Course alternatives marker missing")
                rules.append(
                    requirement(
                        f"alt-{i}-{j}",
                        "Human-context course alternatives",
                        "alternative",
                        ids,
                        parent=term["id"],
                        summary="Choose one source-listed alternative.",
                    )
                )
            else:
                term["course_ids"] += ids
    if totals != {125}:
        raise ValueError("Degree total changed or unhydrated (expected 125)")
    if len(courses) != len({c["id"] for c in courses}):
        raise ValueError("Duplicate plan course")
    root["credits"] = 125
    return {
        "id": PROGRAM_ID,
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": rules,
    }


def parse_rules(html):
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if not soup.find(
        lambda n: n.name == "h1" and text(n) == "Bachelor of Science in Artificial Intelligence"
    ):
        raise ValueError("Expected catalog BS heading")
    if any(text(a) == "course" for a in soup.find_all("a", attrs={"data-course-id": True})):
        raise ValueError("Unhydrated catalog course references; browser rendering required")
    rules = []
    for sid, title, pattern in [
        ("technical", "Technical Electives", r"complete (\d+) Technical electives"),
        ("general", "General Electives", r"complete (\d+) General Electives"),
    ]:
        h = soup.find(lambda n, title=title: n.name == "button" and text(n) == title)
        panel = soup.find(id=h.get("aria-controls")) if h else None
        if panel is None:
            raise ValueError("Expected requirement panel: " + title)
        value = text(panel)
        match = re.search(pattern, value)
        if match is None or "prior approval" not in value:
            raise ValueError("Elective count or advising rule changed")
        links = [text(a) for a in panel.find_all("a", attrs={"data-course-id": True})]
        summary = "Complete " + match[1] + " courses; prior academic-advisor approval required. "
        if sid == "technical":
            summary += (
                "Listed options: "
                + ", ".join(links)
                + ". Detailed course titles/credits and undergraduate access remain unverified."
            )
        else:
            summary += "Use courses carrying at least three credits; required or equivalent coursework is excluded. Additional prohibited courses and overlapping pairs need the full published rule."
        rules.append(
            requirement(
                "policy-" + sid,
                title,
                "choose_courses",
                count=int(match[1]),
                summary=summary,
                source="rules",
            )
        )
    if "two science courses and a science laboratory" not in body:
        raise ValueError("Science sequence structure changed")
    rules.append(
        requirement(
            "policy-science",
            "Science sequence",
            summary="Complete two science courses and a science laboratory using one published sequence. The six permitted pathways and laboratory alternatives require the source table.",
            source="rules",
        )
    )
    return {"id": PROGRAM_ID, "curriculum_status": "partial", "requirements": rules}


SOURCE_PARSERS = {SOURCES[0]: parse, PLAN: parse_plan, RULES: parse_rules}
