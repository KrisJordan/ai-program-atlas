"""Observe Lehigh's AI/ML/DS requirements while preserving published ambiguities."""

import re

from bs4 import BeautifulSoup

PROGRAM_ID = "lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree"
SOURCES = ("https://engineering.lehigh.edu/cse/academics/undergraduate/bs-ai-ml-ds",)
SOURCE_ID = PROGRAM_ID + "-official"


def text(n):
    return " ".join(n.get_text(" ", strip=True).split())


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if (
        "Bachelor of Science (BS) in Artificial Intelligence, Machine Learning, and Data Science"
        not in body
    ):
        raise ValueError("Expected Lehigh BS identity")
    labels = [
        "Degree Requirements table",
        "AI, ML, and DS Depth Approved Courses table",
        "Approved AI, ML, and DS Electives table",
    ]
    tables = [soup.find("table", attrs={"aria-label": label}) for label in labels]
    if any(t is None for t in tables):
        raise ValueError("Missing requirements or elective table")
    courses = {}
    reqs = []

    def req(label, kind="all", ids=(), credits=None, parent=None, summary=""):
        rid = PROGRAM_ID + "-r" + str(len(reqs) + 1)
        r = {
            "id": rid,
            "parent_id": parent,
            "title": label,
            "kind": kind,
            "count": None,
            "credits": credits,
            "credit_unit": "unknown",
            "category": "other",
            "source_id": SOURCE_ID,
            "source_text": None,
            "summary": summary,
            "course_ids": list(ids),
        }
        reqs.append(r)
        return r

    def course(code, name, credit):
        if not re.fullmatch(r"[A-Z]+ \d{3}", code):
            raise ValueError("Unexpected course code")
        cid = "lehigh-" + code.lower().replace(" ", "-")
        courses[cid] = {
            "id": cid,
            "code": code,
            "name": name,
            "description": None,
            "prerequisites": None,
            "credits": int(credit) if credit.isdigit() else None,
            "credit_unit": "unknown",
            "category": "mathematics"
            if code.startswith("MATH")
            else "ai_ml"
            if any(
                w in name.lower()
                for w in ["intelligence", "learning", "ai ", "vision", "language processing"]
            )
            else "human_context"
            if code.startswith(("COMM", "JOUR", "TLT"))
            else "foundations"
            if code.startswith("CSE")
            else "other",
            "source_id": SOURCE_ID,
            "url": SOURCES[0],
            "public_site": None,
            "syllabus": None,
        }
        return cid

    total = text(tables[0].find("tfoot")) if tables[0].find("tfoot") else ""
    if "130-131" not in total:
        raise ValueError("Degree credit range changed")
    root = req(
        "Published degree requirements",
        kind="note",
        summary="The degree table states a 130–131-credit minimum, while the page highlights 130. Degreewide policies and source discrepancies remain unresolved.",
    )
    section = root
    linear = None
    depth = None
    elect = None
    for row in tables[0].find("tbody").find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) == 1:
            section = req(text(cells[0]), parent=root["id"])
            continue
        if len(cells) == 2:
            label, credit = map(text, cells)
            if not credit.isdigit():
                raise ValueError("Unrecognized open requirement credits")
            r = req(
                label,
                kind="note",
                credits=int(credit),
                parent=section["id"],
                summary="Source-stated credit requirement; normalized credit unit and full applicable rules remain unverified.",
            )
            if label.startswith("AI, ML and DS Depth:"):
                depth = r
            elif label.startswith("AI, ML and DS Electives:"):
                elect = r
            continue
        if len(cells) != 3:
            raise ValueError("Unexpected requirement row shape")
        code, name, credit = map(text, cells)
        if code in ["ECO 001", "WRT 001", "WRT 002"]:
            expected = {
                "ECO 001": "Introduction to Engineering Practice",
                "WRT 001": "Applied Engineering Computer Methods",
                "WRT 002": "Introduction to Chemical Principles",
            }
            if name != expected[code]:
                raise ValueError("Previously ambiguous HSS title changed; review correction")
            req(
                code + " — course title unresolved",
                kind="note",
                credits=int(credit),
                parent=section["id"],
                summary="Required code and credits are source-stated. The displayed title repeats an engineering/chemistry title from an earlier row and is not accepted as verified course metadata.",
            )
            continue
        if code == "PHY 011 & PHY 012":
            names = name.split(" and ")
            if len(names) != 2:
                raise ValueError("Physics sequence names changed")
            ids = [course(c, n, "") for c, n in zip(code.split(" & "), names)]
            req(
                "Physics lecture and laboratory",
                ids=ids,
                credits=int(credit),
                parent=section["id"],
                summary="Five credits belong to the two-course group; individual credits remain null.",
            )
            continue
        if code == "MATH 205":
            if credit != "3-4":
                raise ValueError("Linear algebra group range changed")
            linear = req(
                "Linear algebra alternatives",
                "alternative",
                parent=section["id"],
                summary="MATH 205, MATH 241 or MATH 242; source group range 3–4 credits, not an individual course credit value.",
            )
            linear["course_ids"].append(course(code, name, ""))
            continue
        if code.startswith("or "):
            if linear is None:
                raise ValueError("Unexpected alternative row")
            linear["course_ids"].append(course(code.removeprefix("or ").strip(), name, ""))
            continue
        section["course_ids"].append(
            course(code, name.replace(" (Does not count toward HSS)", ""), credit)
        )
    if depth is None or elect is None:
        raise ValueError("Depth/general choice rules missing")
    for table, target in zip(tables[1:], [depth, elect]):
        for row in table.find("tbody").find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if len(cells) != 3:
                raise ValueError("Unexpected elective row shape")
            code, name, credit = map(text, cells)
            target["course_ids"].append(course(code, name, credit))
        if not target["course_ids"]:
            raise ValueError("Empty elective pool")
        target["summary"] = "Listed approved pool. " + (
            "At least "
            + str(target["credits"])
            + " credits; individual normalized credit units remain unverified."
        )
        if target is elect:
            target["summary"] += (
                " The source also permits CSE courses at level 100 or above; that open range is not expanded."
            )
    if "Does not count toward HSS" not in body:
        raise ValueError("Computing ethics HSS exclusion missing")
    req(
        "Computing ethics overlap exclusion",
        "note",
        parent=root["id"],
        summary="CSE 252 does not count toward the humanities/social-science requirement.",
    )
    return {
        "id": PROGRAM_ID,
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": reqs,
    }

from atlas.adapters.lehigh_degree_policies import SOURCE_PARSERS as POLICY_PARSERS
SOURCE_PARSERS = {SOURCES[0]: parse, **POLICY_PARSERS}
SOURCES = tuple(SOURCE_PARSERS)
