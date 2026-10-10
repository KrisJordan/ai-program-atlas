"""Observed Tulane college policies shared by the two distinct AI minors."""

import re

from bs4 import BeautifulSoup

NTC_URL = "https://catalog.tulane.edu/newcomb-tulane/"
SSE_URL = "https://catalog.tulane.edu/science-engineering/"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split())


def note(pid, suffix, title, summary, source):
    return {
        "id": pid + "-" + suffix,
        "parent_id": None,
        "title": title,
        "kind": "note",
        "count": None,
        "credits": None,
        "credit_unit": "unknown",
        "category": "other",
        "source_id": pid + "-" + source,
        "source_text": None,
        "summary": summary,
        "course_ids": [],
    }


def parse_ntc(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    if not any(text(h) == "Newcomb-Tulane College" for h in soup.find_all("h1")):
        raise ValueError("NTC policy heading missing")
    body = text(soup)
    guards = [
        "Minor Component",
        "No courses counting toward the student's first minor",
        "Students may not count the same course(s) toward a minor and a certificate",
        "The S/U option may not be employed",
        "major or minor requirements",
        "Credit Expiration",
        "most recent admission or readmission",
        "continuously enrolled",
        "ten years",
        "C or better",
    ]
    if any(g not in body for g in guards):
        raise ValueError("NTC minor policies changed")
    gpa = re.search(
        r"grade-point average of at least (\d+\.\d+) in courses counting toward that minor", body
    )
    if not gpa:
        raise ValueError("NTC minor GPA missing")
    rows = [
        note(
            pid,
            "college-minor-gpa",
            "College minor GPA floor",
            f"Minor courses require at least {gpa[1]} GPA; the program may impose a higher minimum.",
            "ntc-policies",
        ),
        note(
            pid,
            "college-overlap",
            "Separate minor and certificate credit",
            "A course cannot count toward two minors or both a minor and a certificate. Departments and schools set major overlap and minor-count limits.",
            "ntc-policies",
        ),
        note(
            pid,
            "college-grading",
            "S/U restriction",
            "Credit-bearing minor requirements cannot use S/U grading; both the pre-Fall-2025 and current policies exclude minors.",
            "ntc-policies",
        ),
        note(
            pid,
            "college-expiration",
            "Age of prior credit",
            "Credit older than ten years at latest admission/readmission is ineligible; qualifying credit remains valid during continuous enrollment.",
            "ntc-policies",
        ),
    ]
    # Claim transfer rules only when their approval/grade conditions are present.
    if all(
        s in body
        for s in [
            "prior approval",
            "official transcript",
            "C or better",
            "Grades are not transferred",
        ]
    ):
        rows.append(
            note(
                pid,
                "college-transfer",
                "Transfer approval and grades",
                "Transfer requires college and academic-unit approval and an official transcript with C or better. Grades do not transfer. Pre-matriculation course eligibility and approval are separately reviewed.",
                "ntc-policies",
            )
        )
    return {"id": pid, "requirements": rows}


def parse_sse(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    body = text(soup)
    if not any(text(h) == "School of Science and Engineering" for h in soup.find_all("h1")):
        raise ValueError("SSE heading missing")
    guards = [
        "Major/Minor Declaration Form",
        "Department Chair",
        "Newcomb-Tulane advisor",
        "one or two minors",
        "24 credits",
        "2.000",
        "second minor or towards a certificate",
    ]
    if any(g not in body for g in guards):
        raise ValueError("SSE declaration/overlap policies changed")
    return {
        "id": pid,
        "requirements": [
            note(
                pid,
                "school-declaration",
                "School minor declaration",
                "The department supplies the Major/Minor Declaration Form; obtain chair approval and return the signed form to the Newcomb-Tulane advisor.",
                "sse-policies",
            ),
            note(
                pid,
                "school-overlap",
                "Additional conditions for SSE degree students",
                "SSE students may add one or two minors. At least 24 major credits must remain separate from minors/certificates; minor GPA is at least 2.000, subject to stricter department rules.",
                "sse-policies",
            ),
        ],
    }
