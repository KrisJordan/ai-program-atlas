"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-design-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-design-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Design, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Requirements', 'Design Requirements', 'Design Option', 'Integrative Requirements', 'Supporting Courses', 'Writing Requirements', 'Required General Electives', 'NUpath Requirements Satisfied', 'Program Requirement'],
        outcome_claims=[('visualize concepts and data to enhance human understanding', 'The program connects computational data work with information design that helps people understand complex material.')])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4300', 'DS 4400', 'DS 4200', 'DS 1300'], url='https://catalog.northeastern.edu/course-descriptions/ds/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-design-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200'], 'CY': ['CY 4170', 'CY 5240']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 2350']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Complete the reviewed DS selections, preserving one fetch per source URL.
_DS_COMPLETION_METADATA = register_subject_sources(PROGRAM_ID, {'DS': ['DS 3500', 'DS 3000', 'DS 4300', 'DS 4400', 'DS 4200', 'DS 1300']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DS_COMPLETION_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DS_COMPLETION_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 3302', 'ENGW 3314', 'ENGW 3315'], 'PHIL': ['PHIL 1300', 'PHIL 1145']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EECE': ['EECE 2160', 'EECE 2322'], 'INPR': ['INPR 1000'], 'JRNL': ['JRNL 3700'], 'SOCL': ['SOCL 1280', 'SOCL 2485', 'SOCL 4528']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'ARTF': ['ARTF 1000', 'ARTF 1220', 'ARTF 1200', 'ARTF 1210', 'ARTF 1230', 'ARTF 1240', 'ARTF 1250'], 'ARTG': ['ARTG 1001', 'ARTG 1002', 'ARTG 1270', 'ARTG 1271', 'ARTG 1290', 'ARTG 1291', 'ARTG 4550', 'ARTG 2810', 'ARTG 3810', 'ARTG 3462', 'ARTG 3464', 'ARTG 2252', 'ARTG 3452', 'ARTG 2242', 'ARTG 3444', 'ARTG 2400', 'ARTG 3400', 'ARTG 5330', 'ARTG 5150'], 'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'AFCS': ['AFCS 2600'], 'EEAM': ['EEAM 2000'], 'HIST': ['HIST 2220'], 'INSH': ['INSH 2102']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_REMAINING_SUBJECT_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_REMAINING_SUBJECT_METADATA}

# Independently public offering-specific CS 2000/2001 resources.
from atlas.adapters.northeastern_course_resources import register_resources
_PUBLIC_CS_RESOURCES = register_resources(PROGRAM_ID)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_PUBLIC_CS_RESOURCES)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_PUBLIC_CS_RESOURCES}
