"""Visible official concentration requirements; no automatic completeness claim."""
from atlas.adapters.american_sandiego_concentrations import parse_american

PROGRAM_ID = 'american-cs-bs-ai-concentration'
SOURCE_ID = 'american-cs-bs-ai-concentration-catalog'
SOURCES = ('https://www.american.edu/cas/cs/bs-comp.cfm',)

def parse(html: str) -> dict:
    return parse_american(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

from functools import partial
from atlas.adapters.american_sandiego_policies import parse_american_regulations, parse_american_declaration

SOURCE_PARSERS = {
    'https://www.american.edu/provost/undergrad/undergrad-rules-and-regulations.cfm': partial(parse_american_regulations, pid=PROGRAM_ID, source='american-current-undergrad-regulations'),
    'https://www.american.edu/cas/advising/declaring.cfm': partial(parse_american_declaration, pid=PROGRAM_ID, source='american-cas-declaration'),
}
SOURCES += tuple(SOURCE_PARSERS)
