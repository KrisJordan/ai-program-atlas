"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'duke-university-machine-learning-artificial-intelligence-minor-minor'
SOURCES = ('https://ece.duke.edu/academics/undergrad/minors/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Machine Learning & Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
