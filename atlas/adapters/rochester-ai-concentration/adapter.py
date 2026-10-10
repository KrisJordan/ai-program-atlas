"""Observe Rochester's optional AI concentration and minimum-area course rule."""

import re

from bs4 import BeautifulSoup

PROGRAM_ID = "rochester-ai-concentration"
SOURCES = ("https://www.cs.rochester.edu/undergraduate/bs-requirements.html",)
SOURCE_ID = PROGRAM_ID + "-official"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def req(suffix, title, kind, ids=(), count=None, summary=""):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": None if suffix == "total" else PROGRAM_ID + "-total",
        "title": title,
        "kind": kind,
        "count": count,
        "credits": None,
        "credit_unit": "unknown",
        "category": "ai_ml",
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
        "course_ids": list(ids),
    }


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    if not any(text(h) == "BS in Computer Science" for h in soup.find_all(["h1", "h2"])):
        raise ValueError("Expected Rochester CS BS heading")
    area = soup.find("details", id="artificial-intelligence")
    if area is None or "Approved courses for AI concentration:" not in text(area):
        raise ValueError("AI concentration list missing")
    body = text(soup)
    guards = [
        "five advanced four-credit courses numbered 200 or higher",
        "at least three of these courses in the chosen concentration area",
        "BS students can complete a concentration",
        "does not include core or math courses listed above",
        "No more than two core or major electives may be completed at other institutions unless they are taken as part of the University",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Concentration count, parent or exclusions changed")
    label = next(
        p for p in area.find_all("p") if text(p) == "Approved courses for AI concentration:"
    )
    listing = label.find_next_sibling("ul")
    if listing is None:
        raise ValueError("AI approved course list missing")
    courses = []
    for li in listing.find_all("li", recursive=False):
        m = re.fullmatch(r"(CSC \d{3}): (.+)", text(li))
        if m is None:
            raise ValueError("Unrecognized approved AI course")
        code, name = m.groups()
        courses.append(
            {
                "id": "rochester-" + code.lower().replace(" ", "-"),
                "code": code,
                "name": name,
                "description": None,
                "prerequisites": None,
                "credits": None,
                "credit_unit": "unknown",
                "category": "ai_ml",
                "source_id": SOURCE_ID,
                "url": SOURCES[0] + "#artificial-intelligence",
                "public_site": None,
                "syllabus": None,
            }
        )
    if not courses or len(courses) != len({c["id"] for c in courses}):
        raise ValueError("Empty or duplicate AI course list")
    ids = [c["id"] for c in courses]
    requirements = [
        req(
            "total",
            "Five advanced courses for the concentration",
            "all",
            count=5,
            summary="Five distinct four-credit advanced CS courses numbered 200 or higher; one more course than the base BS requires.",
        ),
        req(
            "ai-minimum",
            "At least three AI-area courses",
            "choose_courses",
            ids,
            count=3,
            summary="At least three of the five courses must be in the approved AI area. Additional unused AI-area courses may fill the remaining two positions.",
        ),
        req(
            "remaining",
            "Two remaining advanced-course positions",
            "choose_courses",
            count=2,
            summary="Two additional eligible four-credit advanced CS courses numbered 200 or higher, including unused AI-area choices. This is an open course-number rule, not a missing finite approved list.",
        ),
        req(
            "exclusions",
            "Core and math exclusions",
            "note",
            summary="Advanced-course choices exclude the parent program core and additional math courses listed on the same source page.",
        ),
        req(
            "relationship",
            "Optional concentration within CS BS",
            "note",
            summary="This is an optional concentration for BS Computer Science students; it does not constitute a standalone AI degree.",
        ),
    ]
    requirements.append(
        req(
            "transfer-limit",
            "Limit on outside core/major electives",
            "note",
            summary="No more than two core or major electives may be completed at other institutions, except through the University's education-abroad program.",
        )
    )
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence",
        "award_level": "concentration",
        "program_kind": "concentration",
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
    }


POLICY_URL = "https://www.cs.rochester.edu/undergraduate/advising.html"
POLICY_ID = PROGRAM_ID + "-advising"
SOURCES += (POLICY_URL,)


def parse_advising(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if any(
        g not in body
        for g in [
            "All transfer courses used to fulfill computer science major requirements must be approved by the corresponding department",
            "To update your official CS course plan, discuss the changes with your CS undergraduate coordinator",
        ]
    ):
        raise ValueError("Rochester transfer/plan rules missing")
    rows = [
        req(
            "transfer-approval",
            "Approval of transfer coursework",
            "note",
            summary="Transfer courses used for CS major requirements require approval from the corresponding department; submit course approval materials and syllabi for CS evaluation.",
        ),
        req(
            "plan-changes",
            "Changes to the CS course plan",
            "note",
            summary="Discuss changes to the official CS course plan with the CS undergraduate coordinator.",
        ),
    ]
    for r in rows:
        r["source_id"] = POLICY_ID
        r["parent_id"] = None
    return {"id": PROGRAM_ID, "requirements": rows}


SOURCE_PARSERS = {POLICY_URL: parse_advising}
