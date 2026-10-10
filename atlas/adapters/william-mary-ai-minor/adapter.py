"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'william-mary-ai-minor'
SOURCES = ('https://cdsp.wm.edu/academics/undergraduate/ai-minor/',)
IDENTITY = {'program_id': 'william-mary-ai-minor', 'title': 'Artificial Intelligence', 'award': 'minor', 'kind': 'minor', 'heading': 'Minoring in Artificial Intelligence', 'claims': ['minor in Artificial Intelligence', 'all majors']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
