"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'stevens-institute-of-technology-artificial-intelligence-minor-minor'
SOURCES = ('https://stevens.catalog.prod.coursedog.com/programs/9a968dad026510010633ba4bf9db0000',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
