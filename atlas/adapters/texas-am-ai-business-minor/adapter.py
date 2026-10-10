"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'texas-am-ai-business-minor'
SOURCES = ('https://catalog.tamu.edu/undergraduate/business/artificial-intelligence-business-minor/',)
IDENTITY = {'program_id': 'texas-am-ai-business-minor', 'title': 'Artificial Intelligence in Business', 'award': 'minor', 'kind': 'minor', 'heading': 'Artificial Intelligence in Business', 'claims': ['Artificial Intelligence in Business minor for undergraduate students']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
