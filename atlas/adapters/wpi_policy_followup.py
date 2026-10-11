"""Current operational WPI policies, retained alongside catalog conflicts."""

from bs4 import BeautifulSoup

from atlas.adapters.cmu_bs.common import requirement, text

GRADUATION_URL = "https://www.wpi.edu/offices/registrar/graduation"
BSMS_URL = "https://www.wpi.edu/academics/undergraduate/bachelors-masters-degree-program/BS-MS-program-FAQs"


def parse_graduation(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main is None or not main.find("h1") or text(main.find("h1")) != "Graduation":
        raise ValueError("WPI registrar graduation heading missing")
    table = next(
        (
            t
            for t in main.find_all("table")
            if [text(h) for h in t.find_all("th")]
            == [
                "Completion of Degree Requirements",
                "Application Deadline",
                "Degree Conferral Date",
            ]
        ),
        None,
    )
    if table is None:
        raise ValueError("Undergraduate application table missing")
    rows = []
    for tr in table.find_all("tr"):
        cells = tr.find_all("td", recursive=False)
        if not cells:
            continue
        if len(cells) != 3:
            raise ValueError("Graduation table structure changed")
        term, deadline, conferral = map(text, cells)
        if term not in ["Fall Semester", "Spring Semester", "Summer Semester"]:
            raise ValueError("Unknown undergraduate graduation term")
        rows.append(
            requirement(
                pid,
                "registrar-graduation-" + term.split()[0].lower(),
                term + " degree application",
                pid + "-registrar-graduation",
                kind="note",
                summary=f"Current registrar table: apply by {deadline} for {term.lower()} completion and {conferral} degree conferral. The catalog separately gives prior-term timing and a September conferral reference; that source discrepancy is preserved for review.",
            )
        )
    if len(rows) != 3:
        raise ValueError("Expected three undergraduate completion terms")
    return {"id": pid, "curriculum_status": "partial", "requirements": rows}


def parse_business_bsms(html, pid):
    soup = BeautifulSoup(html, "html.parser")
    h = next((h for h in soup.find_all("h2") if text(h) == "BS/MS in Business"), None)
    if h is None:
        raise ValueError("WPI business BS/MS section missing")
    paragraphs = []
    for node in h.find_all_next():
        if node.name == "h2":
            break
        if node.name == "p":
            paragraphs.append(text(node))
    value = " ".join(paragraphs)
    guards = [
        "MBA program is not part",
        "Financial Technology (FinTech) program is not part",
        "only graduate credits to double count",
        "completed C-term of their sophomore year",
        "once they have been accepted into the graduate program",
    ]
    if any(s not in value for s in guards):
        raise ValueError("Business BS/MS eligibility policy changed")
    row = requirement(
        pid,
        "business-bsms-eligibility",
        "Optional Business School BS/MS eligibility",
        pid + "-business-bsms-faq",
        kind="note",
        summary="Business graduate courses require prior graduate-program admission. Only graduate credits may be shared with a Business School MS; undergraduate courses cannot count toward it. MBA and MS Financial Technology are excluded from this BS/MS option. Business applications are first reviewed after sophomore C term. This FAQ supplies no universal undergraduate graduate-course count cap; the approved plan and existing shared-credit limits still govern.",
    )
    return {"id": pid, "curriculum_status": "partial", "requirements": [row]}
