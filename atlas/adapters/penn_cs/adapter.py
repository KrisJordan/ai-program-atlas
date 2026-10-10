"""Penn CSCI concentration accordion; names/individual credits unknown on this page."""

import re

from bs4 import BeautifulSoup

from atlas.adapters.penn_bse.common import penn_course, req, text

SOURCES = ["https://www.cis.upenn.edu/undergraduate-program-options/concentrations/"]
PID = "penn-concentration-ai-cs"


def codes(value):
    found = []
    for match in re.finditer(r"([A-Z]{2,5})\s*(\d{4}(?:/\d{4})*)", value):
        found.extend(match.group(1) + " " + n for n in match.group(2).split("/"))
    return found


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1 or "Concentrations" not in text(h1):
        raise ValueError("Penn CSCI concentration page heading missing")
    intro = []
    for node in h1.find_all_next():
        if node.name == "h2":
            break
        if node.name == "p":
            intro.append(text(node))
    intro_text = " ".join(intro)
    for phrase in (
        "only for students pursuing a CSCI degree",
        "concentrations are optional",
        "one concentration per degree",
    ):
        if phrase not in intro_text:
            raise ValueError("Penn concentration eligibility policy missing: " + phrase)
    block = None
    for item in soup.select(".accordion-item"):
        heading = item.find("h2")
        if heading and text(heading) == "Artificial Intelligence":
            block = item.select_one(".accordion-body")
            break
    if block is None:
        raise ValueError("Penn AI concentration section missing")
    lines = [text(p) for p in block.find_all("p")]
    content = " ".join(lines)
    if "4 CUs" not in content or "Pick the remaining two CUs from:" not in content:
        raise ValueError("Penn concentration credit rule changed")
    required = []
    elective = []
    mode = None
    for line in lines:
        if line == "Required:":
            mode = "required"
            continue
        if line == "Pick the remaining two CUs from:":
            mode = "elective"
            continue
        if mode == "required" and codes(line):
            required.append(codes(line))
        if mode == "elective":
            elective.extend(codes(line))
    if len(required) != 2 or not elective:
        raise ValueError("Penn concentration requirement lists incomplete")
    source = PID + "-curriculum"
    courses = {}
    root = req(PID, "concentration", "AI concentration", source, credits=4)
    requirements = [root]
    for i, options in enumerate(required):
        ids = []
        for code in options:
            c = penn_course(code, None, source, SOURCES[0])
            courses[c["id"]] = c
            ids.append(c["id"])
        requirements.append(
            req(
                PID,
                "core-" + str(i + 1),
                "Required core option " + str(i + 1),
                source,
                parent=root["id"],
                kind="choose_courses",
                count=1,
                course_ids=ids,
            )
        )
    ids = []
    for code in elective:
        c = penn_course(code, None, source, SOURCES[0])
        courses[c["id"]] = c
        ids.append(c["id"])
    requirements.append(
        req(
            PID,
            "electives",
            "Remaining AI electives",
            source,
            parent=root["id"],
            kind="choose_credits",
            credits=2,
            course_ids=ids,
        )
    )
    requirements.append(
        req(
            PID,
            "eligibility",
            "Parent-degree eligibility and concentration limit",
            source,
            kind="note",
            category="other",
            summary="Available only to students pursuing a CSCI degree. Optional; at most one concentration per degree. Declare through the university field-of-study form.",
        )
    )
    return {
        "id": PID,
        "title": "Artificial Intelligence",
        "award_level": "concentration",
        "program_kind": "concentration",
        "catalog_year": None,
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": requirements,
        "notes": [
            "All published local AI concentration options, four-CU rule and CSCI eligibility/one-concentration limit observed. Separate review audit determines completeness; this does not certify the parent degree. The source lists codes only, so course titles, individual credits and prerequisites remain separate metadata gaps."
        ],
    }


PROGRAM_ID = "penn-concentration-ai-cs"
