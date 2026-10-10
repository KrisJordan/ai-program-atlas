"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'gonzaga-university-ai-in-engineering-and-applied-science-minor-minor'
SOURCES = ('https://www.gonzaga.edu/school-of-engineering-applied-science/degrees-and-programs/electrical-computer-engineering/ece-tech-minors/ai-minor',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='AI in Engineering and Applied Science', award='minor', kind='minor', aliases=(), award_terms=())
