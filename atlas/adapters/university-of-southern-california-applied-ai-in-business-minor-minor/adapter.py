"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-southern-california-applied-ai-in-business-minor-minor'
SOURCES = ('https://www.marshall.usc.edu/news/usc-marshall-launches-applied-ai-and-business-minor',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Applied AI in Business', award='minor', kind='minor', aliases=(), award_terms=())
