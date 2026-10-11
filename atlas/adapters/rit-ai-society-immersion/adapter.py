"""Observe the public rendered immersion table; never infer it from the minor."""

import re
from bs4 import BeautifulSoup
from atlas.adapters.confirmed_depth3 import parse_rit_immersion

PROGRAM_ID = "rit-ai-society-immersion"
URL = "https://www.rit.edu/study/ai-society-immersion"
SID = PROGRAM_ID + "-rendered-curriculum"
SOURCES = [URL, "https://www.rit.edu/study/immersions-and-minors"]


def text(n):
    return " ".join(n.get_text(" ", strip=True).split()) if n else ""


def rule(suffix, title, source=SID, **kwargs):
    return (
        dict(
            id=PROGRAM_ID + "-" + suffix,
            parent_id=None,
            title=title,
            kind="note",
            count=None,
            credits=None,
            credit_unit="unknown",
            category="human_context",
            source_id=source,
            source_text=None,
            summary=title,
            course_ids=[],
        )
        | kwargs
    )


def parse(html):
    observed = parse_rit_immersion(html)
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    table = soup.select_one("#curriculumContainer table.sc_courselist")
    if table is None:
        observed["notes"] = [
            "Identity observed; HTTP response has no rendered overview/course table. Normal public browser observation is required. No course inventory, aim or completeness assertion emitted."
        ]
        return observed
    if (
        "historical, social, cultural, ethical, policy, and environmental perspectives" not in body
        or "may not overlap with program requirements" not in body
    ):
        raise ValueError("RIT immersion overview context changed")
    observed["outcomes"] = [
        dict(
            text="Analyze how AI and society shape one another through historical, social, cultural, ethical, policy and environmental perspectives.",
            kind="source_stated",
            statement_type="program_aim",
            source_id=SID,
            locator="Immersion overview",
        )
    ]
    if "Curriculum for 2026-2027 for AI in Society Immersion" not in body:
        raise ValueError("Reviewed RIT curriculum year changed")
    courses, required, choices = [], [], []
    section = None
    for tr in table.select("tr"):
        label = text(tr)
        if label == "Required Course":
            section = "required"
        elif label == "Electives":
            section = "electives"
        bubble = tr.select_one("[data-code-bubble]")
        if not bubble:
            continue
        code = text(bubble)
        td = tr.find_all("td", recursive=False)
        if (
            not re.fullmatch(r"[A-Z]+-\d{3}", code)
            or len(td) != 3
            or section not in ("required", "electives")
        ):
            raise ValueError("Unrecognized RIT course table row")
        amount = text(td[2])
        cid = PROGRAM_ID + "-" + code.lower()
        courses.append(
            dict(
                id=cid,
                code=code,
                name=text(td[1]),
                description=None,
                prerequisites=None,
                credits=float(amount) if re.fullmatch(r"\d+(?:\.\d+)?", amount) else None,
                credit_unit="unknown",
                category="human_context",
                source_id=SID,
                url=URL,
                public_site=None,
                syllabus=None,
            )
        )
        (required if section == "required" else choices).append(cid)
    expected = {
        "STSO-320",
        "STSO-140",
        "STSO-201",
        "STSO-240",
        "STSO-340",
        "STSO-350",
        "STSO-360",
        "STSO-425",
        "STSO-441",
        "DHSS-101",
        "DHSS-103",
        "PHIL-307",
        "POLS-280",
        "VISL-234",
    }
    if (
        len(courses) != 14
        or {c["code"] for c in courses} != expected
        or required != [PROGRAM_ID + "-stso-320"]
    ):
        raise ValueError("RIT immersion finite course pool changed")
    if "Select two of the following: 6" not in text(table) or "Total Hours 9" not in text(table):
        raise ValueError("RIT selection or total changed")
    total = rule(
        "total",
        "Three-course AI in Society immersion",
        kind="all",
        credits=9,
        summary="Complete STSO-320 and two listed electives for nine published hours.",
    )
    observed.update(
        catalog_year="2026-2027",
        courses=courses,
        requirements=[
            total,
            rule(
                "required",
                "Required course",
                kind="all",
                parent_id=total["id"],
                course_ids=required,
            ),
            rule(
                "electives",
                "Choose two listed electives",
                kind="choose_courses",
                count=2,
                credits=6,
                parent_id=total["id"],
                course_ids=choices,
            ),
            rule(
                "local-overlap",
                "Outside-major study and no program overlap",
                summary="The immersion provides study outside the major; it may complement but may not overlap program requirements.",
            ),
        ],
    )
    return observed


POLICIES = {
    "rit-immersion-policy": (
        "https://www.rit.edu/generaleducation/immersions",
        "Immersions",
        [
            "All students need to declare an Immersion",
            "may not overlap with program requirements",
            "Programs may not restrict students",
            "coursework for a minor",
        ],
        [
            (
                "declaration",
                "Declare the immersion through the Student Information System; all students must declare an immersion, while minors are optional.",
            ),
            (
                "choice-overlap",
                "Programs cannot restrict students to a particular immersion or group of immersions. Immersion work cannot overlap program requirements, but can fulfill some coursework of a corresponding minor.",
            ),
        ],
    ),
    "rit-curriculum-policy": (
        "https://www.rit.edu/study/curriculum-requirements",
        "Rochester Institute of Technology Curriculum Requirements for Current Students",
        [
            "academic year that you matriculated",
            "academic year that you have been advised to follow",
        ],
        [
            (
                "catalog-applicability",
                "Follow the curriculum from the academic year of matriculation into the current program or the year an advisor directs the student to follow; consult the Academic Advising Report and advisor.",
            )
        ],
    ),
    "rit-d014": (
        "https://www.rit.edu/policies/d014",
        "D01.4 General Education Framework",
        ["at least nine credit hours", "semester credit hours (sch)"],
        [
            (
                "framework",
                "An immersion is at least three related general-education courses totaling at least nine semester credit hours. This local inventory does not certify the host degree’s full general-education requirements.",
            )
        ],
    ),
    "rit-d050": (
        "https://www.rit.edu/policies/d050",
        "D05.0 Grades",
        ["Minimum Passing Grade", "including the immersion"],
        [
            (
                "grading",
                "D is the university minimum passing grade. The elective Pass/No Pass option cannot satisfy general-education requirements, explicitly including the immersion; no separate immersion minimum GPA is stated on the reviewed local page.",
            )
        ],
    ),
    "rit-d020": (
        "https://www.rit.edu/policies/d020",
        "D02.0 Admission",
        [
            "Evaluation of transfer credit is made by the academic school or department",
            'approved courses with a grade of "C" or better',
            "secure the prior written approval",
        ],
        [
            (
                "transfer",
                "Transfer credit requires approved equivalent coursework with C or better, evaluated by the relevant academic unit and College of Liberal Arts. Enrolled RIT students need prior written approval of their home college dean/designee (or applicable unit director). Transfer work remains subject to host-degree residency requirements.",
            )
        ],
    ),
    "rit-d120": (
        "https://www.rit.edu/policies/d120",
        "D12.0 Graduation Requirements",
        [
            "A minimum of 25 % of the total semester credit hours",
            "seven (7) calendar years",
            "approval of the head of the student’s primary academic department",
        ],
        [
            (
                "residency-context",
                "The host bachelor degree requires at least 25% of its total semester credits in successfully completed RIT courses; the degree-granting program chooses which courses satisfy residence. This is not a separate 25% immersion residency rule.",
            ),
            (
                "catalog-limit",
                "The undergraduate bulletin may be the matriculation edition or a later advantageous edition, but not one more than seven calendar years old at graduation. Curriculum adjustments require approval of the primary department head; discontinued courses need not be offered.",
            ),
        ],
    ),
}


def parse_policy(html, key):
    soup = BeautifulSoup(html, "html.parser")
    url, title, guards, rules = POLICIES[key]
    if not any(text(h) == title for h in soup.find_all("h1")) or any(
        g not in text(soup) for g in guards
    ):
        raise ValueError("RIT applicable policy changed: " + key)
    return dict(
        id=PROGRAM_ID,
        requirements=[
            rule(suffix, summary, source=PROGRAM_ID + "-" + key) for suffix, summary in rules
        ],
    )


from functools import partial

SOURCE_PARSERS = {URL: parse}
for key, (url, *_) in POLICIES.items():
    SOURCES.append(url)
    SOURCE_PARSERS[url] = partial(parse_policy, key=key)
