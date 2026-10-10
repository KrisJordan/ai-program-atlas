"""Additional-major mathematics alternatives and local eligibility constraints."""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from atlas.adapters.cmu_bs.common import course, requirement, text


def enrich_requirements(html, observed, url):
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find(id="textcontainer") or soup.find("main") or soup
    headings = content.find_all("h4")
    if [text(h) for h in headings] != [
        "Prerequisites",
        "Math and Statistics Core",
        "Computer Science Core",
        "Artificial Intelligence Core",
        "AI Cluster Electives",
        "Ethics and Human Cognition",
    ]:
        raise ValueError("Additional-major section inventory changed")
    words = text(content)
    for phrase in [
        '"B" average',
        "at most five courses total",
        "all other majors and minors",
        "without restriction",
        "except for 36-402",
        "Sp24 or later",
        "not required for additional majors",
    ]:
        if phrase not in words:
            raise ValueError("Additional-major policy changed: " + phrase)
    introduction = " ".join(text(p) for p in content.find_all("p") if p.find_previous("h4") is None)
    if (
        set(re.findall(r"\d{2}-\d{3}", introduction))
        != {"21-112", "21-120", "15-122", "15-150", "15-210", "15-213", "15-251", "07-280"}
        or "one of" not in introduction
        or "Program Administrator" not in introduction
    ):
        raise ValueError("Additional-major admission prerequisites changed")
    pid = observed["id"]
    source = pid + "-catalog"
    reqs = observed["requirements"]
    courses = {c["id"]: c for c in observed["courses"]}

    def add(key, title, **kwargs):
        r = requirement(pid, key, title, source, **kwargs)
        reqs.append(r)
        return r

    for heading in headings[:2]:
        pre = text(heading) == "Prerequisites"
        root = add(
            "programming-prerequisite" if pre else "mathematics",
            text(heading),
            category="foundations" if pre else "mathematics",
            summary="Programming prerequisite before the additional-major curriculum."
            if pre
            else "Six mathematics/statistics subject requirements as labeled by the source; some probability alternatives are two-course sequences.",
        )
        table = heading.find_next_sibling("table")
        if not table or "sc_courselist" not in table.get("class", []):
            raise ValueError("Additional-major mathematics/prerequisite table missing")
        branch = None
        probability = None
        mode = "pre" if pre else "math"
        group = 0
        prob_options = 0
        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            codecell = row.find("td", class_="codecol")
            if not codecell:
                comment = row.select_one(".courselistcomment")
                if comment:
                    label = text(comment)
                    if label == "Probability and Statistics (one of)":
                        mode = "probability"
                        probability = add(
                            "probability",
                            "Probability and statistics alternatives",
                            parent=root["id"],
                            category="mathematics",
                            kind="alternative",
                            count=1,
                            summary="Choose one child option; a two-course sequence requires both courses. 15-259 qualifies only if taken Spring 2024 or later.",
                        )
                    elif label == "Modern Regression Course":
                        mode = "regression"
                    else:
                        raise ValueError("Additional-major mathematics comment changed")
                continue
            links = codecell.find_all("a")
            titles = [
                re.sub(r"^and\s+", "", v.strip())
                for v in cells[1].get_text("\n", strip=True).splitlines()
            ]
            titles = [v for v in titles if not v.startswith("(if taken")]
            if len(titles) != len(links) or any(
                not re.fullmatch(r"\d{2}-\d{3}", text(a)) for a in links
            ):
                raise ValueError("Additional-major composite course row changed")
            hours = row.select_one(".hourscol")
            value = text(hours) if hours else ""
            credits = float(value) if re.fullmatch(r"\d+(?:\.\d+)?", value) else None
            ids = []
            for link, name in zip(links, titles, strict=True):
                c = course(
                    text(link),
                    name,
                    source,
                    urljoin(url, link.get("href", "")),
                    root["category"],
                    credits if len(links) == 1 else None,
                )
                courses[c["id"]] = c
                ids.append(c["id"])
            if mode == "probability":
                prob_options += 1
                add(
                    "probability-option-" + str(prob_options),
                    " + ".join(text(a) for a in links),
                    parent=probability["id"],
                    category="mathematics",
                    kind="all",
                    course_ids=ids,
                    credits=credits,
                    summary="Complete this alternative in full."
                    + (
                        " 15-259 must be taken Spring 2024 or later." if "cmu-15-259" in ids else ""
                    ),
                )
            else:
                if "orclass" not in row.get("class", []):
                    group += 1
                    branch = add(
                        ("pre" if pre else "math") + "-group-" + str(group),
                        "Programming prerequisite"
                        if pre
                        else "Mathematics requirement " + str(group),
                        parent=root["id"],
                        category=root["category"],
                        kind="choose_courses",
                        count=1,
                    )
                if branch is None:
                    raise ValueError("Additional-major orphan course alternative")
                branch["course_ids"].extend(ids)
        if pre and group != 1 or not pre and (group != 5 or prob_options != 6):
            raise ValueError("Additional-major mathematical choice count changed")
    add(
        "admission",
        "Admission prerequisites and grade average",
        category="other",
        kind="note",
        summary="Consult the program administrator. Before admission complete 21-112 or 21-120, 15-122, 15-150, one of 15-210/15-213/15-251, and 07-280; earn a B average in prerequisite coursework.",
    )
    add(
        "intro-exception",
        "Introductory AI recommendation",
        category="other",
        kind="note",
        summary="07-180 is encouraged before 07-280 but is not required for the additional major.",
    )
    add(
        "overlap",
        "Aggregate overlap limit and exceptions",
        category="other",
        kind="note",
        summary="At most five courses from CS Core, AI Core and AI Cluster Electives may double count across all other majors/minors combined. Mathematics, ethics and human cognition may double count without restriction; 36-402 remains subject to the five-course cap because it is a Machine Learning Cluster elective. Consult the administrator for substantially overlapping majors.",
    )
    for r in reqs:
        if r["title"] == "AI Cluster Electives":
            r["summary"] = "Four courses: choose one course from each of the four cluster children."
        elif r["title"] == "Ethics and Human Cognition":
            r["summary"] = "Two courses: one ethics choice and one human-cognition choice."
    observed["courses"] = list(courses.values())
    observed["notes"] = [
        "All local additional-major requirement sections observed; audit and completeness are assigned only after separate review. This does not certify the host degree. Individual course metadata remain separate."
    ]
    return observed
