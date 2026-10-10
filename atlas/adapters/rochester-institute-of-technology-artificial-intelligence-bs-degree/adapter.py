"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'rochester-institute-of-technology-artificial-intelligence-bs-degree'
SOURCES = ('https://www.rit.edu/study/artificial-intelligence-bs',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='BS', kind='degree', aliases=(), award_terms=())
