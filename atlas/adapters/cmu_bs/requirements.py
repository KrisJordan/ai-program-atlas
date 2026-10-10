"""Primary BS catalog requirements; linked school policies are separate observations."""

import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .common import course, requirement, text


def enrich_requirements(html, observed, url):
    soup = BeautifulSoup(html, "html.parser")
    heading = next((h for h in soup.find_all("h3") if text(h) == "Curriculum"), None)
    if heading is None:
        raise ValueError("CMU BS curriculum heading missing")
    scope = heading.parent
    expected = [
        "Math and Statistics",
        "Computer Science",
        "Artificial Intelligence",
        "School of Computer Science Electives",
        "Ethics Course",
        "SCIENCE AND ENGINEERING",
        "Humanities and Arts",
        "SCS First year seminar",
        "CoRE@CMU",
        "Free Electives",
        "Undergraduate Research Thesis",
    ]
    headings = {text(h): h for h in scope.find_all("h4")}
    if list(headings) != expected:
        raise ValueError("CMU BS degree section inventory changed")
    pid = observed["id"]
    source = pid + "-catalog"
    courses = {c["id"]: c for c in observed["courses"]}
    reqs = observed["requirements"]

    def add(key, title, **kwargs):
        r = requirement(pid, key, title, source, **kwargs)
        reqs.append(r)
        return r

    def section(label):
        nodes = []
        for node in headings[label].next_siblings:
            if getattr(node, "name", None) == "h4":
                break
            if getattr(node, "name", None):
                nodes.append(node)
        return " ".join(text(n) for n in nodes)

    def require(label, phrases):
        words = section(label)
        if any(p not in words for p in phrases):
            raise ValueError("CMU BS rule changed: " + label)
        return words

    def register(code, name, credits=None, category="mathematics"):
        c = course(code, name, source, url, category, credits)
        courses[c["id"]] = c
        return c["id"]

    root = add(
        "math-statistics",
        "Math and Statistics",
        category="mathematics",
        summary="Seven subject requirements; some probability options require a two-course sequence.",
    )
    table = headings["Math and Statistics"].find_next("table")
    mode = "required"
    n = 0
    pn = 0
    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        codecell = row.find("td", class_="codecol")
        if codecell is None:
            comment = row.find(class_="courselistcomment")
            if comment:
                label = text(comment)
                if label == "Probability and Statistics (one of the following options):":
                    mode = "probability"
                    prob = add(
                        "math-probability",
                        "Probability and statistics",
                        category="mathematics",
                        kind="alternative",
                        count=1,
                        parent=root["id"],
                    )
                elif label == "plus Modern Regression:":
                    mode = "required"
                else:
                    raise ValueError("CMU BS mathematics grouping changed")
            continue
        codes = re.findall(r"\d{2}-\d{3}", text(codecell))
        value = text(cells[-1])
        units = float(value) if re.fullmatch(r"\d+(?:\.\d+)?", value) else None
        lines = cells[1].get_text("\n", strip=True).splitlines()
        if mode == "probability":
            pn += 1
            names = [re.sub(r"^and\s+", "", v) for v in lines]
            if len(names) != len(codes):
                raise ValueError("CMU BS probability sequence changed")
            ids = [
                register(c, name, units if len(codes) == 1 else None)
                for c, name in zip(codes, names, strict=True)
            ]
            add(
                "math-probability-" + str(pn),
                " + ".join(codes),
                category="mathematics",
                kind="all",
                credits=units,
                parent=prob["id"],
                course_ids=ids,
                summary="Complete all courses in this alternative; any units shown apply to the entire sequence.",
            )
        else:
            n += 1
            ids = [register(codes[0], lines[0], units)]
            alternatives = re.findall(r"\d{2}-\d{3}", text(cells[1]))
            ids.extend(register(c, None) for c in alternatives)
            summary = "Complete this subject requirement."
            if alternatives:
                if codes[0] == "15-151":
                    if "if not offered, substitute" not in text(cells[1]):
                        raise ValueError("CMU BS foundation substitution changed")
                    summary = (
                        "15-151 is required; 21-127 substitutes only if 15-151 is not offered."
                    )
                else:
                    summary = "Choose one listed calculus alternative."
            add(
                "math-subject-" + str(n),
                lines[0],
                category="mathematics",
                kind="choose_courses",
                count=1,
                parent=root["id"],
                course_ids=ids,
                summary=summary,
            )
    if n != 6 or pn != 6:
        raise ValueError("CMU BS math subject/option count changed")
    require(
        "Computer Science",
        ["without credit or a waiver", "must take", "15-112", "before", "15-122"],
    )
    register("15-112", "Fundamentals of Programming and Computer Science", category="foundations")
    add(
        "programming-prerequisite",
        "Conditional programming prerequisite",
        category="foundations",
        kind="note",
        course_ids=["cmu-15-112"],
        summary="Complete 15-112 before 15-122 unless prior credit or a waiver applies.",
    )
    for r in reqs:
        match = re.search(r"min\. (\d+) units", r["title"])
        if match:
            r["credits"] = int(match[1])
            r["summary"] = (
                "Choose one course meeting the stated minimum units; additional courses may qualify when designated by the AI Undergraduate Program."
            )
    require("Artificial Intelligence", ["others as designated by the AI Undergraduate Program"])
    words = require(
        "School of Computer Science Electives",
        [
            "Two general computer science electives",
            "200-level or above",
            "at least 9 units each",
            "during their first year",
            "combine these two mini-courses",
            "Always consult with an AI undergraduate advisor",
        ],
    )
    excluded = re.search(r"following courses do NOT count as SCS electives:(.*?)Some IDEATE", words)
    if not excluded:
        raise ValueError("SCS elective exclusion list missing")
    codes = re.findall(r"\d{2}-\d{3}", excluded[1])
    r = add(
        "scs-electives",
        "SCS electives",
        category="electives",
        kind="choose_courses",
        count=2,
        credits=18,
        summary="Two approved courses from SCS departments 02/05/07/10/11/15/16/17, each at least 200-level and 9 units. Consult an AI adviser before registration; content may exclude IDeATe or other courses.",
    )
    add(
        "scs-elective-exclusions",
        "SCS elective exclusions",
        category="electives",
        kind="note",
        parent=r["id"],
        summary="Excluded course codes: " + ", ".join(codes) + ".",
    )
    add(
        "scs-mini-exception",
        "First-year introductory mini-course exception",
        category="electives",
        kind="note",
        parent=r["id"],
        summary="Two of 02-180, 05-180, 07-180 and 16-180 taken during the first year can together satisfy one SCS elective.",
    )
    for label, key, units, category in [
        ("SCIENCE AND ENGINEERING", "science-engineering", 36, "mathematics"),
        ("Humanities and Arts", "humanities-arts", 63, "human_context"),
    ]:
        require(label, ["minimum of " + str(units) + " units", "General Education Requirements"])
        add(
            key,
            label,
            category=category,
            kind="choose_credits",
            credits=units,
            summary="Complete the linked SCS general-education distribution; see its separately sourced requirement groups.",
        )
    table = headings["Humanities and Arts"].find_next("table")
    ids = []
    for row in table.find_all("tr"):
        cell = row.find("td", class_="codecol")
        if cell:
            cells = row.find_all("td", recursive=False)
            ids.append(register(text(cell), text(cells[1]), float(text(cells[2])), "human_context"))
    add(
        "cognitive-studies",
        "AI-specific Category 1A cognitive studies",
        category="human_context",
        kind="choose_courses",
        count=1,
        parent=pid + "-humanities-arts",
        course_ids=ids,
        summary="Use Category 1A cognitive studies in place of general Category 1; included within the humanities distribution.",
    )
    for label, key in [("SCS First year seminar", "first-year-seminar"), ("CoRE@CMU", "core-cmu")]:
        table = headings[label].find_next("table")
        row = table.find("tr")
        cells = row.find_all("td", recursive=False)
        code = text(cells[0])
        cid = register(code, text(cells[1]), float(text(cells[2])), "other")
        add(key, label, category="other", course_ids=[cid])
    require(
        "Free Electives",
        [
            "any Carnegie Mellon course",
            "maximum of nine (9) units",
            "Physical Education",
            "Military Science",
            "Student-Led",
            "360",
            "22",
        ],
    )
    add(
        "free-electives",
        "Free electives",
        category="electives",
        kind="choose_credits",
        credits=22,
        summary="The published degree summary assigns 22 units of free electives. Any CMU course may qualify, but at most nine combined PE, ROTC and StuCo units count toward graduation.",
    )
    add(
        "degree-minimum",
        "Degree unit minimum",
        category="other",
        kind="note",
        credits=360,
        summary="The published degree summary requires 360 total units. Distribution totals are components of this total, not additional units.",
    )
    require(
        "Undergraduate Research Thesis",
        [
            "36 units",
            "18 units per semester",
            "Up to 18 units",
            "9 per semester for 2 semesters maximum",
            "07-300",
            "practicum",
        ],
    )
    add(
        "research-thesis",
        "Optional research thesis credit treatment",
        category="electives",
        kind="note",
        summary="Optional 07-599 thesis normally spans the senior year for 36 units (18 per semester). At most 18 units satisfy SCS electives, capped at nine per semester for two semesters. A subsequent practicum after 07-300 may contribute to the 36 thesis units when it starts the thesis. Linked thesis eligibility/completion policies apply.",
    )
    observed["courses"] = list(courses.values())
    observed["notes"] = [
        "Primary BS catalog inventory observed. General education, school graduation policies and optional thesis policies are separately sourced; observation alone does not certify completeness."
    ]
    return observed
