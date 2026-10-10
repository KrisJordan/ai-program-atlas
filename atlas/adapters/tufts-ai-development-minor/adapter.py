"""Observed Tufts minor core, electives and source policies."""

from atlas.adapters.tufts_ai_curriculum import parse_minor

PROGRAM_ID = "tufts-ai-development-minor"
SOURCES = [
    "https://engineering.tufts.edu/cs/current-students/undergraduate/minor-ai-development",
    "https://ai.tufts.edu/ai-tufts/programs-and-courses",
]


def parse(html: str) -> dict:
    return parse_minor(
        html, pid=PROGRAM_ID, title="AI Development", url=SOURCES[0], development=True
    )


SOURCES.append("https://engineering.tufts.edu/cs/current-students/undergraduate/student-forms")
