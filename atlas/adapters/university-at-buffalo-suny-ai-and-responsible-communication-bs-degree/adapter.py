"""Observe program overview facts; catalog inventory remains unresolved."""

from atlas.adapters.buffalo_overview import FAMILY_URL, parse_degree, parse_family

PROGRAM_ID = "university-at-buffalo-suny-ai-and-responsible-communication-bs-degree"
TITLE = "AI and Responsible Communication"
SOURCES = (
    "https://www.buffalo.edu/undergrad-programs/ai-and-responsible-communication.html",
    FAMILY_URL,
    "https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html",
)


def parse(html: str) -> dict:
    return parse_degree(html, PROGRAM_ID, TITLE, SOURCES[0])


def parse_components(html: str) -> dict:
    return parse_family(html, PROGRAM_ID, TITLE)


SOURCE_PARSERS = {SOURCES[0]: parse, FAMILY_URL: parse_components}
