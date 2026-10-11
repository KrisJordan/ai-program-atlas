"""Case 2026–2027 degree/UGER observations, including actual finite approval tables."""

import re

from bs4 import BeautifulSoup

from atlas.adapters.degree_table_observations import Tables
from atlas.adapters.national_curriculum_common import clean, require_phrases

DEGREE_URL = "https://bulletin.case.edu/undergraduate-academics/bachelors-degree-requirements/"
UGER_URL = (
    "https://bulletin.case.edu/undergraduate-academics/unified-general-education-requirements/"
)


def page(html, heading):
    soup = BeautifulSoup(html, "html.parser")
    if not any(clean(h.get_text(" ", strip=True)) == heading for h in soup.find_all("h1")):
        raise ValueError("Expected Case policy heading")
    root = soup.find(id="textcontainer")
    if root is None:
        raise ValueError("Case policy content missing")
    return root


def parse_degree(html, program_id, award):
    root = page(html, "Bachelor's Degree Requirements")
    value = clean(root.get_text(" ", strip=True))
    require_phrases(
        root,
        [
            "At least half the requirements for the major",
            "Major requirements include",
            "minimum of 60 credit hours",
            "at least 15",
            "105 credit hours",
            "2.000",
        ],
    )
    t = Tables(
        "case-" + award.lower() + "-degree",
        "case-bachelor-requirements",
        DEGREE_URL,
        unit="semester_hours",
    )

    def observed(pattern):
        match = re.search(pattern, value)
        if not match:
            raise ValueError("Degree numeric rule changed")
        return match[1]

    gpa = observed(r"cumulative grade point average of no less than ([\d.]+)")
    residency = observed(r"Earn a minimum of (\d+) credit hours")
    late = observed(r"of which at least (\d+) must be earned")
    threshold = observed(r"after the student has earned a total of (\d+) credit hours")
    t.group(
        "University degree GPA and residency",
        kind="note",
        summary=f"CWRU cumulative GPA must be at least {gpa}. Earn at least {residency} CWRU credit hours, including {late} after reaching {threshold} total credits. At least half of all major requirements, including required related-field courses and major electives, must be completed in CWRU courses.",
    )
    require_phrases(root, ["beyond 10 years", "may choose to update their requirements"])
    t.group(
        "Catalog choice and extended study",
        kind="note",
        summary="Use matriculation requirements or elect a later Bulletin. Beyond ten years, the department may update the major and the Associate Provost may update unfinished general education after reviewing the academic record.",
    )
    if award == "BS":
        total = observed(
            r"Candidates for the Bachelor of Science in Artificial Intelligence degree must complete a minimum of (\d+) credit hours"
        )
        t.group(
            "AI BS degree minimum",
            kind="note",
            credits=int(total),
            summary=f"The Case School of Engineering AI BS requires at least {total} total credit hours. The separate Arts and Sciences BS requirements are not applied to this engineering degree.",
        )
    else:
        start = value.index("Candidates for the Bachelor of Arts (BA)")
        ba = value[start : value.index("Bachelor of Science with majors", start)]
        if not all(
            s in ba
            for s in [
                "120 credit hours",
                "90 credit hours",
                "30 credit hours",
                "300- or 400-level",
                "2.000",
                "exempted from six hours",
            ]
        ):
            raise ValueError("BA school conditions changed")
        t.group(
            "BA school requirements",
            kind="note",
            credits=120,
            summary="Earn at least 120 total credit hours, including 90 in arts and sciences and 30 at the 300/400 level. Arts/sciences includes College of Arts and Sciences courses and biochemistry, computer/data sciences, economics, neuroscience and nutrition. Concurrent BA+BS students are exempt from six of the 90 arts/sciences hours. The cumulative average for graded major courses must be at least 2.000.",
        )
    return {"id": program_id, "requirements": t.rules, "curriculum_status": "partial"}


POOL_NAMES = [
    "Academic Inquiry Seminar",
    "Communication-Intensive",
    "Disciplinary Communication",
    "Capstone Project",
    "Quantitative Reasoning",
    "Semester Wellness with significant physical movement",
    "Half-semester Wellness with significant physical movement",
    "Semester Wellness without significant physical movement",
    "Half-semester Wellness without significant physical movement",
    "Moral and Ethical Reasoning",
    "Understanding Global Perspectives",
    "Human Diversity and Commonality",
    "Local and Global Engagement",
]


def parse_uger(html, program_id, award):
    root = page(html, "Unified General Education Requirements")
    require_phrases(
        root,
        [
            "2023-2024",
            "at least 6 credit hours",
            "minimum of 3 credit hours in each breadth area",
            "Up to 9 credit hours",
            "two Communication-Intensive courses",
            "At least one semester",
            "no more than one semester or two half-semesters",
            "active military service",
            "a single course may be used to satisfy all",
        ],
    )
    major_table = root.find("table", class_="tbl_breadthrequirement")
    ai_row = (
        next(
            (
                r
                for r in major_table.find_all("tr")
                if "Artificial Intelligence" in clean(r.get_text(" ", strip=True))
            ),
            None,
        )
        if major_table
        else None
    )
    if ai_row is None or not all(
        s in clean(ai_row.get_text(" ", strip=True)) for s in ["STEM", "A+H", "SS+M"]
    ):
        raise ValueError("AI breadth classification missing")
    tables = root.find_all("table", class_="sc_courselist")
    if len(tables) != 13:
        raise ValueError("UGER pool table count changed")
    t = Tables(
        "case-" + award.lower() + "-uger",
        "case-unified-general-education",
        UGER_URL,
        unit="semester_hours",
    )
    parent = t.group(
        "Unified General Education Requirements",
        summary="Applies to matriculants from 2023–2024; earlier cohorts can elect a later Bulletin. A course may fulfill every requirement for which it is approved, except that a cross-listed course counts in only one breadth area. Pools are the complete published Bulletin inventory; later approvals may be added during the year.",
    )
    breadth = t.group(
        "Breadth outside AI: arts/humanities and social sciences/management",
        parent=parent["id"],
        kind="choose_credits",
        credits=18,
        summary="AI is classified STEM+N. Earn at least 18 credits with passing letter grades in A+H and SS+M, at least six in each. Up to nine may use approved tests/transfer; at least three credits in each area must be taken at CWRU. Incoming transfer students may receive additional approved pre-matriculation transfer breadth credit. One cross-listed course may count toward only one breadth area.",
    )
    # Preserve published subject-wide eligibility and finite exceptions, rather than inventing
    # a finite inventory of every future course offered by an eligible department.
    for area, marker in [
        (
            "Arts & Humanities",
            "Courses offered by the following units will count as Arts & Humanities",
        ),
        (
            "Social Sciences & Management",
            "Courses offered by the following units will count as Social Sciences & Management",
        ),
    ]:
        head = next(
            (
                h
                for h in root.find_all(["h2", "h3", "h4", "p"])
                if clean(h.get_text(" ", strip=True)) == marker
            ),
            None,
        )
        if head is None:
            raise ValueError("Breadth subject heading missing")
        listing = head.find_next("ul")
        units = [
            clean(li.get_text(" ", strip=True)) for li in listing.find_all("li", recursive=False)
        ]
        extra = listing.find_next("ul")
        codes = list(
            dict.fromkeys(
                re.findall(r"\b[A-Z]{2,5} \d{3}[A-Z]?\b", clean(extra.get_text(" ", strip=True)))
            )
        )
        if not units or not codes:
            raise ValueError("Breadth department/exception inventory missing")
        t.group(
            area + " eligibility",
            parent=breadth["id"],
            kind="note",
            summary="Eligible published departments/subjects: "
            + "; ".join(units)
            + ". Additional approved identifiers (slash-linked listings are cross-listed choices, not multiple required courses): "
            + ", ".join(codes)
            + ". Department-wide eligibility remains an open rule.",
        )
    communication = t.group(
        "Communication sequence and Experience Portfolio",
        parent=parent["id"],
        kind="all",
        summary="Pass with letter grades an Academic Inquiry Seminar in the first or second semester, two communication-intensive courses of at least three credits each, disciplinary communication of at least three credits, and a capstone of at least three credits. Submit work from every component to the Experience Portfolio, including inquiry and capstone reflections. DC/capstone may be approved sequences and are usually completed within the major.",
    )
    wellness = t.group(
        "Wellness enrollment duration",
        parent=parent["id"],
        kind="note",
        summary="Pass with letter grades two semester-equivalents of wellness, with at least one semester-equivalent involving significant physical movement, regardless of course credits. Combine full/half semesters. A repeatable course counts for at most one semester or two half-semesters, except varsity sports, ROTC and marching band. Formal transcripted enrollment is required; active military service waives the requirement. Approved transfer credit is permitted.",
    )
    for index, (table, name) in enumerate(zip(tables, POOL_NAMES)):
        heading = clean(
            table.find_previous(["h2", "h3", "h4"]).get_text(" ", strip=True)
        ).casefold()
        expected = name.casefold().replace("project", "").strip()
        if 5 <= index <= 8 and (
            ("half-semester" in heading) != (index in (6, 8))
            or ("without significant" in heading) != (index in (7, 8))
        ):
            raise ValueError("Wellness duration/movement pool changed")
        if index not in range(5, 9) and expected not in heading.replace("project", ""):
            raise ValueError("UGER pool order/heading changed")
        ids = []
        bundles = []
        activities = []
        for row in table.find_all("tr"):
            cells = row.find_all("td", recursive=False)
            if not cells or "areaheader" in row.get("class", []):
                continue
            parsed = t.row(row)
            if parsed:
                if parsed["bundle"]:
                    bundles.append(parsed)
                else:
                    ids.extend(parsed["ids"])
            else:
                label = clean(cells[0].get_text(" ", strip=True))
                if not label:
                    raise ValueError("Empty UGER activity rule")
                activities.append(label)
        group = t.group(
            name + " approved options",
            parent=wellness["id"]
            if 5 <= index <= 8
            else communication["id"]
            if index <= 3
            else parent["id"],
            kind="note" if 5 <= index <= 8 else "choose_courses",
            count=None if 5 <= index <= 8 else 2 if index == 1 else 1,
            ids=list(dict.fromkeys(ids)),
            summary="Published approved options. Whole bundled rows require every named component; non-course options require the approval/certification printed below. Apply the governing duration, minimum credits, residency and overlap rules.",
        )
        if index == 2:
            require_phrases(table, ["MGMT 395", "Seminar (requires 3 sections)"])
            group["summary"] += " The MGMT 395 route requires three sections, not a single one-credit enrollment."
        for bundle in bundles:
            t.group(
                bundle["title"],
                parent=group["id"],
                ids=bundle["ids"],
                summary="This approved option requires the entire published course sequence; the combined hours do not establish individual credits.",
            )
        for activity in activities:
            t.group(
                "Approved non-enumerated option", parent=group["id"], kind="note", summary=activity
            )
    t.group(
        "Inquiry seminar placement and transfer",
        parent=communication["id"],
        kind="note",
        summary="Choose AIQS 100, 110, 120 or community-engaged AIQS 130 (four credits). Students for whom English is a second language and who need academic-English preparation take AIAE 100 (three credits) first, then the seminar. Some students for whom English is a second language enter AIQS 120 directly. Incoming transfers who completed prior first-year writing receive inquiry transfer credit. Other students require FSCUE appeal approval to use transfer credit. Submit two inquiry assignments; the printed word counts are ordinary examples, not universal numeric minima.",
    )
    t.group(
        "Communication residency and portfolio",
        parent=communication["id"],
        kind="note",
        summary="Both communication-intensive courses and disciplinary communication must be taken at CWRU; test/transfer substitution requires FSCUE appeal approval. Capstone must be taken at CWRU. Upload one assignment per communication-intensive course and a disciplinary communication artifact; capstone includes final project/public-facing explanation and final reflection. The portfolio also includes synthesis and self-assessment.",
    )
    t.group(
        "Quantitative and perspectives credit policies",
        parent=parent["id"],
        kind="note",
        summary="Quantitative reasoning requires a passing letter grade in an approved course of at least three credits; approved test and transfer credit may satisfy it. Moral/ethical reasoning, global perspectives, and human diversity each require passing letter grades in an approved course or sequence. Local/global engagement permits passing an approved course/sequence or participating in an approved activity. Transfer substitution for any perspective requires FSCUE appeal approval.",
    )
    # UGER approval is not subject evidence; description parsers supply reviewed taxonomy.
    for course in t.courses.values():
        course["category"] = "other"
    return {
        "id": program_id,
        "courses": list(t.courses.values()),
        "requirements": t.rules,
        "curriculum_status": "partial",
    }
