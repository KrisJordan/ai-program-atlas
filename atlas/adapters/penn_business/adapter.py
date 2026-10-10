"""Wharton undergraduate concentration: do not mislabel as a standalone BS."""

import re

from bs4 import BeautifulSoup

from atlas.adapters.penn_bse.common import penn_course, req, text

SOURCES = ["https://oid.wharton.upenn.edu/artificial-intelligence-joint-concentration/"]
PID = "penn-concentration-ai-business"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    if not h1 or text(h1) != "Artificial Intelligence for Business Joint Concentration":
        raise ValueError("Wharton undergraduate concentration heading missing")
    heading = next(
        (h for h in soup.find_all("h3") if text(h) == "Requirements for Concentration"), None
    )
    if heading is None:
        raise ValueError("Wharton concentration requirements missing")
    nodes = []
    for n in heading.next_siblings:
        if getattr(n, "name", None) == "h3":
            break
        nodes.append(n)
    section = BeautifulSoup("".join(map(str, nodes)), "html.parser")
    if not re.search(r"requires a total of 4 CU", text(section)):
        raise ValueError("Wharton total changed")
    headings = section.find_all("h4")
    if len(headings) != 4:
        raise ValueError("Wharton four pillar requirements changed")
    source = PID + "-curriculum"
    courses = {}
    requirements = []
    root = req(PID, "concentration", "Concentration requirements", source, credits=4)
    requirements.append(root)
    for index, h in enumerate(headings):
        label = text(h)
        category = "ai_ml" if label.startswith("Pillar F") else "human_context"
        if not label.startswith(("Pillar F", "Pillar I")):
            raise ValueError("Wharton pillar heading changed")
        paras = []
        for n in h.next_siblings:
            if getattr(n, "name", None) == "h4":
                break
            if getattr(n, "name", None) == "p":
                paras.append(n)
        items = []
        for p in paras:
            for line in p.get_text("\n", strip=True).splitlines():
                match = re.fullmatch(
                    r"([A-Z]{2,5}(?:/[A-Z]{2,5})? \d{4}):\s*(.+?)(?:\s*\((\d+(?:\.\d+)?) CU\))?",
                    line.strip(),
                )
                if not match:
                    continue
                item = penn_course(
                    match.group(1),
                    match.group(2),
                    source,
                    SOURCES[0],
                    category,
                    float(match.group(3)) if match.group(3) else None,
                )
                courses[item["id"]] = item
                items.append(item["id"])
        if not items:
            raise ValueError("Wharton pillar courses missing")
        if index >= 2:
            m = re.search(r"additional (\d+(?:\.\d+)?) CU", label)
            if not m:
                raise ValueError("Wharton elective credit rule changed")
            credits = float(m.group(1))
        else:
            if any(courses[c]["credits"] is None for c in items):
                raise ValueError("Wharton required-course credits missing")
            credits = sum(courses[c]["credits"] for c in items)
        requirements.append(
            req(
                PID,
                "pillar-" + str(index + 1),
                label,
                source,
                category=category,
                parent=root["id"],
                kind="all" if index < 2 else "choose_credits",
                credits=credits,
                course_ids=items,
            )
        )
    if sum(r["credits"] for r in requirements[1:]) != 4:
        raise ValueError("Wharton pillar credits disagree with total")
    policies = [text(li) for li in section.find_all("li")]
    if len(policies) != 3:
        raise ValueError("Wharton concentration policy inventory changed")
    if not any("pass/fail" in p and "cannot be counted" in p for p in policies):
        raise ValueError("Wharton grading policy missing")
    requirements.append(
        req(
            PID,
            "grading",
            "Letter-grade policy",
            source,
            kind="note",
            parent=root["id"],
            category="other",
            summary="Pass/fail courses cannot count toward the concentration.",
        )
    )
    for key, phrase, label in [
        ("independent-study", "Independent Study Project", "Independent-study allowance"),
        ("outside-wharton", "outside of Wharton", "Outside-Wharton allowance"),
    ]:
        policy = next((p for p in policies if phrase in p), "")
        match = re.search(r"maximum of (\d+(?:\.\d+)?) CU", policy)
        if not match or "faculty advisor approval" not in policy:
            raise ValueError("Wharton approval/cap policy missing: " + key)
        cap = float(match.group(1))
        requirements.append(
            req(
                PID,
                key,
                label,
                source,
                kind="note",
                parent=root["id"],
                category="other",
                summary=f"At most {cap:g} CU may count with faculty advisor approval. "
                + (
                    "Applies to an Independent Study Project."
                    if key == "independent-study"
                    else "Applies to Penn courses outside Wharton."
                ),
            )
        )
    return {
        "id": PID,
        "title": "Artificial Intelligence for Business",
        "award_level": "concentration",
        "program_kind": "concentration",
        "catalog_year": None,
        "curriculum_status": "partial",
        "courses": list(courses.values()),
        "requirements": requirements,
        "notes": [
            "Observed complete local four-CU pillar inventory and all three published policies. Completeness requires a separate review audit. This concentration does not certify completion of the host Wharton BS in Economics; course metadata remain separately incomplete."
        ],
    }


PROGRAM_ID = "penn-concentration-ai-business"
