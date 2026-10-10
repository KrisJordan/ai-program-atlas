"""Observe Columbia College rules and the math lists referenced by its AI minor."""

import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

PID = "columbia-ai-minor"
COLLEGE_ID = "columbia-ai-minor-college-policies"


def text(node):
    return " ".join(node.get_text(" ", strip=True).replace("\u200b", "").split())


def section(soup, title):
    h = next((h for h in soup.find_all(re.compile(r"^h[1-6]$")) if text(h) == title), None)
    if h is None:
        raise ValueError("Missing Columbia policy section: " + title)
    parts = []
    for n in h.find_next_siblings():
        if n.name and re.fullmatch(r"h[1-6]", n.name) and int(n.name[1]) <= int(h.name[1]):
            break
        parts.append(str(n))
    return BeautifulSoup("".join(parts), "html.parser")


def guard(node, *phrases):
    value = text(node)
    if not all(p in value for p in phrases):
        raise ValueError("Columbia policy changed: " + ", ".join(phrases))
    return value


def enrich_department(soup, courses, requirements, req, key, source, url):
    math = section(soup, "Mathematics Requirement (6-11 points)")
    tables = math.find_all("table")
    if len(tables) != 3:
        raise ValueError("CS Core math table inventory changed")
    guard(math, "may simultaneously satisfy both", "without the need to take additional classes")
    base = next(r for r in requirements if r["id"] == PID + "-foundation-0")
    base.update(kind="alternative", count=1, course_ids=[])
    requirements.append(
        req(
            "math-combined",
            "Combined linear algebra and probability",
            "all",
            ["columbia-math-un2015"],
            parent=base["id"],
        )
    )
    pair = req("math-separate", "Separate linear algebra and probability", "all", parent=base["id"])
    requirements.append(pair)
    for table, label, suffix in [
        (tables[1], "Linear Algebra Requirement", "linear"),
        (tables[2], "Probability / Statistics Requirement", "probability"),
    ]:
        guard(table, label, "Select one of the following courses")
        ids = []
        for row in table.find_all("tr"):
            cell = row.find("td", class_="codecol")
            if cell is None:
                continue
            code = text(cell)
            if not re.fullmatch(r"[A-Z]+ [A-Z]+\d{4}", code):
                raise ValueError("Unknown CS Core mathematics code")
            if code == "MATH UN2015":
                continue  # This combined course is the other branch, not half of a pair.
            cid = "columbia-" + key(code)
            ids.append(cid)
            cells = row.find_all("td", recursive=False)
            hours = row.find("td", class_="hourscol")
            amount = text(hours) if hours else ""
            if amount and not re.fullmatch(r"\d+(?:\.\d+)?", amount):
                raise ValueError("Unknown mathematics points value")
            link = cell.find("a", href=True)
            courses[cid] = dict(
                id=cid,
                code=code,
                name=text(cells[1]).removesuffix(" (recommended)") or None,
                description=None,
                prerequisites=None,
                credits=float(amount) if amount else None,
                credit_unit="unknown",
                category="foundations",
                source_id=source,
                url=urljoin(url, link["href"]) if link else url,
                public_site=None,
                syllabus=None,
            )
        if not ids:
            raise ValueError("Empty mathematics substitute list")
        requirements.append(
            req("math-" + suffix, label, "choose_courses", ids, count=1, parent=pair["id"])
        )
    old = next(r for r in requirements if r["id"] == PID + "-math-substitution")
    old["summary"] = (
        "MATH UN2015 can satisfy both components alone; alternatively select a separate course from each referenced CS Core mathematics list. The CS major's separate calculus requirement is not imposed on this minor. COMS W3251 is the recommended linear algebra option."
    )
    double = section(soup, "Double Counting")
    guard(
        double,
        "student's home school",
        "No other courses can be double-counted",
        "One Linear Algebra course",
        "One Probability/Statistics course",
        "COMS W1004",
    )
    requirements.append(
        req(
            "department-overlap",
            "Department limits on overlap with other programs",
            "note",
            summary="Subject to home-school rules, CS permits overlap only for COMS W1004, calculus (including Honors Math A/B), one linear algebra course and one probability/statistics course; other courses cannot overlap another program. This does not resolve reuse between the AI requirement and AI elective within this minor.",
        )
    )
    grade = section(soup, "D Grades")
    guard(grade, "one course", "4 points", "grade of D", "major or minor")
    requirements.append(
        req(
            "department-d-grade",
            "Department D-grade exception",
            "note",
            summary="At most one course worth no more than four points with grade D may count toward the major or minor, as stated in departmental Restrictions / D Grades.",
        )
    )


def parse_college(html):
    soup = BeautifulSoup(html, "html.parser")
    minor = section(soup, "Minors")
    guard(
        minor,
        "Spring semester of their sophomore year",
        "or they can declare a minor at a later point",
    )
    maximum = section(soup, "Maximum Number of Programs of Study")
    guard(
        maximum,
        "eight semesters",
        "three (3)",
        "more than two minors",
        "same offering unit",
        "All joint majors",
    )
    overlap = section(soup, "Policy on Double-Counting Courses toward Requirements")
    guard(
        overlap,
        "STAT UN1101 or UN1201",
        "COMS W1004",
        "maximum of two classes",
        "already approved",
        "may not be double-counted",
        "three declared programs",
    )
    summaries = [
        (
            "declaration",
            "Minor declaration and host degree",
            "The College minor accompanies a major. Declaration may occur in spring of sophomore year or later if completion fits the student's program.",
        ),
        (
            "program-limits",
            "Number, duration and offering-unit limits",
            "At most three programs, no more than two majors or two minors, and at least one major. No additional semesters are granted for another program beyond eight total semesters, including prior transfer terms; additional programs must fit the expected workload without regular petitions above 18 points. Programs cannot share an offering unit, and joint majors belong to both units.",
        ),
        (
            "college-overlap",
            "College overlap framework",
            "Eligible shared foundational skills include elementary/intermediate languages, the listed calculus sequences, STAT UN1101/UN1201 and COMS W1004. Other foundational exceptions require Committee on Instruction approval. Core Global Core, Science and Language distribution courses may also overlap, but shared Core courses cannot. Up to two additional already-approved classes may overlap two programs; substitutions should not be sought solely to create overlap. An applicable condition may span three programs. Departmental restrictions must also be observed.",
        ),
    ]
    rows = [
        dict(
            id=PID + "-college-" + suffix,
            parent_id=None,
            title=title,
            kind="note",
            count=None,
            credits=None,
            credit_unit="unknown",
            category="other",
            source_id=COLLEGE_ID,
            source_text=None,
            summary=summary,
            course_ids=[],
        )
        for suffix, title, summary in summaries
    ]
    return dict(id=PID, curriculum_status="partial", courses=[], requirements=rows)
