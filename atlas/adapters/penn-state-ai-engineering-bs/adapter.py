from functools import partial
from atlas.adapters.psu_university_park_degrees import parse_degree, parse_units, CREDIT_URL
PROGRAM_ID='penn-state-ai-engineering-bs'
SOURCES=('https://bulletins.psu.edu/undergraduate/colleges/engineering/artificial-intelligence-engineering-bs/', CREDIT_URL)
parse=partial(parse_degree,pid=PROGRAM_ID)
SOURCE_PARSERS={SOURCES[0]:parse,CREDIT_URL:partial(parse_units,pid=PROGRAM_ID)}
from atlas.adapters.psu_degree_courses import source_parsers
SOURCE_PARSERS.update(source_parsers(PROGRAM_ID))
SOURCES=tuple(SOURCE_PARSERS)
from atlas.adapters.psu_degree_policy_details import source_parsers as policy_parsers
SOURCE_PARSERS.update(policy_parsers(PROGRAM_ID))
SOURCES=tuple(SOURCE_PARSERS)
from atlas.adapters.psu_university_park_degrees import DEGREE_POLICY_URL, parse_residence_notice
SOURCE_PARSERS[DEGREE_POLICY_URL]=partial(parse_residence_notice,pid=PROGRAM_ID)
SOURCES=tuple(SOURCE_PARSERS)
