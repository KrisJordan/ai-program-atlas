"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-at-buffalo-suny-artificial-intelligence-crime-and-society-minor-minor'
SOURCES = ('https://arts-sciences.buffalo.edu/college/departments-and-programs/social-sciences/ai-society.html',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence, Crime and Society', award='minor', kind='minor', aliases=(), award_terms=())
