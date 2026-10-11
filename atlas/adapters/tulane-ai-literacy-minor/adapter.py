"""Observe the separate Newcomb-Tulane AI Literacy minor, not the technical minor."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from atlas.adapters.tulane_policies import NTC_URL, SSE_URL, note, parse_ntc, parse_sse, text

PROGRAM_ID = "tulane-ai-literacy-minor"
URL = "https://catalog.tulane.edu/newcomb-tulane/ai-literacy-minor/"
SOURCES = (URL, NTC_URL, SSE_URL)
SOURCE_ID = PROGRAM_ID + "-catalog"


def key(code):
    return re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-")


def req(suffix, title, kind, ids=(), parent="total", count=None, credits=None, summary=""):
    row = note(PROGRAM_ID, suffix, title, summary, "catalog")
    row.update(
        kind=kind,
        parent_id=PROGRAM_ID + "-" + parent if parent else None,
        count=count,
        credits=credits,
        course_ids=list(ids),
    )
    return row


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    if not any(
        text(h) == "Artificial Intelligence (AI) Literacy Minor" for h in soup.find_all("h1")
    ):
        raise ValueError("AI Literacy minor heading missing")
    content = soup.find(id="requirementstextcontainer")
    if content is None:
        raise ValueError("Literacy requirements missing")
    body = text(content)
    total = re.search(r"requires (\d+) credit hours.*?minimum (\d+\.\d+) grade point average", body)
    if (
        total is None
        or "Only three credit hours" not in body
        or "minor and a certificate" not in body
    ):
        raise ValueError("Literacy total, GPA or overlap changed")
    table = content.find("table", class_="sc_courselist")
    if table is None:
        raise ValueError("Literacy course table missing")
    groups, courses = [], []
    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells or "listsum" in row.get("class", []):
            continue
        if "areaheader" in row.get("class", []):
            title = text(row.find(class_="courselistcomment"))
            credit = text(row.find(class_="hourscol"))
            sup = text(row.find("sup")) if row.find("sup") else ""
            count = re.search(r"(?:^(\d+) course|Choose \w+ \((\d+)\))", sup)
            if not credit.isdigit() or count is None:
                raise ValueError("Literacy group count or credits missing")
            groups.append(
                {
                    "title": title,
                    "credits": int(credit),
                    "count": int(count[1] or count[2]),
                    "options": [],
                    "approval": False,
                }
            )
            continue
        if not groups:
            raise ValueError("Course outside literacy group")
        link = row.find("a", class_="code")
        if link is None:
            if "equivalent" in text(
                row
            ) and "approval of the AI Literacy Minor Faculty Steering Committee" in text(row):
                groups[-1]["approval"] = True
                continue
            raise ValueError("Unrecognized literacy option")
        code = text(link)
        if not re.fullmatch(r"[A-Z]+ \d{4}", code):
            raise ValueError("Literacy course code changed")
        amount = text(row.find(class_="hourscol")) if row.find(class_="hourscol") else ""
        if amount and not amount.isdigit():
            raise ValueError("Unrecognized literacy credit amount")
        cid = "tulane-" + key(code)
        courses.append(
            {
                "id": cid,
                "code": code,
                "name": text(cells[1]),
                "credits": int(amount) if amount else None,
                "credit_unit": "unknown",
                "description": None,
                "prerequisites": None,
                "category": "human_context" if len(groups) == 2 else "ai_ml",
                "source_id": SOURCE_ID,
                "url": urljoin(URL, link["href"]),
                "public_site": None,
                "syllabus": None,
            }
        )
        if "orclass" in row.get("class", []):
            if not groups[-1]["options"]:
                raise ValueError("Orphan literacy alternative")
            groups[-1]["options"][-1].append(cid)
        else:
            groups[-1]["options"].append([cid])
    if [g["title"] for g in groups] != [
        "Foundational Requirement",
        "AI and Society Electives",
        "Problem Solving with AI Electives",
    ]:
        raise ValueError("Literacy group structure changed")
    if not all(g["approval"] for g in groups[1:]):
        raise ValueError("Literacy committee-approved option missing")
    rows = [req("total", "Published minor credit total", "all", credits=int(total[1]), parent=None)]
    for suffix, group in zip(["foundation", "society", "problem-solving"], groups):
        rows.append(
            req(
                suffix,
                group["title"],
                "all" if suffix == "foundation" else "choose_courses",
                count=group["count"],
                credits=group["credits"],
                summary="Choose distinct options; an OR pair is a single option.",
            )
        )
        for i, ids in enumerate(group["options"]):
            rows.append(
                req(
                    f"{suffix}-option-{i}",
                    "Course option " + str(i + 1),
                    "alternative" if len(ids) > 1 else "all",
                    ids,
                    parent=suffix,
                    count=1,
                )
            )
        if group["approval"]:
            rows.append(
                req(
                    suffix + "-approved",
                    "Committee-approved equivalent option",
                    "note",
                    parent=suffix,
                    summary="Equivalent courses, including special topics, require AI Literacy Minor Faculty Steering Committee approval.",
                )
            )
    rows += [
        req("gpa", "Minor GPA", "note", summary=f"Earn a minor GPA of at least {total[2]}."),
        req(
            "overlap",
            "Major, minor and certificate overlap",
            "note",
            summary="At most three minor credits may overlap a major. No credit may overlap another minor or a certificate.",
        ),
    ]
    year = re.search(r"20\d\d-20\d\d", text(soup))
    return {
        "id": PROGRAM_ID,
        "title": "Artificial Intelligence (AI) Literacy",
        "award_level": "minor",
        "program_kind": "minor",
        "catalog_year": year[0] if year else None,
        "curriculum_status": "partial",
        "courses": courses,
        "requirements": rows,
    }


def parse_college(html):
    return parse_ntc(html, PROGRAM_ID)


def parse_school(html):
    # Only the SSE-degree overlap rule applies to SSE students taking this NTC minor.
    result = parse_sse(html, PROGRAM_ID)
    result["requirements"] = [
        r for r in result["requirements"] if r["id"].endswith("-school-overlap")
    ]
    return result


SOURCE_PARSERS = {NTC_URL: parse_college, SSE_URL: parse_school}

from atlas.adapters.tulane_literacy_policy_followup import DECLARATION,UNIVERSITY,parse_declaration,parse_university
SOURCES=(*SOURCES,DECLARATION,UNIVERSITY)
SOURCE_PARSERS[DECLARATION]=lambda html:parse_declaration(html,PROGRAM_ID)
SOURCE_PARSERS[UNIVERSITY]=lambda html:parse_university(html,PROGRAM_ID)

from atlas.adapters.tulane_home_policies import register as register_home
SOURCES=list(SOURCES)
register_home(PROGRAM_ID,SOURCES,SOURCE_PARSERS)
