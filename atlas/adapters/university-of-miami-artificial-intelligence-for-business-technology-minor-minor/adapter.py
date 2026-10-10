"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-miami-artificial-intelligence-for-business-technology-minor-minor'
SOURCES = ('https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-for-business-technology-minor/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence for Business Technology', award='minor', kind='minor', aliases=(), award_terms=())
