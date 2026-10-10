"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree'
SOURCES = ('https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-major/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence Major, BS in Engineering', award='BSE', kind='degree', aliases=('Artificial Intelligence',), award_terms=())
