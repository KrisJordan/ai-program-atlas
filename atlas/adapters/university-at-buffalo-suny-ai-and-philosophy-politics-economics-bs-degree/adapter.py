"""Observe the explicit PPE BS award, program overview and AI+X membership."""

from bs4 import BeautifulSoup
from atlas.adapters.buffalo_overview import FAMILY_URL, parse_degree, parse_family, text

PROGRAM_ID = "university-at-buffalo-suny-ai-and-philosophy-politics-economics-bs-degree"
TITLE = "AI and Philosophy, Politics and Economics"
SOURCES = (
    "https://www.buffalo.edu/undergrad-programs/ai-and-politics-philosophy-economics.html",
    FAMILY_URL,
    "https://arts-sciences.buffalo.edu/philosophy-politics-economics/undergraduate/bs.html",
)


def parse(html: str) -> dict:
    return parse_degree(html, PROGRAM_ID, TITLE, SOURCES[0])


def parse_components(html: str) -> dict:
    return parse_family(html, PROGRAM_ID, TITLE)


def parse_award(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    if not soup.find(lambda n: n.name == "h1" and text(n) == "BS in AI and PPE"):
        raise ValueError("Expected PPE BS heading")
    if "BS in AI and Philosophy, Politics and Economics (PPE)" not in text(soup):
        raise ValueError("Full AI and PPE BS award missing")
    return {"id": PROGRAM_ID, "title": TITLE, "award_level": "BS", "program_kind": "degree"}


SOURCE_PARSERS = {SOURCES[0]: parse, FAMILY_URL: parse_components, SOURCES[2]: parse_award}

from atlas.adapters.buffalo_public_policies import register as register_public_policies
SOURCES = list(SOURCES)
SOURCE_PARSERS = globals().get("SOURCE_PARSERS", {})
register_public_policies(PROGRAM_ID, SOURCES, SOURCE_PARSERS)
