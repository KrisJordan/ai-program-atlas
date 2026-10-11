"""Read public CS substitution combinations, without certifying their applicability."""

import re
from bs4 import BeautifulSoup
from atlas.adapters.vt_duke_minors import rule, observation


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def parse(html, pid, source, url):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find("main") or soup
    full = text(body)
    if not all(
        t in full
        for t in [
            "CS Course Substitutions Guide",
            "MUST REQUEST",
            "No online courses",
            "Substitutions for CS Majors",
            "once you have approval",
            "can only be used once",
            "STA 360L has been re-numbered to STA 402L",
        ]
    ):
        raise ValueError("Substitution guide approval/scope changed")
    table = next(
        (
            t
            for t in body.find_all("table")
            if any(text(c) == "COMPSCI 230" for c in t.find_all("td"))
        ),
        None,
    )
    if table is None:
        raise ValueError("Major substitution table missing")
    rows = {
        text(tr.find_all("td")[0]): tr.find_all("td")
        for tr in table.find_all("tr")
        if tr.find_all("td")
    }
    expected = {
        "COMPSCI 201",
        "COMPSCI 210D",
        "COMPSCI 230",
        "COMPSCI 270L",
        "COMPSCI 330",
        "Stats requirement for CompSci BS",
    }
    if set(rows) != expected:
        raise ValueError("Major substitution row inventory changed")
    if "none allowed" not in text(
        rows["COMPSCI 201"][2]
    ) or "Pratt ECE students are still required" not in text(rows["COMPSCI 210D"][1]):
        raise ValueError("Core substitution policy changed")
    if not all(
        t in text(rows["COMPSCI 230"][1])
        for t in [
            "cannot count for any other requirement",
            "permission number",
            "Dukehub does not recognize",
        ]
    ):
        raise ValueError("COMPSCI 230 approval constraints changed")
    courses = {}
    requirements = [
        rule(
            "duke-ai-guide-core-policy",
            "Core substitution limits",
            source,
            summary="COMPSCI 201 cannot be substituted. COMPSCI 250D/ECE 250D may replace 210D for Trinity CS majors, while Pratt ECE students still require 250D; other Pratt students must consult their DUS. A 230 substitute cannot count elsewhere in the CS major. Alternatives other than 231D/232 need a prerequisite permission number because DukeHub does not recognize substitutions automatically.",
        )
    ]
    root = "duke-ai-guide-options"
    requirements.append(
        rule(
            root,
            "Conditional options from the CS substitutions guide",
            source,
            summary="These are optional routes subject to DUS approval, subsequent record amendment, no course reuse and no online substitutions. Guide/current-program discrepancies remain unresolved; these observations do not override the concentration curriculum.",
        )
    )

    def codes(value):
        value = re.sub(r"MATH/EGR\s+(\d+[A-Z]*)", r"MATH \1/EGR \1", value)
        found = re.findall(
            r"(?:COMPSCI|BME|ECE|MATH|STA|EGR|ECON|PSY|PHYSICS)\s+\d+[A-Z]*(?:/(?:COMPSCI|BME|ECE|MATH|STA|EGR)\s+\d+[A-Z]*)*",
            value,
        )
        ids = []
        for code in found:
            if code == "STA 360L":
                continue  # Source explicitly says renumbered to 402L.
            code = " / ".join(code.split("/"))
            cid = "duke-" + re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-")
            ids.append(cid)
            courses.setdefault(
                cid,
                dict(
                    id=cid,
                    code=code,
                    name=None,
                    description=None,
                    prerequisites=None,
                    credits=None,
                    credit_unit="unknown",
                    category="foundations",
                    source_id=source,
                    url=url,
                    public_site=None,
                    syllabus=None,
                ),
            )
        return list(dict.fromkeys(ids))

    def add(key, title, kind, parent, ids=(), count=None):
        rid = "duke-ai-guide-" + key
        requirements.append(
            rule(rid, title, source, kind=kind, parent=parent, ids=ids, number=count)
        )
        return rid

    branch = add("230", "Options to replace COMPSCI 230", "alternative", root, count=1)
    cell = rows["COMPSCI 230"][2]
    top = cell.find("ul").find_all("li", recursive=False)
    if len(top) != 7:
        raise ValueError("COMPSCI 230 substitution branches changed")
    # Single-course branches and a fixed two-course combination.
    for i in range(3):
        own = BeautifulSoup(str(top[i]), "html.parser")
        ids = codes(text(own))
        if len(ids) != (2 if i == 2 else 1):
            raise ValueError("Simple substitution shape changed")
        add("230-" + str(i), "Alternative " + str(i + 1), "all", branch, ids)
    # Anchor course AND one selection from an observed nested list.
    for i in [3, 4, 6]:
        li = top[i]
        nested = li.find("ul")
        copy = BeautifulSoup(str(li), "html.parser")
        for n in copy.find_all("ul"):
            n.decompose()
        anchor = codes(text(copy))
        choices = []
        if len(anchor) != 1 or nested is None or "AND" not in text(copy):
            raise ValueError("Paired substitution shape changed")
        for n in nested.find_all("li", recursive=False):
            choices += codes(text(n))
        pair = add("230-" + str(i), "Two-course alternative " + str(i + 1), "all", branch)
        add("230-" + str(i) + "-anchor", "Required member of this pair", "all", pair, anchor)
        add(
            "230-" + str(i) + "-choice",
            "Choose the other member of this pair",
            "choose_courses",
            pair,
            choices,
            count=1,
        )
    stats = top[5].find("ul")
    if stats is None or len(stats.find_all("li", recursive=False)) != 2:
        raise ValueError("Statistics pair branches changed")
    for i, li in enumerate(stats.find_all("li", recursive=False)):
        value = text(li)
        if "AND" not in value:
            raise ValueError("Statistics conjunction changed")
        left, right = value.split("AND", 1)
        pair = add("230-stats-" + str(i), "Statistics pair " + str(i + 1), "all", branch)
        add(
            "230-stats-" + str(i) + "-anchor",
            "Required statistics member",
            "all",
            pair,
            codes(left),
        )
        ids = codes(right)
        add(
            "230-stats-" + str(i) + "-other",
            "Second statistics member",
            "choose_courses" if len(ids) > 1 else "all",
            pair,
            ids,
            count=1 if len(ids) > 1 else None,
        )
    # The guide's 270L route is recorded, but conflict with the current program stays explicit.
    value = text(rows["COMPSCI 270L"][2])
    parts = value.split("AND")
    if len(parts) != 2:
        raise ValueError("COMPSCI 270L conjunction changed")
    pair = add("270l", "Guide replacement for COMPSCI 270L — applicability unresolved", "all", root)
    for i, p in enumerate(parts):
        add(
            "270l-" + str(i),
            "Choose one mathematics course",
            "choose_courses",
            pair,
            codes(p),
            count=1,
        )
    add(
        "330", "Guide replacement for COMPSCI 330", "all", root, codes(text(rows["COMPSCI 330"][2]))
    )
    stats = add(
        "bs-statistics",
        "Guide alternatives for the BS statistics requirement",
        "alternative",
        root,
        count=1,
    )
    for i, li in enumerate(rows["Stats requirement for CompSci BS"][2].find_all("li")):
        add(
            "bs-statistics-" + str(i),
            "Statistics alternative " + str(i + 1),
            "all",
            stats,
            codes(text(li)),
        )
    result = observation(pid, full, courses.values(), requirements)
    result.update(program_kind="concentration", award_level="concentration")
    return result
