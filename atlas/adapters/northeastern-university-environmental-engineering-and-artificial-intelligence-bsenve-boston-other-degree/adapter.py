"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-environmental-engineering-and-artificial-intelligence-bsenve-boston-other-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/engineering/civil-environmental/environmental-engineering-artificial-intelligence-bsenve/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Environmental Engineering and Artificial Intelligence, BSEnvE (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Engineering Requirements', 'Artificial Intelligence Major Requirements', 'Supporting Courses: Mathematics/Science', 'Professional Development', 'Writing Requirements', 'Integrative Course', 'General Electives', 'Engineering GPA Requirement', 'Program Requirement'], outcome_claims=[('acquire data analytics and machine learning skills', 'Students develop data analytics and machine-learning skills for environmental engineering applications.')], **{'award_level': 'other'})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_cive_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='CIVE', heading='Civil and Environmental Engineering (CIVE)', codes=['CIVE 2221', 'CIVE 2222', 'CIVE 2300', 'CIVE 2301', 'CIVE 2331', 'CIVE 2334', 'CIVE 3435', 'CIVE 4534', 'CIVE 4535', 'CIVE 4765', 'CIVE 4540', 'CIVE 4777', 'CIVE 5100', 'CIVE 5150', 'CIVE 5250', 'CIVE 5255', 'CIVE 5260', 'CIVE 5261', 'CIVE 5271', 'CIVE 5275', 'CIVE 5280', 'CIVE 5281', 'CIVE 5363', 'CIVE 5365', 'CIVE 5366', 'CIVE 5368', 'CIVE 5369', 'CIVE 5536', 'CIVE 5670', 'CIVE 5699', 'CIVE 3430'], url='https://catalog.northeastern.edu/course-descriptions/cive/')


def parse_ge_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='GE', heading='General Engineering (GE)', codes=['GE 3300', 'GE 1501', 'GE 1502', 'GE 1000'], url='https://catalog.northeastern.edu/course-descriptions/ge/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/engineering/civil-environmental/environmental-engineering-artificial-intelligence-bsenve/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/cive/', 'https://catalog.northeastern.edu/course-descriptions/ge/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/cive/': parse_cive_metadata, 'https://catalog.northeastern.edu/course-descriptions/ge/': parse_ge_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341', 'MATH 1342', 'MATH 2321', 'MATH 2341', 'MATH 3081'], 'CS': ['CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 3302', 'ENGW 3303', 'ENGW 3315'], 'PHYS': ['PHYS 1151', 'PHYS 1152', 'PHYS 1153']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'CHEM': ['CHEM 1151', 'CHEM 1153']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EEMB': ['EEMB 3455'], 'ENVR': ['ENVR 1200', 'ENVR 2200', 'ENVR 3125', 'ENVR 3200', 'ENVR 3600']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'ENCP': ['ENCP 2000', 'ENCP 3000']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_REMAINING_SUBJECT_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_REMAINING_SUBJECT_METADATA}
