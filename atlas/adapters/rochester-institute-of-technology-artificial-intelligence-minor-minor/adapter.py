"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'rochester-institute-of-technology-artificial-intelligence-minor-minor'
SOURCES = ('https://www.rit.edu/study/artificial-intelligence-minor',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
