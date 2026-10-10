"""Observed Tufts minor core, electives and source policies."""

from atlas.adapters.tufts_ai_curriculum import parse_minor

PROGRAM_ID = "tufts-application-ai-minor"
SOURCES = [
    "https://engineering.tufts.edu/cs/current-students/undergraduate/minor-application-ai",
    "https://ai.tufts.edu/ai-tufts/programs-and-courses",
]


def parse(html: str) -> dict:
    return parse_minor(
        html, pid=PROGRAM_ID, title="Application of AI", url=SOURCES[0], development=False
    )


SOURCES.append("https://engineering.tufts.edu/cs/current-students/undergraduate/student-forms")


from atlas.adapters.tufts_minor_paperwork import parse_paperwork, URL as PAPERWORK_URL

SOURCES.extend(["https://tufts.box.com/v/cs-minor-appai-checklist", PAPERWORK_URL])
SOURCE_PARSERS = {
    SOURCES[0]: parse,
    PAPERWORK_URL: lambda html: parse_paperwork(html, pid=PROGRAM_ID),
}
