"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-at-buffalo-suny-ai-and-policy-analysis-bs-degree'
SOURCES = ('https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='AI and Policy Analysis', award='BS', kind='degree', aliases=(), award_terms=())
