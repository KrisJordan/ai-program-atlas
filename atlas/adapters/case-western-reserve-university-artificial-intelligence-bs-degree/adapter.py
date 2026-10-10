"""Source-specific major-table observations; degree-wide inventory remains partial."""
from atlas.adapters.case_ai_degrees import parse_case

PROGRAM_ID = 'case-western-reserve-university-artificial-intelligence-bs-degree'
SOURCES = ('https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-bs/',)

def parse(html):
    return parse_case(html, PROGRAM_ID, 'BS', SOURCES[0])
