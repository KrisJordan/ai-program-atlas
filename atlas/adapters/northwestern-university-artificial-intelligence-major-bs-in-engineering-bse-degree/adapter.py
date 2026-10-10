"""Source-specific AI major curriculum observations; degree-wide coverage is partial."""
from atlas.adapters.northwestern_ai_degree import parse_northwestern

PROGRAM_ID = 'northwestern-university-artificial-intelligence-major-bs-in-engineering-bse-degree'
SOURCES = ('https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-major/',)

def parse(html):
    return parse_northwestern(html, PROGRAM_ID, SOURCES[0])
