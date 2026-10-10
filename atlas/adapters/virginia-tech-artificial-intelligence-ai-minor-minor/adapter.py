"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'virginia-tech-artificial-intelligence-ai-minor-minor'
SOURCES = ('https://website.cs.vt.edu/academic/undergraduate/ai-minor.html',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence (AI)', award='minor', kind='minor', aliases=(), award_terms=())
