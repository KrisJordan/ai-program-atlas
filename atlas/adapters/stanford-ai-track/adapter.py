"""Observe the formal AI track in the Stanford undergraduate CS program."""

from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = "stanford-ai-track"
SOURCES = ("https://www.cs.stanford.edu/academics-overview/academics-bachelors-program",)


def parse(html: str) -> dict:
    return parse_identity(
        html,
        program_id=PROGRAM_ID,
        title="Artificial Intelligence (CS BS track)",
        award="concentration",
        kind="concentration",
        aliases=("Artificial Intelligence",),
    )


# These sources govern the AI track's relationship to the parent CS BS.
SHEETS_URL = "https://www.cs.stanford.edu/bs-program-sheets"
DEGREE_URL = "https://www.cs.stanford.edu/bs-degree-requirements"
SOURCES += (SHEETS_URL, DEGREE_URL)


def policy(suffix, title, summary, source_id):
    return {
        "id": PROGRAM_ID + "-" + suffix,
        "parent_id": None,
        "title": title,
        "kind": "note",
        "count": None,
        "credits": None,
        "credit_unit": "units",
        "category": "other",
        "source_id": source_id,
        "source_text": None,
        "summary": summary,
        "course_ids": [],
    }


def parse_sheets(html: str) -> dict:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    normalize = lambda node: " ".join(node.get_text(" ", strip=True).split())
    title = soup.find("h1")
    body = normalize(soup)
    if title is None or normalize(title) != "BS | Program Sheets":
        raise ValueError("Stanford program sheet heading missing")
    guards = [
        "Artificial Intelligence (AI)",
        "year they matriculated",
        "not allowed to mix requirements",
        "there is no double-counting",
        "letter grade except",
        "Spring 2019-20",
        "Autumn 2020-21 through Summer 2020-21",
        "at least one quarter prior",
        "approved program sheets",
        "meet all the requirements for one CS track",
        "petition for exceptions or deviations",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Program sheet track policies changed")
    sid = PROGRAM_ID + "-program-sheets"
    rows = [
        policy(
            "sheet-year",
            "Program-sheet year selection",
            "Use a program sheet from the matriculation year or later; requirements from different sheets cannot be mixed.",
            sid,
        ),
        policy(
            "letter-grades",
            "Letter-grade requirement and historical exceptions",
            "Program-sheet courses require letter grades except Spring 2019–20 and Autumn 2020–21 through Summer 2020–21.",
            sid,
        ),
        policy(
            "category-overlap",
            "No category double-counting",
            "A program-sheet course may count under only one category; separate CS degree rules identify Writing in the Major exceptions unrelated to AI depth.",
            sid,
        ),
        policy(
            "approval",
            "Program-sheet approval",
            "Submit planned/completed courses with units for approval at least one quarter before expected graduation. Only approved sheets proceed to Engineering graduation review; special registration status also requires an approved sheet.",
            sid,
        ),
        policy(
            "track-change",
            "Track completion and changes",
            "The AI track belongs to the CS BS. Track changes are allowed, but one full CS track must be satisfied before applying to graduate; notify CS through its track-change form after the Axess request.",
            sid,
        ),
        policy(
            "petitions",
            "Exceptions and deviations",
            "Departures from the published program sheet require a petition for exceptions or deviations; approval is not assumed.",
            sid,
        ),
    ]
    return {"id": PROGRAM_ID, "curriculum_status": "partial", "requirements": rows}


def parse_degree_policies(html: str) -> dict:
    import re

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    body = " ".join(soup.get_text(" ", strip=True).split())
    title = soup.find("h1")
    if title is None or title.get_text(" ", strip=True) != "BS | Degree Requirements":
        raise ValueError("Stanford CS degree policy heading missing")
    gpa = re.search(
        r"minimum (\d+\.\d+) GPA across all Engineering Fundamentals, CS Core, Depth, and Senior Project courses combined",
        body,
    )
    if (
        gpa is None
        or "Depth section has strict minimum requirements for both the number of courses and units"
        not in body
    ):
        raise ValueError("Depth/GPA policy changed")
    sid = PROGRAM_ID + "-degree-policies"
    return {
        "id": PROGRAM_ID,
        "requirements": [
            policy(
                "gpa",
                "Combined CS program GPA",
                f"The parent CS program requires at least {gpa[1]} GPA across Engineering Fundamentals, CS Core, Depth and Senior Project combined; this is not a separately stated AI-track GPA.",
                sid,
            ),
            policy(
                "depth-minima",
                "Depth course and unit minima",
                "Both the depth course-count minimum and unit minimum must be met. The AI sheet's actual minima and choices remain unreviewed.",
                sid,
            ),
        ],
    }


SOURCE_PARSERS = {SHEETS_URL: parse_sheets, DEGREE_URL: parse_degree_policies}
