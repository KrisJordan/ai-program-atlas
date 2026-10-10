"""Source-specific identity observation; curriculum extraction pending."""
from atlas.adapters.final_discovery_common import parse_claims

PROGRAM_ID = 'stony-brook-ai-data-science-specialization'
SOURCES = ('https://www.stonybrook.edu/sb/bulletin/current-fall24/academicprograms/cse/degreesandrequirements.php',)
IDENTITY = {'program_id': 'stony-brook-ai-data-science-specialization', 'title': 'Artificial Intelligence and Data Science', 'award': 'concentration', 'kind': 'concentration', 'heading': 'Requirements for the Major and Minor in Computer Science', 'claims': ['Specialization in Artificial Intelligence and Data Science', 'declare their participation in the specialization']}

def parse(html: str) -> dict:
    return parse_claims(html, **IDENTITY)
