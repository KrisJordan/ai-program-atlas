"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'boston-college-artificial-intelligence-concentration-concentration-concentration'
SOURCES = ('https://www.bc.edu/bc-web/schools/morrissey/departments/computer-science/academics/programs.html',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence Concentration', award='concentration', kind='concentration', aliases=(), award_terms=())
