"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'santa-clara-responsible-ai-minor'
SOURCES = ('https://www.scu.edu/bulletin/undergraduate/chapter-5-school-of-engineering/computer-science-and-engineering.html',)
IDENTITY = {'program_id': 'santa-clara-responsible-ai-minor', 'title': 'Responsible Artificial Intelligence', 'award': 'minor', 'kind': 'minor', 'heading': 'Minor in Responsible Artificial Intelligence', 'claims': ['Responsible Artificial Intelligence', 'All undergraduate students are eligible']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
