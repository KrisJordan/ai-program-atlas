"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'case-western-reserve-university-artificial-intelligence-ba-degree'
SOURCES = ('https://case.edu/ai/education/degree-programs-certificates',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='BA', kind='degree', aliases=(), award_terms=())
