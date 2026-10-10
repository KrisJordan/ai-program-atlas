"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'rochester-ai-concentration'
SOURCES = ('https://www.cs.rochester.edu/undergraduate/bs-requirements.html',)
IDENTITY = {'program_id': 'rochester-ai-concentration', 'title': 'Artificial Intelligence', 'award': 'concentration', 'kind': 'concentration', 'heading': 'BS in Computer Science', 'claims': ['Artificial Intelligence', 'Approved courses for AI concentration']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
