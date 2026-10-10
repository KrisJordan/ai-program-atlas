"""Observe the College AI minor; preserve ambiguous source rows for review."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "columbia-ai-minor"
SOURCES = (
    "https://bulletin.columbia.edu/columbia-college/departments-instruction/computer-science/",
)
SOURCE_ID = PROGRAM_ID + "-identity"


def text(node):
    return " ".join(node.get_text(" ", strip=True).replace("\u200b", "").split())


def key(value):
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def requirement(suffix, title, kind, ids=(), count=None, parent=None, summary=""):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": parent,
        "title": title,
        "kind": kind,
        "count": count,
        "credits": None,
        "credit_unit": "unknown",
        "category": "other",
        "source_id": SOURCE_ID,
        "source_text": None,
        "summary": summary,
        "course_ids": list(ids),
    }


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    heading = next(
        (h for h in soup.find_all("h3") if text(h) == "Minor in Artificial Intelligence"), None
    )
    if heading is None:
        raise ValueError("AI minor section missing")
    nodes = []
    for node in heading.find_next_siblings():
        if node.name in {"h2", "h3"}:
            break
        nodes.append(node)
    section_text = " ".join(text(n) for n in nodes)
    total = re.search(r"consists of (\d+) courses", section_text)
    if (
        total is None
        or "are not eligible" not in section_text
        or "solely or jointly" not in section_text
    ):
        raise ValueError("Minor count or eligibility rules missing")
    headings = [text(n) for n in nodes if n.name == "h4"]
    if headings != ["AI Requirement:", "Ethics Requirement:", "AI Elective:"]:
        raise ValueError("Minor subsection inventory changed")
    tables = [n for n in nodes if n.name == "table"]
    if len(tables) != 4:
        raise ValueError("Expected four minor tables")
    requirements = [
        requirement(
            "total",
            "Published minor course count",
            "all",
            count=int(total[1]),
            summary="Published course count; foundation-table duplication requires advising clarification before completion can be certified.",
        )
    ]
    courses = {}
    parsed = []
    for table_index, table in enumerate(tables):
        rows, comments = [], []
        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if not cells:
                continue
            code_cell = row.find("td", class_="codecol")
            if code_cell is None:
                comments.append(text(row))
                continue
            code = re.sub(r"^or\s+", "", text(code_cell))
            if not re.fullmatch(r"[A-Z]+ [A-Z]+\d{4}", code):
                raise ValueError("Unknown minor course code")
            cid = "columbia-" + key(code)
            link = code_cell.find("a", href=True)
            title = text(cells[1]) if len(cells) > 1 else ""
            hours = row.find("td", class_="hourscol")
            credit = text(hours) if hours else ""
            if credit and not re.fullmatch(r"\d+(?:\.\d+)?", credit):
                raise ValueError("Unrecognized points value")
            courses[cid] = {
                "id": cid,
                "code": code,
                "name": title or code + " (title not supplied)",
                "description": None,
                "prerequisites": None,
                "credits": float(credit) if credit else None,
                "credit_unit": "unknown",
                "category": "foundations"
                if table_index == 0
                else "human_context"
                if table_index == 2
                else "ai_ml",
                "source_id": SOURCE_ID,
                "url": urljoin(SOURCES[0], link["href"]) if link else SOURCES[0],
                "public_site": None,
                "syllabus": None,
            }
            rows.append((cid, "orclass" in row.get("class", [])))
        parsed.append((rows, comments))
    # A repeated standalone foundation row is not silently a seventh course.
    groups, duplicates, seen = [], [], set()
    for cid, is_or in parsed[0][0]:
        if is_or:
            if not groups:
                raise ValueError("Orphan OR row")
            groups[-1].append(cid)
        elif cid in seen:
            duplicates.append(cid)
        else:
            groups.append([cid])
        seen.add(cid)
    if not groups or groups[0] != ["columbia-math-un2015"]:
        raise ValueError("Mathematics foundation changed")
    for index, ids in enumerate(groups):
        requirements.append(
            requirement(
                "foundation-" + str(index),
                "Foundation requirement " + str(index + 1),
                "alternative" if len(ids) > 1 else "all",
                ids,
                count=1 if len(ids) > 1 else None,
                parent=PROGRAM_ID + "-total",
            )
        )
    if duplicates:
        requirements.append(
            requirement(
                "duplicate-source-row",
                "Repeated foundation row — unresolved",
                "note",
                duplicates,
                parent=PROGRAM_ID + "-total",
                summary="The same course appears as an OR option and a later standalone row. Preserve this ambiguity; do not count the repeated row as an extra completed course.",
            )
        )
    for index, suffix, title in [
        (1, "ai", "AI requirement"),
        (2, "ethics", "Ethics choice"),
        (3, "elective", "AI elective"),
    ]:
        rows, comments = parsed[index]
        if index > 1 and not any(c.lower() == "choose one:" for c in comments):
            raise ValueError("Choice rule changed")
        requirements.append(
            requirement(
                suffix,
                title,
                "all" if index == 1 else "choose_courses",
                [cid for cid, _ in rows],
                count=None if index == 1 else 1,
                parent=PROGRAM_ID + "-total",
            )
        )
        if index == 3:
            patterns = [c for c in comments if c.lower() != "choose one:"]
            if (
                len(patterns) != 2
                or not any("47XX" in c for c in patterns)
                or not any("4995/6998" in c for c in patterns)
            ):
                raise ValueError("Broad elective rule changed")
            requirements.append(
                requirement(
                    "broad-electives",
                    "Additional COMS elective routes",
                    "note",
                    parent=PROGRAM_ID + "-elective",
                    summary="The elective may also be any COMS 47XX course or a relevant COMS 4995/6998 offering. The source does not define relevant or resolve overlap with the AI requirement.",
                )
            )
    if (
        "separate linear algebra course" not in section_text
        or "separate probability course" not in section_text
    ):
        raise ValueError("Mathematics substitution changed")
    requirements.append(
        requirement(
            "math-substitution",
            "Mathematics substitution",
            "note",
            parent=PROGRAM_ID + "-foundation-0",
            summary="MATH UN2015 may be replaced by separate linear algebra and probability courses, following the CS Core. Detailed approved combinations await review.",
        )
    )
    requirements.append(
        requirement(
            "eligibility",
            "CS-program exclusion",
            "note",
            parent=PROGRAM_ID + "-total",
            summary="Students pursuing a major or minor offered solely or jointly by the CS department are ineligible, including CS, Information Science, Data Science, CS and Mathematics, and Computational Biology.",
        )
    )
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence",
        "award_level": "minor",
        "program_kind": "minor",
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": requirements,
    }
