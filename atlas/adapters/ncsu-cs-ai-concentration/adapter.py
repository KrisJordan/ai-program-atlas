"""Source-scoped identity observation; curriculum review remains pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'ncsu-cs-ai-concentration'
SOURCES = ['https://catalog.ncsu.edu/undergraduate/engineering/computer-science/artificial-intelligence-concentration/']


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='concentration', kind='concentration')
