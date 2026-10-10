"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-miami-artificial-intelligence-technologies-for-business-other-degree'
SOURCES = ('https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-tech-for-business-bba/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence Technologies for Business', award='other', kind='degree', aliases=(), award_terms=('Bachelor of Business Administration', 'BBA'))
