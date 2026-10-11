"""Linked current option tables and degree policy observations."""

import json
import re
from bs4 import BeautifulSoup
from .common import course, requirement, text

PID = "cmu-bs-ai"
SCIENCE = "https://www.cs.cmu.edu/education/undergraduate/science-and-engineering-reqs1"
HUMANITIES = "https://www.cs.cmu.edu/education/undergraduate/humanities-and-arts-requirements"
REGULATIONS = "https://coursecatalog.web.cmu.edu/aboutcmu/undergraduateacademicregulations/"
THESIS = "https://coursecatalog.web.cmu.edu/schools-colleges/schoolofcomputerscience/honors-research-thesis/"
DATA_BASE = "https://www.cs.cmu.edu/rs-datasources/data-source/scs-gen-ed-reqs-"
DATASETS = {
    "sci-approved": ("science-additions", "Additional approved science options"),
    "lab-approved": ("lab", "Laboratory requirement"),
    "sci-deletions": ("science-exclusions", "Science exclusions"),
    "cat2": ("category-2", "Economic, political and social institutions"),
    "cat3": ("category-3", "Cultural analysis"),
    "arts-additions": ("humanities-additions", "Additional approved humanities/arts options"),
    "arts-deletions": ("humanities-exclusions", "Humanities/arts exclusions"),
}


def payload(source, rows, courses=None):
    return {
        "id": PID,
        "curriculum_status": "partial",
        "courses": courses or [],
        "requirements": [
            requirement(
                PID,
                key,
                title,
                source,
                category="other",
                kind="note",
                summary=summary,
                course_ids=ids,
            )
            for key, title, summary, ids in rows
        ],
        "notes": [
            "Linked source observation only; manual reconciliation with primary requirements is required. No audit or completeness is emitted."
        ],
    }


def parse_options(raw, key):
    data = json.loads(raw)
    if (
        data.get("success") != "true"
        or data.get("more") != "0"
        or [c["n"] for c in data.get("cols", [])] != ["course-number", "title", "units"]
    ):
        raise ValueError("CMU option feed incomplete or schema changed")
    if not data.get("data"):
        raise ValueError("CMU option feed empty")
    source = PID + "-current-" + key
    courses = []
    excluded = []
    for row in data["data"]:
        if len(row) != 3 or not re.fullmatch(r"\d{2}-(?:\d{3}|xxx)", row[0]):
            raise ValueError("CMU option-feed row changed")
        code, name, units = row
        if key.endswith("deletions"):
            excluded.append(code + (": " + name if "xxx" in code else ""))
            continue
        if "xxx" in code:
            raise ValueError("Wildcard in positive course list")
        c = course(
            code,
            name,
            source,
            DATA_BASE + key,
            "mathematics" if key.startswith(("sci", "lab")) else "human_context",
            float(units) if re.fullmatch(r"\d+(?:\.\d+)?", units) else None,
        )
        courses.append(c)
    reqkey, title = DATASETS[key]
    summary = (
        ("Current exclusions: " + "; ".join(excluded) + ".")
        if excluded
        else "Current approved option pool. Selection and combination rules are specified by the linked distribution pages."
    )
    return payload(
        source, [("gened-" + reqkey, title, summary, [c["id"] for c in courses])], courses
    )


def parse_current_page(html, kind):
    soup = BeautifulSoup(html, "html.parser")
    words = text(soup)
    if kind == "science":
        checks = [
            "minimum of 36 units",
            "at least four courses",
            "at least two courses must be from the same department",
            "no Electrical and Computer Engineering graduate courses",
            "18-6xx",
            "18-7xx",
            "18-8xx",
            "18-9xx",
            "before registration",
        ]
        summary = "Current science rules supplement the catalog: consult an SCS adviser before registration for every selected course; minis need adviser/associate-dean review. ECE graduate courses (18-6xx through 18-9xx) are excluded. Unlisted Engineering & Public Policy courses require adviser/associate-dean suitability review. SCS crosslists or substantial mathematical/computational content generally disqualify a course."
    else:
        checks = [
            "minimum of 63 units",
            "two minis totaling 9 units or more",
            "permission of the associate dean",
            "replace Category 1 with Category 1A",
            "Complete three nontechnical courses",
            "adviser approval",
        ]
        summary = "Current humanities rules permit two minis totaling at least nine units to fulfill one breadth category only with associate-dean permission and suitable category goals. Lower-unit humanities/arts courses may combine into one nine-unit elective with adviser and associate-dean approval. AI uses Category 1A; other Category 1 options are excluded from this AI inventory."
    if any(v not in words for v in checks):
        raise ValueError("CMU current " + kind + " policy changed")
    return payload(
        PID + "-current-" + kind,
        [("gened-current-" + kind, "Current " + kind + " approval rules", summary, [])],
    )


def parse_regulations(html):
    soup = BeautifulSoup(html, "html.parser")
    words = text(soup)
    for marker in [
        "Standard Degree Requirements & Degree Certification",
        "free-elective course pass/no-pass",
        "only one set of units will count",
        "grade of C- or better",
        "within eight years",
        "all courses taken after the first year",
        "eight semesters of full-time enrollment",
        "Higher Level IB exams",
        "not being used to fulfill a college, school, major or minor requirement",
        "completed two full semesters",
        "Vice-Provost for Education",
        "space-available basis",
    ]:
        if marker not in words:
            raise ValueError("CMU undergraduate regulation changed: " + marker)
    return payload(
        PID + "-university-regulations",
        [
            (
                "university-grading",
                "Grading and repeated credit",
                "A free elective is not simultaneously used for a college, school, major or minor requirement. Pass/no-pass may be elected for a free elective unless disallowed; A–D earns P credit without QPA points. Audit earns no credit. Repeated-course grades all affect QPA, but units count once; repeating a passed course needs dean/department-head approval. Course prerequisites and corequisites must be met.",
                [],
            ),
            (
                "university-course-access",
                "Course access and campus transfer",
                "Primary-major registration has priority. Other-program courses are space-available and not guaranteed; prerequisites and corequisites still apply. Pittsburgh–Doha permanent campus transfer requires good standing, two completed semesters, a compelling rationale and Vice-Provost approval through the exceptional formal process; consult the home associate dean. A Qatar-only pool listing is not permission for an individual to enroll there.",
                [],
            ),
            (
                "university-transfer",
                "Transfer and examination credit",
                "Transfer credit needs official final transcripts, departmental equivalency/application review, and C− or better (including pass marks certified equivalent). No transfer math below Calculus I, English-language courses, career-preparation/first-year seminars or algebra-based physics. AP/IB credit applies only with home-unit approval; IB credit is restricted to Higher Level exams. Approved non-equivalent courses may count as electives or breadth where appropriate.",
                [],
            ),
            (
                "university-qpa-exception",
                "University graduation QPA exception",
                "University graduation rules allow a post-first-year QPA of at least 2.0 when a first-year entrant’s first-year grades alone cause cumulative QPA below 2.0. The transcript retains all grades; additional program QPA rules may apply, so SCS adviser confirmation is needed.",
                [],
            ),
            (
                "university-completion",
                "Certification, catalog and time limits",
                "Use applicable matriculation-catalog requirements and any approved College Council modifications. Standard study is eight semesters; earlier or longer completion is certified on meeting primary-degree requirements with adviser consultation. All degree units must be earned within eight years of award unless the dean grants a course-specific, time-bounded waiver based on currency, preparation and legitimate delay.",
                [],
            ),
            (
                "university-residence",
                "University residence and diploma conditions",
                "At least four full-time semesters or part-time equivalent and 180 units must be completed at CMU; exceptions require the home dean. Residence/course requirements, applicable QPA and financial obligations must be satisfied. These overlap the SCS graduation policy rather than adding units.",
                [],
            ),
        ],
    )


def parse_thesis(html):
    soup = BeautifulSoup(html, "html.parser")
    words = text(soup)
    for marker in [
        "Honors Research Thesis",
        "36 units",
        "18 units per semester",
        "no specific QPA requirement",
        "at least a 3.5 QPA",
        "3-4 pages",
        "start of the senior year",
        "07-400",
        "12 units",
    ]:
        if marker not in words:
            raise ValueError("CMU thesis policy changed: " + marker)
    return payload(
        PID + "-thesis-policy",
        [
            (
                "thesis-eligibility",
                "Optional honors thesis application",
                "Optional program: an SCS faculty adviser endorses a three-to-four-page prospectus describing the problem, significance, research plan/timeline and bibliography, with short abstract and adviser signature/email. Submit by senior-year start; junior-year submission is encouraged. There is no fixed QPA admission cutoff; 3.5 in relevant core topics is an expectation for success.",
                [],
            ),
            (
                "thesis-completion",
                "Optional honors thesis deliverables",
                "Normally 36 units over senior year (18 each semester), with a prior-work/progress paper, December poster, year-end poster and oral presentation, and written thesis. Optional 07-300 (9 units) and 07-400 practicum (12 units) prepare for research; practicum units may count toward the 36 thesis units when beginning that thesis. The major limits how thesis units fill electives.",
                [],
            ),
        ],
    )
