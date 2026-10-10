"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import ba_overview, declaration

PROGRAM_ID = 'william-mary-applied-ai-ba'
SOURCES = ('https://cdsp.wm.edu/data-science/degrees/ba_appliedai/', 'https://cdsp.wm.edu/data-science/degrees/ba_appliedai/declare-ba-aai/')

def parse(html):
    return ba_overview(html)

def parse_declaration(html):
    return declaration(html, PROGRAM_ID, applied=True)

SOURCE_PARSERS = {SOURCES[0]: parse, SOURCES[1]: parse_declaration}
