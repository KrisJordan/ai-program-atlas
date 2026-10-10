"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'william-mary-data-science-ai-specialization'
SOURCES = ('https://cdsp.wm.edu/data-science/degrees/bs_minor/',)
IDENTITY = {'program_id': 'william-mary-data-science-ai-specialization', 'title': 'Artificial Intelligence', 'award': 'concentration', 'kind': 'concentration', 'heading': 'Bachelors of Science & Minor in Data Science', 'content_header_class': 'm-title', 'claims': ['Choose one track', 'Artificial Intelligence']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
