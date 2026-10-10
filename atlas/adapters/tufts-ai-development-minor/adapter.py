"""Source-scoped identity observation; curriculum review remains pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'tufts-ai-development-minor'
SOURCES = ['https://engineering.tufts.edu/cs/current-students/undergraduate/minor-ai-development', 'https://ai.tufts.edu/ai-tufts/programs-and-courses']


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='AI Development', award='minor', kind='minor')
