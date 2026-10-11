"""Observe public eligibility and competing neuroscience evidence without resolving conflicts."""

import re
from bs4 import BeautifulSoup
from atlas.adapters.national_curriculum_common import rule

COMPUTING_URL = "https://www.cc.gatech.edu/minors"
NEUR_URL = "https://catalog.gatech.edu/courses-undergrad/neur/"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def guard(value, *phrases):
    if any(p not in value for p in phrases):
        raise ValueError("Georgia Tech follow-up policy changed")


def parse_computing(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    h = next((h for h in soup.find_all("h4") if text(h) == "Policies and Eligibility:"), None)
    if h is None:
        raise ValueError("Computing minor eligibility heading missing")
    section = h.find_next("ul")
    value = text(section)
    alltext = text(soup)
    guard(
        value,
        "good academic standing",
        "CS 1301 or CS 1315 or CS 1371",
        "CS 1331",
        "“B” or higher",
        "Computational Media",
        "Mathematics and Computing",
        "2021-2022 and later",
        "may not select any CS minor",
        "unless accepted",
    )
    guard(alltext, "no longer a minimum remaining credit hour requirement")
    items = [
        (
            "standing",
            "Admission and standing",
            "Applicants must have good academic standing, without warning/probation, and satisfactory academic progress. CS 1301/1315/1371 and CS 1331 must be completed with B or higher. Apply to and receive acceptance into the CS minor program before a change-of-minor form is processed.",
        ),
        (
            "excluded-majors",
            "Computing-minor eligibility exclusions",
            "Computer Science, Computational Media, and Mathematics and Computing majors cannot declare a CS minor. Computer Engineering majors using catalog year 2021–22 or later cannot select any CS minor. Restrictions specific to other computing minors are not imposed on this AI minor.",
        ),
        (
            "remaining-hours",
            "Admission timing",
            "There is no longer a minimum remaining-credit-hour admission requirement. The college advises allowing three to four semesters, excluding summer, because of sequencing and course availability; this is planning guidance, not an invented minimum enrollment requirement.",
        ),
    ]
    return dict(
        id=pid,
        curriculum_status="partial",
        courses=[],
        requirements=[
            rule("gt-college-" + k, t, "gatech-computing-minor-eligibility", kind="note", summary=s)
            for k, t, s in items
        ],
    )


def parse_neuroscience(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    value = text(soup)
    facts = []
    for code, title in [
        ("NEUR 3803", "Special Topics in Neuroscience"),
        ("NEUR 4740", "Neuroethics"),
    ]:
        match = re.search(
            re.escape(code) + r"\.\s*" + re.escape(title) + r"\.\s*(\d+) Credit Hours?\.", value
        )
        if match is None:
            raise ValueError("Neuroscience catalog identity changed")
        facts.append(code + " is " + title + " (" + match[1] + " catalog credit hours)")
    return dict(
        id=pid,
        curriculum_status="partial",
        courses=[],
        requirements=[
            rule(
                "gt-apps-neur-crosscheck",
                "Neuroscience subject-catalog cross-check",
                "gatech-neuroscience-course-catalog",
                kind="note",
                summary="; ".join(facts)
                + ". These individual course identities support a discrepancy review but do not establish the intended minor cross-listing or topic. The conflicting minor row is retained pending advising clarification.",
            )
        ],
    )


def parse_program_neuroscience(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    value = text(soup)
    guard(
        value,
        "NEUR/PSYC 3803",
        "NEUR/PSYC 4740",
        "Neuroethics",
        "Computational Cognitive Neuroscience",
    )
    return dict(
        id=pid,
        curriculum_status="partial",
        courses=[],
        requirements=[
            rule(
                "gt-apps-site-neuroscience",
                "Competing program-site neuroscience wording",
                "gatech-apps-program-requirements",
                kind="note",
                summary="The program site lists the computational-cognitive-neuroscience topic under NEUR/PSYC 3803 and Neuroethics under NEUR/PSYC 4740. The catalog minor row combines NEUR 4740/PSYC 3803 with that topic. This records both source statements without rewriting catalog eligibility.",
            )
        ],
    )
