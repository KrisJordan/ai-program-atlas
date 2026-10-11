"""Observe Denison's published minor requirements without replaying seed data."""
import re

from bs4 import BeautifulSoup

SOURCES = ("https://denison.edu/academics/machine-learning-and-artificial-intelligence/degree-requirements",)
SOURCE_ID = "denison-mlai-requirements"
PROGRAM_ID = "denison-mlai-minor"


def parse(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.get_text(" ", strip=True).split())
    if "Requirements for the minor in Machine Learning and Artificial Intelligence" not in text:
        raise ValueError("Denison minor requirements identity missing")
    if "The following courses are required to complete the minor" not in text:
        raise ValueError("Required-course directive missing")
    courses = []
    for table in soup.find_all("table"):
        observed = []
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"], recursive=False)
            if len(cells) != 2:
                continue
            code, name = [" ".join(c.get_text(" ", strip=True).split()) for c in cells]
            if not re.fullmatch(r"(?:MATH|CS|ML)(?:/(?:MATH|CS))? \d{3}(?:/(?:MATH|CS) \d{3})?", code):
                continue
            category = "ai_ml" if "Machine Learning" in name else "foundations" if code.startswith("CS") else "mathematics"
            observed.append(dict(id="denison-" + re.sub(r"[^a-z0-9]+", "-", code.lower()).strip("-"),
                code=code, name=name, description=None, prerequisites=None, credits=None,
                credit_unit="unknown", category=category, source_id=SOURCE_ID,
                url=SOURCES[0], public_site=None, syllabus=None))
        if observed:
            courses.extend(observed)
    if not courses:
        raise ValueError("No Denison required courses extracted")
    return dict(id="denison-mlai-minor", title="Machine Learning and Artificial Intelligence",
        award_level="minor", program_kind="minor", curriculum_status="partial", courses=courses,
        requirements=[dict(id="denison-mlai-minor-required", parent_id=None,
            title="Required courses", kind="all", count=None, credits=None, credit_unit="unknown",
            category="other", source_id=SOURCE_ID, source_text=None,
            summary="Complete each listed course; cross-listed codes denote the same course.",
            course_ids=[c["id"] for c in courses])],
        notes=["Observed required-course table only. Course credits and prerequisites require separate course-page review."])

from atlas.adapters import small_complete_metadata as metadata

SOURCES += (metadata.DENISON_ABOUT, metadata.DENISON_HOME, metadata.DENISON_CATALOG)
SOURCE_PARSERS = {
    metadata.DENISON_ABOUT: metadata.parse_denison_about,
    metadata.DENISON_HOME: metadata.parse_denison_home,
    metadata.DENISON_CATALOG: metadata.parse_denison_prerequisites,
}
