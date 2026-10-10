"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import ds_overview, declaration

PROGRAM_ID = 'william-mary-data-science-ai-specialization'
SOURCES = ('https://cdsp.wm.edu/data-science/degrees/bs_minor/', 'https://cdsp.wm.edu/data-science/degrees/bs_minor/declare-bsdsci/')

def parse(html):
    return ds_overview(html)

def parse_declaration(html):
    return declaration(html, PROGRAM_ID, applied=False)

SOURCE_PARSERS = {SOURCES[0]: parse, SOURCES[1]: parse_declaration}
