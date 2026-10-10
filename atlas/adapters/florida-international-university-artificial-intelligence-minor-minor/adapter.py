"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'florida-international-university-artificial-intelligence-minor-minor'
SOURCES = ('https://cec.fiu.edu/news-events/news/2026/new-artificial-intelligence-ai-minor-prepares-fiu-engineering-computing-students-for-an-ai-driven-future.html',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
