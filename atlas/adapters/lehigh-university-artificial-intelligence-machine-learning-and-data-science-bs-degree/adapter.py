"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'lehigh-university-artificial-intelligence-machine-learning-and-data-science-bs-degree'
SOURCES = ('https://engineering.lehigh.edu/cse/academics/undergraduate/bs-ai-ml-ds',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence, Machine Learning and Data Science', award='BS', kind='degree', aliases=(), award_terms=())
