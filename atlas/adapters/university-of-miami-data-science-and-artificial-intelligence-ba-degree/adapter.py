"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-miami-data-science-and-artificial-intelligence-ba-degree'
SOURCES = ('https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/computer-science/data-science-and-ai-ba/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Data Science and Artificial Intelligence', award='BA', kind='degree', aliases=(), award_terms=(), identity_scopes=('miami-title',))
