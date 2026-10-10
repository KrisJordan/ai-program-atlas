"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'new-jersey-institute-of-technology-business-with-ai-bs-degree'
SOURCES = ('https://catalog.njit.edu/undergraduate/management/management/business-with-ai-bs/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Business with AI', award='BS', kind='degree', aliases=(), award_terms=())
