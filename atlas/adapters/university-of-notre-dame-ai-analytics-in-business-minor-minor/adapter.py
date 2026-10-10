"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-notre-dame-ai-analytics-in-business-minor-minor'
SOURCES = ('https://mendoza.nd.edu/undergraduate/ai-analytics-in-business/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='AI Analytics in Business', award='minor', kind='minor', aliases=(), award_terms=())
