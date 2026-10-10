"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'william-mary-applied-ai-ba'
SOURCES = ('https://cdsp.wm.edu/data-science/degrees/ba_appliedai/',)
IDENTITY = {'program_id': 'william-mary-applied-ai-ba', 'title': 'Applied Artificial Intelligence', 'award': 'BA', 'kind': 'degree', 'heading': 'Major in Applied AI', 'claims': ['BA in Interdisciplinary Studies', 'Major in Applied Artificial Intelligence']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
