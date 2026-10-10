"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'georgia-institute-of-technology-applications-of-artificial-intelligence-and-machine-learning-minor-minor'
SOURCES = ('https://catalog.gatech.edu/programs/minor-artificial-intelligence-machine-learning/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Applications of Artificial Intelligence and Machine Learning', award='minor', kind='minor', aliases=(), award_terms=())
