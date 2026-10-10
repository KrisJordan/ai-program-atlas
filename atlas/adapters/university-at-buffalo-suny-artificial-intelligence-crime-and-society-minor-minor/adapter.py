"""Observe program overview facts; catalog inventory remains unresolved."""

from atlas.adapters.buffalo_overview import parse_minor

PROGRAM_ID = "university-at-buffalo-suny-artificial-intelligence-crime-and-society-minor-minor"
TITLE = "Artificial Intelligence, Crime and Society"
SOURCES = (
    "https://arts-sciences.buffalo.edu/sociology-criminology/undergraduate/ai-crime-society.html",
    "https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html",
)


def parse(html: str) -> dict:
    return parse_minor(html, PROGRAM_ID, TITLE)
