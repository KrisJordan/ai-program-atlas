"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'william-mary-cs-ai-ml-concentration'
SOURCES = ('https://cdsp.wm.edu/computerscience/undergraduate/bachelor-of-science-b.s-in-computer-science.php?mapstat=1',)
IDENTITY = {'program_id': 'william-mary-cs-ai-ml-concentration', 'title': 'Artificial Intelligence/Machine Learning', 'award': 'concentration', 'kind': 'concentration', 'heading': 'Bachelor of Science', 'content_header_class': 'm-title', 'claims': ['Artificial Intelligence/Machine Learning', 'must select a concentration']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
