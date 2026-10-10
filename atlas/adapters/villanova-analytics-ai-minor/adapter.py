"""Observed Villanova local curriculum; completeness is reviewer-only."""

from atlas.adapters.villanova_curriculum import parse_program

PROGRAM_ID = "villanova-analytics-ai-minor"
SOURCES = [
    "https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-minor",
    "https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html",
    "https://live-villanova-catalog.cleancatalog.io/",
]


def parse(html: str) -> dict:
    return parse_program(
        html,
        pid=PROGRAM_ID,
        title="Analytics & Artificial Intelligence",
        award="minor",
        kind="minor",
        url=SOURCES[0],
    )


from atlas.adapters.villanova_curriculum import parse_course

SOURCE_PARSERS = {SOURCES[0]: parse}
SOURCES.append("https://live-villanova-catalog.cleancatalog.io/management/mgt-3170")
SOURCE_PARSERS["https://live-villanova-catalog.cleancatalog.io/management/mgt-3170"] = lambda html: (
    parse_course(
        html,
        pid=PROGRAM_ID,
        code="MGT 3170",
        url="https://live-villanova-catalog.cleancatalog.io/management/mgt-3170",
    )
)
SOURCES.append("https://live-villanova-catalog.cleancatalog.io/management/mgt-4170")
SOURCE_PARSERS["https://live-villanova-catalog.cleancatalog.io/management/mgt-4170"] = lambda html: (
    parse_course(
        html,
        pid=PROGRAM_ID,
        code="MGT 4170",
        url="https://live-villanova-catalog.cleancatalog.io/management/mgt-4170",
    )
)
