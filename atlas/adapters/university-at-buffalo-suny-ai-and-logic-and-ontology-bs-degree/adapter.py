"""Observe program overview facts; catalog inventory remains unresolved."""

from atlas.adapters.buffalo_overview import FAMILY_URL, parse_degree, parse_family

PROGRAM_ID = "university-at-buffalo-suny-ai-and-logic-and-ontology-bs-degree"
TITLE = "AI and Logic and Ontology"
SOURCES = (
    "https://www.buffalo.edu/undergrad-programs/ai-and-logic-and-ontology.html",
    FAMILY_URL,
    "https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html",
)


def parse(html: str) -> dict:
    return parse_degree(html, PROGRAM_ID, TITLE, SOURCES[0])


def parse_components(html: str) -> dict:
    return parse_family(html, PROGRAM_ID, TITLE)


SOURCE_PARSERS = {SOURCES[0]: parse, FAMILY_URL: parse_components}

from atlas.adapters.buffalo_public_policies import register as register_public_policies
SOURCES = list(SOURCES)
SOURCE_PARSERS = globals().get("SOURCE_PARSERS", {})
register_public_policies(PROGRAM_ID, SOURCES, SOURCE_PARSERS)
