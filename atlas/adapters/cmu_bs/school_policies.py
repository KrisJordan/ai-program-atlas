"""Observe relevant SCS standards; unrelated majors and operational policies excluded."""

from bs4 import BeautifulSoup
from .common import requirement, text

URL = "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/"
PID = "cmu-bs-ai"
SOURCE = PID + "-school-policies"


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    body = soup.find(id="policiestextcontainer")
    if body is None:
        raise ValueError("SCS policy container missing")
    words = text(body)
    checks = [
        "Graduation Requirements",
        "quality point average of 2.00 or higher",
        "minimum of four semesters",
        "at least 180 units",
        "recommended for a degree by the faculty",
        "all financial obligations",
        "semester QPA of at least 2.00",
        "cumulative QPA of at least 2.00",
        "no more than two attempts per course",
        "grade of C or higher in 15-112, 15-122 and 15-151 (or 21-127)",
        "grade of D or higher in 21-120 and 21-122",
        "Artificial Intelligence students must complete 07-280",
        "Probability course with grades of C or higher by the end of their sophomore year",
        "at least one of 15-210, 15-213 and 15-251",
        "grade of D or higher by the end of their junior year",
        "Starting Fall 2026",
        "only once",
        "3.6 or higher",
        "overall QPA of at least 3.0",
        "mini-1",
        "mini-3",
        "mini-6",
    ]
    for phrase in checks:
        if phrase not in words:
            raise ValueError("SCS degree/standing policy changed: " + phrase)
    ai_transfer = next(
        (
            text(p)
            for p in body.find_all(["p", "li"])
            if text(p).startswith("For the Artificial Intelligence primary major")
        ),
        None,
    )
    if not ai_transfer or any(
        code not in ai_transfer
        for code in [
            "15-122",
            "15-150",
            "07-280",
            "07-380",
            "15-210",
            "15-213",
            "15-251",
            "15-259",
            "21-325",
            "21-425",
            "36-218",
            "36-225",
        ]
    ):
        raise ValueError("CMU AI transfer requirements changed")
    rows = [
        (
            "transfer",
            "Conditional admission and transfer rules",
            "SCS entrants declare a major in first-year spring. Internal SCS transfers depend on interest, ability and space after consultation; no grade cutoff is specified. Transfers from other CMU schools or dual-degree applicants must complete 15-122, 15-150, 07-280, 07-380, one of 15-210/15-213/15-251, and one of 15-259/21-325/21-425/36-218/36-225; expected QPA across these six is at least 3.6 and overall QPA at least 3.0. Starting Fall 2026, apply to a specific major only once. Deadlines are last classes of mini-1, mini-3 or mini-6; review includes coursework, computing involvement and an essay. External university transfers apply through Admissions; admission depends on space and preparation. Admitted external transfers must remain in their initial SCS major at least one year and meet the internal transfer criteria before changing, excluding transferred courses.",
        ),
        (
            "graduation",
            "Graduation and residence",
            "Complete the degree program with cumulative CMU QPA at least 2.00, SCS faculty recommendation, and fulfilled university financial obligations. Residence requires at least four full-time semesters or equivalent part-time study at CMU, comprising at least 180 units.",
        ),
        (
            "standing",
            "Good academic standing",
            "Maintain semester and cumulative QPA at least 2.00. Complete attempted foundational courses by the end of sophomore year, in at most two attempts each: C or better in 15-112, 15-122 and 15-151 (or 21-127), and D or better in 21-120 and 21-122.",
        ),
        (
            "ai-progress",
            "AI-specific academic progress",
            "Complete 07-280 and the required probability course with C or better by the end of sophomore year. Complete at least one of 15-210, 15-213 or 15-251 with D or better by the end of junior year. Major-specific progress courses allow at most two attempts each. Academic-action procedures apply when good-standing conditions are unmet.",
        ),
    ]
    return {
        "id": PID,
        "curriculum_status": "partial",
        "courses": [],
        "requirements": [
            requirement(
                PID, "policy-" + key, title, SOURCE, category="other", kind="note", summary=summary
            )
            for key, title, summary in rows
        ],
        "notes": [
            "Degree-completion and academic-progress observations only; source changes require review, and this parser cannot issue a curriculum audit. Transfer/admission procedures and university-wide academic regulations are separate policies."
        ],
    }
