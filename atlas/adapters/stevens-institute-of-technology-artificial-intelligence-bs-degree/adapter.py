"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'stevens-institute-of-technology-artificial-intelligence-bs-degree'
SOURCES = ('https://www.stevens.edu/program/bachelors-degree-in-artificial-intelligence',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='BS', kind='degree', aliases=(), award_terms=())
