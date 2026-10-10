"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'duke-university-artificial-intelligence-applications-and-implications-minor-minor'
SOURCES = ('https://cs.duke.edu/undergraduate/degrees/minors',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence: Applications and Implications', award='minor', kind='minor', aliases=(), award_terms=())
