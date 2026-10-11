"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import ai_minor, declaration

PROGRAM_ID = 'william-mary-ai-minor'
SOURCES = ('https://cdsp.wm.edu/academics/undergraduate/ai-minor/',)

def parse(html):
    return ai_minor(html)

from atlas.adapters.william_mary_public_policies import ADVISING, parse_advising

def parse_public_policies(html):
    return parse_advising(html, PROGRAM_ID)

SOURCE_PARSERS = {SOURCES[0]: parse}
SOURCES = SOURCES + (ADVISING,)
SOURCE_PARSERS[ADVISING] = parse_public_policies
