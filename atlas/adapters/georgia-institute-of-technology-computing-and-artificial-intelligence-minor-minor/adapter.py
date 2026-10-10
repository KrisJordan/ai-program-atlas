"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'georgia-institute-of-technology-computing-and-artificial-intelligence-minor-minor'
SOURCES = ('https://catalog.gatech.edu/programs/minor-computing-artificial-intelligence/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Computing and Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
