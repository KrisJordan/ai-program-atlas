"""Parse the Drexel degree table, preserving alternatives, sequences and open ranges."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

PROGRAM_ID = "drexel-ai-ml-bs"
SOURCES = (
    "https://catalog.drexel.edu/undergraduate/computer-information-sciences/artificialintellicenceandmachinelearningbs/",
)
SOURCE_ID = PROGRAM_ID + "-identity"


def text(n):
    return " ".join(n.get_text(" ", strip=True).split())


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.find_all(["nav", "header", "footer", "aside", "script", "style"]):
        node.decompose()
    h = soup.find("h1")
    panel = soup.find(id="degreerequirementstextcontainer")
    if h is None or text(h) != "Artificial Intelligence & Machine Learning" or panel is None:
        raise ValueError("Expected Drexel AI/ML degree panel")
    if "Degree Awarded: Bachelor of Science (BS)" not in text(soup):
        raise ValueError("Explicit BS award missing")
    table = panel.find("table", class_="sc_courselist")
    if table is None:
        raise ValueError("Degree table missing")
    for sup in table.find_all("sup"):
        sup.decompose()
    reqs = []
    courses = {}
    section = None
    target = None
    previous = None

    def req(title, kind="all", parent=None, ids=(), credit=None, summary="", count=None):
        r = {
            "id": PROGRAM_ID + "-r" + str(len(reqs) + 1),
            "parent_id": parent,
            "title": title,
            "kind": kind,
            "count": count,
            "credits": credit,
            "credit_unit": "unknown",
            "category": "other",
            "source_id": SOURCE_ID,
            "source_text": None,
            "summary": summary,
            "course_ids": list(ids),
        }
        reqs.append(r)
        return r

    root = req(
        "Degree requirements",
        summary="Main catalog requirements. Open course ranges and university-wide policies remain under review.",
    )
    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        classes = row.get("class", [])
        value = text(cells[0])
        hours = row.find("td", class_="hourscol")
        raw = text(hours) if hours else ""
        credit = float(raw) if re.fullmatch(r"\d+(\.\d+)?", raw) else None
        if raw and credit is None and not re.fullmatch(r"\d+\.\d+-\d+\.\d+", raw):
            raise ValueError("Unrecognized credit value")
        if "areaheader" in classes:
            section = req(value, parent=root["id"])
            target = section
            previous = None
            continue
        if value == "Total Credits":
            root["credits"] = credit
            continue
        codecell = row.find("td", class_="codecol")
        if codecell is None:
            if value.startswith("Select 8 courses"):
                if (
                    "each course may count separately" not in value
                    or "not already used" not in value
                ):
                    raise ValueError("Elective sequence counting policy changed")
                target = req(
                    "AI/ML electives",
                    "choose_courses",
                    section["id"],
                    credit=credit,
                    count=8,
                    summary="Choose eight courses. Sequence components count individually only when not used for another degree requirement. Sequence groupings and alternative choices are preserved below.",
                )
                previous = None
            elif value in [
                "Select one of the following sequences:",
                "Choose one of the following sequences:",
            ]:
                target = req(
                    section["title"] + " sequence choice",
                    "alternative",
                    section["id"],
                    credit=credit,
                    summary="Choose one complete sequence; source credit value " + raw + ".",
                )
                previous = None
            elif value.startswith(("Select from the following 100-400", "Select any unrestricted")):
                target = req(
                    section["title"] + " open range",
                    "note",
                    section["id"],
                    credit=credit,
                    summary=value
                    + "; published credit amount "
                    + raw
                    + ". Approved inventory remains unexpanded.",
                )
                previous = None
            elif value.startswith("Any "):
                req(
                    value,
                    "note",
                    target["id"],
                    summary="Eligible science subject within the 100–400-level selection rule. Individual courses and restrictions remain unexpanded.",
                )
            else:
                raise ValueError("Unrecognized non-course rule: " + value)
            continue
        if section is None:
            raise ValueError("Course before section")
        codes = re.findall(r"\b[A-Z]+ (?:[A-Z]+)?\d+\b", text(codecell))
        names = [
            re.sub(r"^and\s+", "", x).strip() for x in cells[1].get_text("|", strip=True).split("|")
        ]
        names = [x for x in names if x not in ["*", "**"]]
        # A source row lacks ECEC 455's linked title; preserve code as a policy gap, not an invented course name.
        if not codes or len(codes) != len(names):
            raise ValueError("Course sequence/title shape changed")
        ids = []
        missing = []
        for code, name in zip(codes, names):
            if not name or name == "and":
                missing.append(code)
                continue
            cid = "drexel-" + code.lower().replace(" ", "-")
            ids.append(cid)
            anchor = codecell.find("a", string=lambda s, code=code: s and " ".join(s.split()) == code)
            ccredit = credit if len(codes) == 1 else None
            if cid not in courses:
                courses[cid] = {
                    "id": cid,
                    "code": code,
                    "name": name,
                    "description": None,
                    "prerequisites": None,
                    "credits": ccredit,
                    "credit_unit": "unknown",
                    "category": "mathematics"
                    if code.startswith("MATH")
                    else "ai_ml"
                    if any(
                        w in name.lower()
                        for w in ["intelligence", "learning", "neural", "vision", "recognition"]
                    )
                    else "human_context"
                    if code.startswith(("ENGL", "COM", "PHIL"))
                    else "foundations"
                    if code.startswith(("CS ", "CI ", "SE ", "INFO"))
                    else "other",
                    "source_id": SOURCE_ID,
                    "url": urljoin(SOURCES[0], anchor["href"]) if anchor else SOURCES[0],
                    "public_site": None,
                    "syllabus": None,
                }
            elif courses[cid]["name"] != name:
                raise ValueError("Conflicting duplicate course title")
            elif ccredit is not None and courses[cid]["credits"] is None:
                courses[cid]["credits"] = ccredit
        if "orclass" in classes:
            if previous is None:
                raise ValueError("Or row without previous option")
            if previous["kind"] != "alternative":
                previous["kind"] = "alternative"
                previous["title"] = "Course alternatives"
                previous["summary"] += (
                    " Choose one of the source-listed alternatives. Credits shown on the leading row do not establish the credits of every option."
                )
            previous["course_ids"] += ids
            if target["kind"] == "choose_courses":
                target["course_ids"] += ids
            continue
        if target["kind"] == "alternative" and len(codes) == 1:
            # Following standalone math requirements end the preceding sequence choice.
            target = section
        if target["kind"] == "choose_courses":
            target["course_ids"] += ids
            previous = req(
                "Elective sequence" if len(codes) > 1 else "Elective option",
                "note",
                target["id"],
                ids,
                summary="Source-listed sequence; individual components may count toward the eight-course requirement if not used elsewhere."
                if len(codes) > 1
                else "Listed elective option; not independently required.",
            )
        else:
            previous = req(
                " + ".join(codes),
                "all",
                target["id"],
                ids,
                credit=credit if len(codes) > 1 else None,
                summary="Complete this source-listed sequence."
                if len(codes) > 1
                else ("Source row credit range " + raw + "." if raw and credit is None else ""),
            )
        if missing:
            req(
                "Unresolved course title",
                "note",
                previous["id"],
                summary="The source lists "
                + ", ".join(missing)
                + " in this sequence without a course title; title, credits and current course identity require confirmation.",
            )
    for r in reqs:
        r["course_ids"] = list(dict.fromkeys(r["course_ids"]))
    headings = {r["title"] for r in reqs}
    expected = {
        "Core Requirements",
        "Elective Requirements",
        "Project Requirements",
        "Mathematics Requirements",
        "Science Requirements",
        "Arts & Humanities Requirements",
        "University Requirements",
        "Free Electives",
    }
    if not expected <= headings or root["credits"] != 180:
        raise ValueError("Degree sections or 180-credit total changed")
    body = text(panel)
    guards = [
        "Only one of the two High Performance Computing sequences",
        "any other MATH course not used",
        "three writing-intensive courses after their freshman year",
        "Two writing-intensive courses must be in a student",
        "Transfer students need to meet with an academic advisor",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Degree footnote or writing policy changed")
    req(
        "High-performance-computing exclusion",
        "note",
        root["id"],
        summary="Select at most one of the two High Performance Computing sequences: CS 281/283/476 or ECE 350/ECEC 414.",
    )
    req(
        "MATH 200 substitutions",
        "note",
        root["id"],
        summary="MATH 200 may be replaced by CS 270, ECE 232, ENGR 232, or another MATH course not used for a different requirement. Substitute metadata and open MATH pool remain unverified.",
    )
    req(
        "Writing-intensive graduation rule",
        "note",
        root["id"],
        summary="Pass three writing-intensive courses after the first year, including two in the major. Transfer students consult an advisor about the applicable number; current WI attributes must be checked.",
    )
    return {
        "id": PROGRAM_ID,
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": reqs,
    }

from atlas.adapters.drexel_degree_policies import SOURCE_PARSERS as POLICY_PARSERS
SOURCE_PARSERS = {SOURCES[0]: parse, **POLICY_PARSERS}
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.drexel_required_course_review import register as register_reviewed_courses
SOURCES=list(SOURCES)
register_reviewed_courses(SOURCES,SOURCE_PARSERS)
