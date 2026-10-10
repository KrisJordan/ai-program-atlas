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


from atlas.adapters.tufts_minor_paperwork import parse_paperwork, URL as PAPERWORK_URL

SOURCES.extend(["https://tufts.box.com/v/cs-minor-aidev-checklist", PAPERWORK_URL])
SOURCE_PARSERS = {
    SOURCES[0]: parse,
    PAPERWORK_URL: lambda html: parse_paperwork(html, pid=PROGRAM_ID),
}
