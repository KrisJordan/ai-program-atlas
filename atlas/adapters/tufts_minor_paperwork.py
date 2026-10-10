"""Fresh observations from Tufts' HTML graduation procedure, scoped to minors.

The separately reviewed public PDF checklists need viewer/PDF review; this HTML
parser never pretends that a Box shell contains the checklist document.
"""

from bs4 import BeautifulSoup
from atlas.adapters.cmu_bs.common import requirement, text

URL = "https://engineering.tufts.edu/cs/current-students/undergraduate/instructions-graduation-paperwork"


def parse_paperwork(html, *, pid):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    heading = main.find("h1") if main else None
    if heading is None or text(heading) != "Instructions for Graduation Paperwork":
        raise ValueError("Tufts graduation procedure identity missing")
    section = next(
        (
            li
            for li in main.find_all("li", class_="accordion-item")
            if li.find("h3") and text(li.find("h3")) == "All Minors (SoE and A&S)"
        ),
        None,
    )
    if section is None:
        raise ValueError("All-minors procedure section missing")
    value = text(section)
    for phrase in [
        "and sign.",
        "“IP”",
        "“TBD”",
        "Lastname Firstname CS minor checklist",
        "reviewed, signed, and returned to you via email",
        "rest of your graduation packet",
    ]:
        if phrase not in value:
            raise ValueError("Reviewed minor procedure changed: " + phrase)
    target = next(
        (a for a in section.find_all("a", href=True) if text(a) == "CS minor Box folder"), None
    )
    if target is None:
        raise ValueError("Minor submission link missing")
    source = pid + "-graduation-instructions"
    node = requirement(
        pid,
        "minor-paperwork-procedure",
        "Minor checklist processing",
        source,
        kind="note",
        category="other",
        unit="unknown",
        summary="Sign the minor checklist, mark in-progress work IP and next-semester work TBD, and name the file Lastname Firstname CS minor checklist. Submit through the linked CS minor Box folder. The department reviews/signs and returns it by email for inclusion in the graduation packet. The PDF form instead instructs future-course grade cells to remain blank; that discrepancy is recorded separately.",
    )
    return {
        "id": pid,
        "curriculum_status": "partial",
        "courses": [],
        "requirements": [node],
        "observed_submission_url": target["href"],
        "notes": [
            "Only the All Minors section applies here. Rules for CS/DS majors elsewhere on the page are not imported. Checklist PDFs require separate review."
        ],
    }
