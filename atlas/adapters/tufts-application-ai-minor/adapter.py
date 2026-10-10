"""Source-scoped identity observation; curriculum review remains pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'tufts-application-ai-minor'
SOURCES = ['https://engineering.tufts.edu/cs/current-students/undergraduate/minor-application-ai', 'https://ai.tufts.edu/ai-tufts/programs-and-courses']


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Application of AI', award='minor', kind='minor')
