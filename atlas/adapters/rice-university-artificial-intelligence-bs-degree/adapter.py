"""Source-specific AI major curriculum observations; degree-wide coverage is partial."""
from atlas.adapters.rice_ai_degree import parse_rice

PROGRAM_ID = 'rice-university-artificial-intelligence-bs-degree'
SOURCES = ('https://ga.rice.edu/programs-study/departments-programs/engineering/artificial-intelligence/artificial-intelligence-bs/',)

def parse(html):
    return parse_rice(html, PROGRAM_ID, SOURCES[0])
