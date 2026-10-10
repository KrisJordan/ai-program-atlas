"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-south-florida-artificial-intelligence-bs-degree'
SOURCES = ('https://www.usf.edu/ai-cybersecurity-computing/academics/undergraduate/bsai.aspx',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='BS', kind='degree', aliases=(), award_terms=())
