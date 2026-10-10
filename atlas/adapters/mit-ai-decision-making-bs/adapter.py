"""Source-scoped identity observation; curriculum review remains pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'mit-ai-decision-making-bs'
SOURCES = ['https://catalog.mit.edu/degree-charts/artifical-intelligence-decision-making-course-6-4/', 'https://catalog.mit.edu/degree-charts/']


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Decision Making', award='BS', kind='degree')
