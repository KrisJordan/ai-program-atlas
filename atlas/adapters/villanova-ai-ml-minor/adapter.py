"""Observed Villanova local curriculum; completeness is reviewer-only."""

from atlas.adapters.villanova_curriculum import parse_program

PROGRAM_ID = "villanova-ai-ml-minor"
SOURCES = [
    "https://live-villanova-catalog.cleancatalog.io/business/artificial-intelligence-and-machine-learning-minor",
    "https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html",
    "https://live-villanova-catalog.cleancatalog.io/",
]


def parse(html: str) -> dict:
    return parse_program(
        html,
        pid=PROGRAM_ID,
        title="Artificial Intelligence and Machine Learning",
        award="minor",
        kind="minor",
        url=SOURCES[0],
    )


from atlas.adapters.villanova_curriculum import parse_course

SOURCE_PARSERS = {SOURCES[0]: parse}
SOURCES.append(
    "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3300"
)
SOURCE_PARSERS[
    "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3300"
] = lambda html: parse_course(
    html,
    pid=PROGRAM_ID,
    code="MIS 3300",
    url="https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3300",
)
SOURCES.append(
    "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-2020"
)
SOURCE_PARSERS[
    "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-2020"
] = lambda html: parse_course(
    html,
    pid=PROGRAM_ID,
    code="MIS 2020",
    url="https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-2020",
)
SOURCES.append(
    "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3080"
)
SOURCE_PARSERS[
    "https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3080"
] = lambda html: parse_course(
    html,
    pid=PROGRAM_ID,
    code="MIS 3080",
    url="https://live-villanova-catalog.cleancatalog.io/management-information-systems/mis-3080",
)

from atlas.adapters import small_complete_metadata as metadata

_parse_requirements = parse


def parse(html):
    result = _parse_requirements(html)
    result.update(metadata.parse_villanova_aim(html))
    return result


SOURCES.append(metadata.VILLANOVA_CSC)
SOURCE_PARSERS[SOURCES[0]] = parse
SOURCE_PARSERS[metadata.VILLANOVA_CSC] = metadata.parse_villanova_csc
