"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'cornell-university-artificial-intelligence-minor-minor'
SOURCES = ('https://bowers.cornell.edu/programs/artificial-intelligence-minor',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=(), identity_scopes=('cornell-program-hero',))
