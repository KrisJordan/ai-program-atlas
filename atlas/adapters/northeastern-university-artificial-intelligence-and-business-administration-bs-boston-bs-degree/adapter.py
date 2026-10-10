"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Business Administration, BS (Boston)', award='BS', kind='degree', aliases=('Artificial Intelligence and Business Administration, BS',), award_terms=())
