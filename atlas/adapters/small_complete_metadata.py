"""Bounded source-specific metadata observations; never promote review completeness."""

import re
from bs4 import BeautifulSoup

TAMU_URL = "https://catalog.tamu.edu/undergraduate/course-descriptions/busn/"
OSU_URL = "https://cse.osu.edu/courses"
DENISON_ABOUT = "https://denison.edu/academics/machine-learning-and-artificial-intelligence/about"
DENISON_HOME = "https://denison.edu/academics/machine-learning-and-artificial-intelligence"
DENISON_CATALOG = "https://catalog.denison.edu/catalog/courses-of-study/machine-learning/"
VILLANOVA_CSC = "https://live-villanova-catalog.cleancatalog.io/computing-sciences/csc-1052"


def text(node):
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""


def body(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup, text(soup.find("main") or soup.find(id="content") or soup)


TAMU_SUMMARIES = {
    "BUSN 250": (
        "building custom AI tools",
        "Uses generative AI across business functions, including practical tool building and ethical considerations.",
    ),
    "BUSN 255": (
        "visualization principles",
        "Uses visual analytics and varied datasets to communicate business findings through dashboards and Python.",
    ),
    "BUSN 460": (
        "managing machine learning projects",
        "Connects machine-learning concepts with business applications and project leadership.",
    ),
    "BUSN 465": (
        "autonomous, goal-driven",
        "Examines autonomous AI agent design, business applications and deployment risks.",
    ),
    "BUSN 470": (
        "focus on business text",
        "Applies generative and agentic AI to business text through practical team-oriented work.",
    ),
}
OSU_SUMMARIES = {
    "CSE 3521": (
        "knowledge representation",
        "Surveys AI problem solving, knowledge representation and machine learning.",
    ),
    "CSE 5523": (
        "clustering and data representation",
        "Introduces classification, clustering, data representation and their theoretical analysis.",
    ),
    "CSE 5524": (
        "image formation",
        "Studies visual features, segmentation, shape, tracking and motion for interactive systems.",
    ),
    "CSE 5525": (
        "speech synthesis",
        "Builds systems for written and spoken language using NLP, recognition and synthesis.",
    ),
    "CSE 5526": (
        "radial-basis function networks",
        "Surveys perceptrons, radial-basis models, support-vector machines and recurrent networks.",
    ),
    "CSE 5243": (
        "graph and network analysis",
        "Covers data preparation, classification, clustering, anomalies and network analysis; assumes programming preparation.",
    ),
    "CSE 5914": (
        "teamwork, written and oral communication",
        "Develops knowledge-based systems through a team design project with technical and communication work.",
    ),
}


def parse_tamu_courses(html):
    soup, full = body(html)
    if "BUSN - Mays Business School" not in full:
        raise ValueError("TAMU BUSN catalog identity missing")
    courses = []
    for block in soup.select(".courseblock"):
        heading = text(block.select_one(".courseblocktitle"))
        match = re.match(r"(BUSN \d{3}) (.+)", heading)
        if not match or match[1] not in TAMU_SUMMARIES:
            continue
        code, title = match.groups()
        raw = text(block.select_one(".courseblockdesc"))
        credit = re.search(r"Credits (\d+)\.", raw)
        guard, summary = TAMU_SUMMARIES[code]
        if not credit or guard not in raw:
            raise ValueError("TAMU course metadata changed: " + code)
        prereq = re.search(r"Prerequisites?:\s*(.+)", raw)
        courses.append(
            {
                "id": "tamu-" + code.lower().replace(" ", "-"),
                "code": code,
                "name": title,
                "description": summary,
                "prerequisites": prereq[1] if prereq else None,
                "credits": int(credit[1]),
                "credit_unit": "semester_hours",
                "category": "applications",
                "source_id": "tamu-busn-course-catalog",
                "url": TAMU_URL,
                "public_site": None,
                "syllabus": None,
            }
        )
    if {c["code"] for c in courses} != set(TAMU_SUMMARIES) or len(courses) != 5:
        raise ValueError("Expected all five distinct TAMU minor courses")
    return {"id": "texas-am-ai-business-minor", "courses": courses}


def parse_osu_courses(html):
    soup, _ = body(html)
    heading = soup.find("h1")
    if text(heading) != "Courses":
        raise ValueError("Ohio State course directory heading missing")
    courses = []
    for block in soup.select("details.coe-accordion"):
        code = text(block.find("summary"))
        if code not in OSU_SUMMARIES:
            continue
        raw = text(block.select_one(".description"))
        match = re.fullmatch(
            r"Description:\s*(.*?)\s+Prereq:\s*(.*?)\s+Units:\s*(\d+(?:\.\d+)?)", raw
        )
        guard, summary = OSU_SUMMARIES[code]
        if not match or guard not in match[1]:
            raise ValueError("Ohio State metadata structure or description changed: " + code)
        courses.append(
            {
                "id": "ohio-state-" + code.lower().replace(" ", "-"),
                "code": code,
                "name": text(block.select_one(".title")),
                "description": summary,
                "prerequisites": match[2],
                "credits": float(match[3]),
                "credit_unit": "unknown",
                "category": "ai_ml",
                "source_id": "ohio-state-course-directory",
                "url": OSU_URL,
                "public_site": None,
                "syllabus": None,
            }
        )
    if {c["code"] for c in courses} != set(OSU_SUMMARIES) or len(courses) != 7:
        raise ValueError("Expected all seven distinct Ohio State AI options")
    return {
        "id": "ohio-state-ai-specialization",
        "courses": courses,
        "notes": [
            "Course-directory observation only; reconcile prerequisite differences with the specialization table before registration. Published Units are not normalized."
        ],
    }


def outcome(text_, source, locator, kind="program_aim"):
    return {
        "text": text_,
        "kind": "source_stated",
        "statement_type": kind,
        "source_id": source,
        "locator": locator,
    }


def parse_denison_about(html):
    _, full = body(html)
    guards = [
        "Departmental Guidelines & Mission Statement",
        "opportunity to implement these algorithms",
        "mathematical principles",
    ]
    if any(g not in full for g in guards):
        raise ValueError("Denison mission statement changed")
    return {
        "id": "denison-mlai-minor",
        "outcomes": [
            outcome(
                "Understand and implement machine learning algorithms to solve practical problems.",
                "denison-mlai-about",
                "Departmental Guidelines & Mission Statement",
            )
        ],
    }


def parse_denison_home(html):
    _, full = body(html)
    guards = [
        "Machine Learning & Artificial Intelligence",
        "Communicate effectively",
        "technical and non-technical audiences",
        "advanced graduate study in artificial intelligence",
    ]
    if any(g not in full for g in guards):
        raise ValueError("Denison program aims or career context changed")
    return {
        "id": "denison-mlai-minor",
        "outcomes": [
            outcome(
                "Explain machine-learning methods and results to technical and nontechnical audiences.",
                "denison-mlai-home",
                "Communicate effectively",
            ),
            outcome(
                "Prepare for work applying machine learning across industries and for graduate study in AI.",
                "denison-mlai-home",
                "Jobs as a machine learning & artificial intelligence major",
                "career_pathway",
            ),
        ],
    }


def parse_denison_prerequisites(html):
    soup, full = body(html)
    if "Machine Learning & AI (ML)" not in full:
        raise ValueError("Denison catalog identity missing")
    aliases = {
        "ML 240": ("denison-ml-cs-240", "ML/CS 240"),
        "ML 310": ("denison-ml-310-math-428", "ML 310/MATH 428"),
        "ML 400": ("denison-ml-400", "ML 400"),
    }
    rows = []
    for block in soup.select(".courseblock"):
        match = re.match(r"(ML \d{3}) - ", text(block.select_one(".courseblocktitle")))
        if not match or match[1] not in aliases:
            continue
        pr = next(
            (
                text(p).removeprefix("Prerequisite(s):").strip()
                for p in block.select(".courseblockextra")
                if text(p).startswith("Prerequisite(s):")
            ),
            None,
        )
        if not pr:
            raise ValueError("Denison prerequisite wording missing")
        cid, code = aliases[match[1]]
        rows.append(
            {
                "id": cid,
                "code": code,
                "prerequisites": pr,
                "source_id": "denison-mlai-catalog",
                "url": DENISON_CATALOG,
            }
        )
    if len(rows) != 3:
        raise ValueError("Expected three Denison prerequisite observations")
    return {
        "id": "denison-mlai-minor",
        "courses": rows,
        "notes": [
            "Exact source conjunctions retained; their and/or grouping remains unresolved, not converted into an eligibility rule."
        ],
    }


def parse_villanova_csc(html):
    from atlas.adapters.villanova_curriculum import parse_course

    result = parse_course(html, pid="villanova-ai-ml-minor", code="CSC 1052", url=VILLANOVA_CSC)
    _, full = body(html)
    if (
        "inheritance, interfaces, polymorphism" not in full
        or "dynamically linked structures" not in full
    ):
        raise ValueError("CSC1052 description changed")
    result["courses"][0]["description"] = (
        "Develops object-oriented design, recursion and linked data structures, including stacks, queues, trees and maps."
    )
    return result


def parse_villanova_aim(html):
    _, full = body(html)
    if (
        "Artificial Intelligence and Machine Learning Minor" not in full
        or "building prototype intelligent systems" not in full
        or "supervised and unsupervised learning" not in full
    ):
        raise ValueError("Villanova minor overview changed")
    return {
        "id": "villanova-ai-ml-minor",
        "outcomes": [
            outcome(
                "Explore intelligent-system prototypes, language processing, expert systems, machine learning and robotics in a business-oriented minor.",
                "villanova-ai-ml-minor-identity",
                "About: coursework overview",
            )
        ],
    }


def parse_tamu_aim(html):
    _, full = body(html)
    if (
        "Artificial Intelligence in Business - Minor" not in full
        or "foundation required to efficiently and effectively utilize AI and ML" not in full
    ):
        raise ValueError("TAMU minor overview changed")
    return {
        "id": "texas-am-ai-business-minor",
        "outcomes": [
            outcome(
                "Apply AI and machine learning in business work.",
                "texas-am-ai-business-minor-identity",
                "Program overview",
            )
        ],
    }
