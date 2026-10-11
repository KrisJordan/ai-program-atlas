"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import cs_concentration, declaration

PROGRAM_ID = 'william-mary-cs-ai-ml-concentration'
SOURCES = ('https://cdsp.wm.edu/computerscience/undergraduate/bachelor-of-science-b.s-in-computer-science.php?mapstat=1',)

def parse(html):
    return cs_concentration(html)

from atlas.adapters.william_mary_public_policies import ADVISING, parse_advising

def parse_public_policies(html):
    return parse_advising(html, PROGRAM_ID)

SOURCE_PARSERS = {SOURCES[0]: parse}
SOURCES = SOURCES + (ADVISING,)
SOURCE_PARSERS[ADVISING] = parse_public_policies
