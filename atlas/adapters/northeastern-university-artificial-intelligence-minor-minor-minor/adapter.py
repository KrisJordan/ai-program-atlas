"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'northeastern-university-artificial-intelligence-minor-minor-minor'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/data-science/artificial-intelligence-minor/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence, Minor', award='minor', kind='minor', aliases=('Artificial Intelligence',), award_terms=())
