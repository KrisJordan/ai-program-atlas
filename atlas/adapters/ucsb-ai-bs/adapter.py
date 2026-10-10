"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'ucsb-ai-bs'
SOURCES = ('https://ai.cs.ucsb.edu/',)
IDENTITY = {'program_id': 'ucsb-ai-bs', 'title': 'Artificial Intelligence', 'award': 'BS', 'kind': 'degree', 'heading': 'Why AI at UCSB', 'claims': ['Bachelor of Science in Artificial Intelligence']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
