"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import ba_overview, declaration

PROGRAM_ID = 'william-mary-applied-ai-ba'
SOURCES = ('https://cdsp.wm.edu/data-science/degrees/ba_appliedai/', 'https://cdsp.wm.edu/data-science/degrees/ba_appliedai/declare-ba-aai/')

def parse(html):
    return ba_overview(html)

def parse_declaration(html):
    return declaration(html, PROGRAM_ID, applied=True)

SOURCE_PARSERS = {SOURCES[0]: parse, SOURCES[1]: parse_declaration}

from atlas.adapters.william_mary_public_policies import ADVISING, parse_advising

def parse_public_policies(html):
    return parse_advising(html, PROGRAM_ID)

SOURCES = SOURCES + (ADVISING,)
SOURCE_PARSERS[ADVISING] = parse_public_policies

from atlas.adapters.william_mary_ba_policy_review import register as register_ba_public_policies
register_ba_public_policies(SOURCE_PARSERS)
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.william_mary_coll_review import register as register_coll_policies
register_coll_policies(SOURCE_PARSERS)
SOURCES = tuple(SOURCE_PARSERS)

from atlas.adapters.william_mary_course_review import register as register_path_courses
register_path_courses(SOURCE_PARSERS)
SOURCES = tuple(SOURCE_PARSERS)
