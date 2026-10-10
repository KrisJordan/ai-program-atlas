"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'ohio-state-ai-specialization'
SOURCES = ('https://cse.osu.edu/bscse-and-bscis-specializations',)
IDENTITY = {'program_id': 'ohio-state-ai-specialization', 'title': 'Artificial Intelligence', 'award': 'concentration', 'kind': 'concentration', 'heading': 'BSCSE and BSCIS Specializations', 'claims': ['Artificial Intelligence', 'All CSE and BSCIS majors are required to take a specialization']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
