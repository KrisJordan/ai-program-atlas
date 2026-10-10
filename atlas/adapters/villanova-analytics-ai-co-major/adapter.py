"""Source-scoped identity observation; curriculum review remains pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'villanova-analytics-ai-co-major'
SOURCES = ['https://live-villanova-catalog.cleancatalog.io/analytics-artificial-intelligence/analytics-artificial-intelligence-comajor', 'https://www.villanova.edu/university/business/academics/undergraduate-programs/degrees.html', 'https://live-villanova-catalog.cleancatalog.io/']


def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Analytics & Artificial Intelligence', award='other', kind='additional_major', award_terms=('Co-Major',))
