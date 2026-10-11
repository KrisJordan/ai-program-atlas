from atlas.adapters.confirmed_depth3 import parse_delaware

PROGRAM_ID = "delaware-cs-ai-robotics-concentration"
SOURCES = ("https://www.cis.udel.edu/academics/undergraduate-programs/bscs/",)


def parse(html):
    return parse_delaware(html)


from bs4 import BeautifulSoup
from atlas.adapters.confirmed_depth3 import text

FAQ = "https://ucpc.cis.udel.edu/pages/2-students/faq.html"
FAQ_ID = PROGRAM_ID + "-committee-faq"


def note(suffix, title, summary):
    return dict(
        id=PROGRAM_ID + "-" + suffix,
        parent_id=None,
        title=title,
        kind="note",
        count=None,
        credits=None,
        credit_unit="unknown",
        category="other",
        source_id=FAQ_ID,
        source_text=None,
        summary=summary,
        course_ids=[],
    )


def parse_faq(html):
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    guards = [
        "Student FAQ",
        "no such approval is required to select a concentration",
        "second semester of your second (Sophomore) year",
        "Can independent study be used as a concentration course?",
        "No, but it can be used",
        "pass/fail cannot be used to satisfy any major or minor requirement",
        "permission must be obtained from the department",
        "you must look up the program description for your catalog year",
    ]
    if any(g not in body for g in guards):
        raise ValueError("Delaware concentration policy changed")
    return dict(
        id=PROGRAM_ID,
        requirements=[
            note(
                "declaration",
                "Declare the concentration",
                "Choose a concentration as early as possible, and no later than the second semester of sophomore year before third-year registration. No advisor approval is required to select one; changing it later may delay graduation. The default traditional BS and its advisor-approved focus area are separate paths.",
            ),
            note(
                "independent-study",
                "Independent-study exclusion",
                "Independent study cannot be used as a concentration course. Its separate use as a CISC elective or in an advisor-approved traditional focus area does not establish AI/Robotics concentration credit.",
            ),
            note(
                "grading",
                "Pass/fail and audit restrictions",
                "Pass/fail coursework cannot meet major or minor requirements. Audited courses earn no credit. No concentration-specific minimum grade is established by this FAQ.",
            ),
            note(
                "substitution",
                "Exceptions and substitutions",
                "Department permission is required for exceptional substitutions. A different course requires the Course Requirement Substitution Form; other exceptions go to the Undergraduate Curriculum and Program Committee.",
            ),
            note(
                "catalog",
                "Applicable catalog edition",
                "The university catalog controls degree requirements; use the student’s matriculation-year program description unless the student has changed to a later catalog year. Detailed current AI/Robotics course choices remain unverified.",
            ),
        ],
    )


_original_parse = parse


def parse(html):
    observed = _original_parse(html)
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if not all(
        g in body
        for g in [
            "building blocks of cognition",
            "embodied agents",
            "deep learning and neural networks",
        ]
    ):
        raise ValueError("Delaware AI/Robotics overview changed")
    observed["outcomes"] = [
        dict(
            text="Understand cognition and develop intelligent systems through reasoning, language, learning, perception, navigation and interaction.",
            kind="source_stated",
            statement_type="program_aim",
            source_id=PROGRAM_ID + "-catalog",
            locator="AI and Robotics expanded program option",
        )
    ]
    return observed


SOURCES = (*SOURCES, FAQ)
SOURCE_PARSERS = {SOURCES[0]: parse, FAQ: parse_faq}
