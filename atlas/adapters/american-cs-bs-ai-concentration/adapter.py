"""Visible official concentration requirements; no automatic completeness claim."""
from atlas.adapters.american_sandiego_concentrations import parse_american

PROGRAM_ID = 'american-cs-bs-ai-concentration'
SOURCE_ID = 'american-cs-bs-ai-concentration-catalog'
SOURCES = ('https://www.american.edu/cas/cs/bs-comp.cfm',)

def parse(html: str) -> dict:
    return parse_american(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])
