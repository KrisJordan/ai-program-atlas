"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-iowa-artificial-intelligence-theory-methods-and-applications-minor-minor'
SOURCES = ('https://catalog.registrar.uiowa.edu/engineering/electrical-computer-engineering/artificial-intelligence-theory-methods-applications-minor/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence: Theory, Methods, and Applications', award='minor', kind='minor', aliases=(), award_terms=())
