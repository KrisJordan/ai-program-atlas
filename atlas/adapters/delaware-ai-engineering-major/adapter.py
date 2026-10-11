"""Observe the department's explicitly labeled sample AI Engineering BS plan."""

import re

from bs4 import BeautifulSoup

PROGRAM_ID = "delaware-ai-engineering-major"
SOURCES = (
    "https://www.ece.udel.edu/academics/undergraduate/artificial-intelligence-engineering-bs/",
)
SOURCE_ID = PROGRAM_ID + "-department"


def text(n):
    return " ".join(n.get_text(" ", strip=True).split())


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    for n in soup.find_all(["nav", "header", "footer", "aside"]):
        n.decompose()
    if not soup.find(
        lambda n: n.name == "h1" and text(n) == "Artificial Intelligence Engineering BS"
    ):
        raise ValueError("Explicit department BS heading missing")
    if not soup.find(lambda n: n.name == "h2" and text(n) == "Sample Plan of Study"):
        raise ValueError("Sample plan heading missing")
    courses = []
    requirements = []

    def req(title, kind="note", parent=None, ids=(), summary=""):
        r = {
            "id": PROGRAM_ID + "-r" + str(len(requirements) + 1),
            "parent_id": parent,
            "title": title,
            "kind": kind,
            "count": None,
            "credits": None,
            "credit_unit": "unknown",
            "category": "other",
            "source_id": SOURCE_ID,
            "source_text": None,
            "summary": summary,
            "course_ids": list(ids),
        }
        requirements.append(r)
        return r

    root = req(
        "Published sample plan",
        summary="Illustrative department study plan, not a fully verified graduation requirement inventory. The source directs students to the current catalog and states courses may change.",
    )
    for year in ["First Year", "Second Year", "Third Year", "Fourth Year"]:
        h = soup.find(lambda n, year=year: n.name == "h5" and text(n) == year)
        if h is None:
            raise ValueError("Sample year section missing")
        box = h.find_parent(class_="et_pb_toggle")
        if box is None:
            raise ValueError("Sample year container missing")
        group = req(
            year + " sample courses",
            parent=root["id"],
            summary="Sample placement only; no prerequisite or regular offering is inferred.",
        )
        for li in box.find_all("li"):
            value = text(li)
            m = re.fullmatch(r"([A-Z]+) (\d+(?: (?:or|&) \d+)?)\s*[–-]\s*(.+)", value)
            if not m:
                req(
                    value,
                    parent=group["id"],
                    summary="Open sample-plan slot; credit amount, option pool and applicable rules remain unverified.",
                )
                continue
            subject, numbers, names = m.groups()
            if " & " in numbers:
                req(
                    subject + " " + numbers,
                    parent=group["id"],
                    summary="Source groups "
                    + subject
                    + " "
                    + numbers
                    + " as "
                    + names
                    + ". Separate titles and individual credits are not supplied.",
                )
                continue
            codes = [subject + " " + n for n in numbers.split(" or ")]
            titles = names.split(" or ") if len(codes) > 1 else [names]
            if len(codes) != len(titles):
                raise ValueError("Sample alternative title mismatch")
            ids = []
            for code, name in zip(codes, titles):
                cid = "delaware-" + code.lower().replace(" ", "-")
                ids.append(cid)
                courses.append(
                    {
                        "id": cid,
                        "code": code,
                        "name": name,
                        "description": None,
                        "prerequisites": None,
                        "credits": None,
                        "credit_unit": "unknown",
                        "category": "ai_ml"
                        if any(
                            w in name.lower() for w in ["intelligence", "learning", "data mining"]
                        )
                        else "mathematics"
                        if subject == "MATH"
                        else "human_context"
                        if subject == "ENGL" or "Ethics" in name
                        else "foundations"
                        if subject == "CISC"
                        else "other",
                        "source_id": SOURCE_ID,
                        "url": SOURCES[0],
                        "public_site": None,
                        "syllabus": None,
                    }
                )
            if len(ids) > 1:
                req(
                    "Sample course alternatives",
                    "alternative",
                    group["id"],
                    ids,
                    summary="The sample plan gives these alternatives; eligibility and graduate-level access rules require catalog confirmation.",
                )
            else:
                group["course_ids"] += ids
    if len({c["id"] for c in courses}) != len(courses) or not courses:
        raise ValueError("Missing or duplicate sample courses")
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence Engineering",
        "award_level": "BS",
        "program_kind": "degree",
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": requirements,
    }

from atlas.adapters.delaware_ai_policies import SOURCE_PARSERS as POLICY_PARSERS
SOURCE_PARSERS={SOURCES[0]:parse,**POLICY_PARSERS}
SOURCES=tuple(dict.fromkeys([*SOURCES,*POLICY_PARSERS]))
