"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'emory-university-cs-bs-ai-concentration-concentration-concentration'
SOURCES = ('https://computerscience.emory.edu/undergraduate/degrees-and-requirements/cs-bs-ai-concentration.html',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='CS BS, AI Concentration', award='concentration', kind='concentration', aliases=('AI Concentration', 'Artificial Intelligence Concentration'), award_terms=())
