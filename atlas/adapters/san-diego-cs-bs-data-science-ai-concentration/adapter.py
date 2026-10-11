"""Visible official concentration requirements; no automatic completeness claim."""
from atlas.adapters.american_sandiego_concentrations import parse_sandiego

PROGRAM_ID = 'san-diego-cs-bs-data-science-ai-concentration'
SOURCE_ID = 'san-diego-cs-bs-data-science-ai-concentration-catalog'
SOURCES = ('https://undergraduate.catalog.sandiego.edu/programs/major-BS_ENGR-UG-M-EN-BS-COMS/program-requirements-ZEsvA',)

def parse(html: str) -> dict:
    return parse_sandiego(html, PROGRAM_ID, SOURCE_ID, SOURCES[0], 'BS')
