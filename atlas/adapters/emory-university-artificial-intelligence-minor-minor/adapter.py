"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'emory-university-artificial-intelligence-minor-minor'
SOURCES = ('https://computerscience.emory.edu/undergraduate/degrees-and-requirements/minors.html',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='minor', kind='minor', aliases=('AI Minor',), award_terms=())
