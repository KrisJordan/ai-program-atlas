"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'duke-university-ai-and-machine-learning-concentration-concentration'
SOURCES = ('https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='AI and Machine Learning', award='concentration', kind='concentration', aliases=(), award_terms=())
