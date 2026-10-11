"""Observe UF's GeoAI minor table and separately scoped public minor policies."""
import re
from urllib.parse import urljoin
from bs4 import BeautifulSoup

PROGRAM_ID = "florida-geoai-geographic-analysis-minor"
SOURCE_ID = "florida-geoai-catalog"
SOURCES = (
    "https://catalog.ufl.edu/UGRD/colleges-schools/UGLAS/GAI_UMN/",
    "https://catalog.ufl.edu/UGRD/minors/",
    "https://catalog.ufl.edu/UGRD/colleges-schools/UGLAS/",
    "https://www.advising.ufl.edu/aac-academics/minors/",
)


def clean(node):
    return " ".join(node.get_text(" ", strip=True).split())


def note(suffix, title, summary, source=SOURCE_ID):
    return dict(id=PROGRAM_ID + "-" + suffix, parent_id=None, title=title,
                kind="note", count=None, credits=None, credit_unit="unknown",
                category="other", source_id=source, source_text=None,
                summary=summary, course_ids=[])


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find("h1") or clean(soup.find("h1")) != "GeoAI and Geographic Analysis":
        raise ValueError("UF GeoAI identity missing")
    text = clean(soup)
    if "minor" not in text.lower() or "Required Courses" not in text:
        raise ValueError("Minor requirement identity missing")
    table = soup.find("table", class_="sc_courselist")
    if table is None:
        raise ValueError("Course table missing")
    configurations = {
        "Introductory course": ("intro", "choose_courses", 1, "foundations"),
        "Geographic Techniques courses (select two)": ("techniques", "choose_courses", 2, "systems"),
        "GeoAI and Geographic Analysis courses (select two)": ("analysis", "choose_courses", 2, "applications"),
        "Capstone course": ("capstone", "all", None, "ai_ml"),
    }
    courses, requirements, current = [], [], None
    for row in table.find_all("tr"):
        cells = row.find_all("td", recursive=False)
        if not cells:
            continue
        if "areaheader" in row.get("class", []):
            label = clean(cells[0])
            if label not in configurations:
                raise ValueError("Requirement group changed: " + label)
            suffix, kind, count, category = configurations[label]
            amount = clean(cells[-1])
            current = note(suffix, label, "Published group credits: " + amount + ".")
            current.update(kind=kind, count=count, category=category,
                           credits=int(amount) if amount.isdigit() else None)
            requirements.append(current)
        elif "listsum" in row.get("class", []):
            requirements.append(note("total", "Total minor credits", "Complete " + clean(cells[-1]) + " credits."))
        else:
            link = row.find("a", class_="code")
            if link is None:
                continue
            if current is None or len(cells) < 2:
                raise ValueError("Course outside known group")
            code = clean(link)
            if not re.fullmatch(r"(?:GIS|MET) \d{4}[A-Z]?", code):
                raise ValueError("Unknown course code")
            c = dict(id="florida-" + code.lower().replace(" ", "-"), code=code,
                     name=clean(cells[1]), description=None, prerequisites=None,
                     credits=None, credit_unit="unknown", category=current["category"],
                     source_id=SOURCE_ID, url=urljoin(SOURCES[0], link["href"]),
                     public_site=None, syllabus=None)
            courses.append(c)
            current["course_ids"].append(c["id"])
    if len(requirements) != 5 or [len(r['course_ids']) for r in requirements[:4]] != [2, 5, 7, 1]:
        raise ValueError("Finite option pools changed; review required")
    policies = [
        ("grades", "Minimum course grades", "Completed with minimum grades of C", "Complete minor coursework with C or higher."),
        ("transfer", "Transfer limit", "No more than six transfer credits", "At most six transfer credits may count toward this minor."),
        ("exclusive", "Twelve exclusive credits", "minimum of twelve credits of coursework exclusive", "At least twelve credits must be exclusive to this minor and cannot count toward the major or other minors."),
        ("certificates", "Excluded certificate combinations", "Students pursuing the Certificate of Geographic Artificial Intelligence and Big Data or the Certificate of Geospatial Information Analysis are not eligible", "Students pursuing either Geographic Artificial Intelligence and Big Data or Geospatial Information Analysis certificates are ineligible for this minor."),
    ]
    for suffix, title, guard, summary in policies:
        if guard not in text:
            raise ValueError("Local policy changed: " + suffix)
        requirements.append(note(suffix, title, summary))
    return dict(id=PROGRAM_ID, title="GeoAI and Geographic Analysis", award_level="minor",
                program_kind="minor", curriculum_status="partial", courses=courses,
                requirements=requirements, notes=["Local catalog observation; general minor and home-college policies require separate review. Credit ranges are preserved in summaries."])


def parse_university_policy(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    text = clean(soup)
    guards = ("Applying for a Minor", "approval of the student’s college as well as the college offering the minor", "at least 45 credits", "Students on college probation cannot apply")
    if not all(g in text for g in guards):
        raise ValueError("UF university minor policy scope or rules changed")
    return [note("application", "University application and approval", "Apply for the minor and receive approval from both the home college and the college offering the minor. Approval is required to earn the credential.", "florida-minor-policy"),
            note("university-eligibility", "University application eligibility", "At least 45 earned credits are required to apply. Students on college probation cannot apply.", "florida-minor-policy")]


def parse_clas_policy(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    text = clean(soup)
    guards = ("Liberal Arts and Sciences", "15 semester credits", "At least three courses", "3000 level or above", "no more than three may be individual work", "UF minimum GPA of 2.0", "Be on-track for their major", "certified for the minor at the same time")
    if not all(g in text for g in guards):
        raise ValueError("CLAS minor policy scope or rules changed")
    sid = "florida-clas-policy"
    return [note("clas-structure", "CLAS minor standards", "CLAS minors require at least 15 semester credits with C or higher. At least three courses of at least three credits must be at the 3000 level or above and cannot be individual work; at most three credits of individual work may count.", sid),
            note("clas-eligibility", "CLAS eligibility and timely completion", "The CLAS policy requires an established UF GPA of at least 2.0, on-track status, 45 earned credits, and timely completion. CLAS students apply via ONE.UF and are encouraged to do so before the end of junior year. Other home-college-specific approval conditions remain unreviewed.", sid),
            note("clas-overlap", "CLAS overlap review", "A minor may not inherently overlap the major. The college baseline is six exclusive credits, but this GeoAI minor expressly requires twelve. An AAC advisor reviews the proposed combination; published combination lists are not exhaustive.", sid),
            note("certification", "Certification with the bachelor’s degree", "The offering unit certifies completion, and the minor must be certified at the same time as the bachelor’s degree. Admission to the minor does not guarantee its award.", sid)]
