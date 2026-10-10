"""Observe program overview facts; catalog inventory remains unresolved."""

from atlas.adapters.buffalo_overview import parse_minor

PROGRAM_ID = "university-at-buffalo-suny-ai-ethics-minor-minor"
TITLE = "AI Ethics"
SOURCES = (
    "https://www.buffalo.edu/cas/philosophy/undergraduate/minor-ai-ethics.html",
    "https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html",
)


def parse(html: str) -> dict:
    return parse_minor(html, PROGRAM_ID, TITLE)
