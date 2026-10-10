"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-maryland-college-park-human-centered-ai-ba-degree'
SOURCES = ('https://ai.umd.edu/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Human-Centered AI', award='BA', kind='degree', aliases=(), award_terms=())
