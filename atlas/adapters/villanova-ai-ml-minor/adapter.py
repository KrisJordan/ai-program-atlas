"""Source-scoped identity observation; curriculum review remains pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'villanova-ai-ml-minor'
SOURCES = ['https://live-villanova-catalog.cleancatalog.io/business/artificial-intelligence-and-machine-learning-minor', 'https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html', 'https://live-villanova-catalog.cleancatalog.io/']


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Machine Learning', award='minor', kind='minor')
