"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import ds_overview, declaration

PROGRAM_ID = 'william-mary-data-science-ai-specialization'
SOURCES = ('https://cdsp.wm.edu/data-science/degrees/bs_minor/', 'https://cdsp.wm.edu/data-science/degrees/bs_minor/declare-bsdsci/')

def parse(html):
    return ds_overview(html)

def parse_declaration(html):
    return declaration(html, PROGRAM_ID, applied=False)

SOURCE_PARSERS = {SOURCES[0]: parse, SOURCES[1]: parse_declaration}

from atlas.adapters.william_mary_public_policies import ADVISING, parse_advising

def parse_public_policies(html):
    return parse_advising(html, PROGRAM_ID)

SOURCES = SOURCES + (ADVISING,)
SOURCE_PARSERS[ADVISING] = parse_public_policies
