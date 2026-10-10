"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'case-western-reserve-university-artificial-intelligence-minor-minor'
SOURCES = ('https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-minor/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
