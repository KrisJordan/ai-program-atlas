"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'northeastern-university-interdisciplinary-artificial-intelligence-minor-minor'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/business/interdisciplinary-minors/interdisciplinary-artificial-intelligence-minor/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Interdisciplinary Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
