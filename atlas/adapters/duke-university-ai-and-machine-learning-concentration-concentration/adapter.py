"""Reviewed source-specific observations; no automatic completeness promotion."""

from atlas.adapters.concentrations_2026 import parse_duke_concentration, parse_duke_substitutions

PROGRAM_ID = "duke-university-ai-and-machine-learning-concentration-concentration"
SOURCES = (
    "https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml",
    "https://cs.duke.edu/undergraduate/courses/substitutions",
)


def parse(html: str) -> dict:
    return parse_duke_concentration(
        html,
        PROGRAM_ID,
        "duke-university-ai-and-machine-learning-concentration-concentration-official",
        SOURCES[0],
    )


def parse_policy(html: str) -> dict:
    from atlas.adapters.duke_substitution_details import parse as parse_details

    return parse_details(html, PROGRAM_ID, "duke-ai-concentration-substitutions", SOURCES[1])


SOURCE_PARSERS = {SOURCES[1]: parse_policy}


from atlas.adapters.duke_public_policies import (
    GRADES_URL,
    TRANSFER_URL,
    parse_grades,
    parse_transfer,
)

SOURCES += (GRADES_URL, TRANSFER_URL)
SOURCE_PARSERS.update(
    {
        GRADES_URL: lambda html: parse_grades(html, PROGRAM_ID),
        TRANSFER_URL: lambda html: parse_transfer(html, PROGRAM_ID),
    }
)

from atlas.adapters.duke_public_policies import (
    TRINITY_SU_URL,
    TRINITY_TRANSFER_URL,
    parse_trinity_su,
    parse_trinity_transfer,
)

SOURCES += (TRINITY_SU_URL, TRINITY_TRANSFER_URL)
SOURCE_PARSERS.update(
    {
        TRINITY_SU_URL: lambda html: parse_trinity_su(html, PROGRAM_ID),
        TRINITY_TRANSFER_URL: lambda html: parse_trinity_transfer(html, PROGRAM_ID),
    }
)
