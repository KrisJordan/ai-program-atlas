"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-philosophy-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-philosophy-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Philosophy, BS (Boston)', url=SOURCES[0],
        required_sections=['Artificial Intelligence Requirements', 'Philosophy Requirements', 'Integrative Requirement', 'Supporting Courses', 'Writing Requirement', 'Program Requirement'],
        outcome_claims=[('ability to represent arguments clearly and evaluate them for cogency', 'Students develop formal reasoning and assess the validity of arguments.'), ('ethical and social issues related to data', 'Students examine ethical and social consequences of using data.')])

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 2350']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Complete the reviewed DS selections, preserving one fetch per source URL.
_DS_COMPLETION_METADATA = register_subject_sources(PROGRAM_ID, {'DS': ['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420', 'DS 4440']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DS_COMPLETION_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DS_COMPLETION_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 3302', 'ENGW 3309', 'ENGW 3315'], 'PHIL': ['PHIL 1115', 'PHIL 1145', 'PHIL 4515', 'PHIL 4516', 'PHIL 3050', 'PHIL 1300', 'PHIL 5005', 'PHIL 4050', 'PHIL 5010']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'PHIL': ['PHIL 1000', 'PHIL 1115', 'PHIL 1145', 'PHIL 2325', 'PHIL 2330', 'PHIL 4515', 'PHIL 4516', 'PHIL 1104', 'PHIL 1271', 'PHIL 2155', 'PHIL 2410', 'PHIL 2619', 'PHIL 3492', 'PHIL 3512', 'PHIL 3822', 'PHIL 3050', 'PHIL 1300', 'PHIL 2001', 'PHIL 5005', 'PHIL 4050', 'PHIL 5010']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EECE': ['EECE 2160', 'EECE 2322', 'EECE 2323'], 'INPR': ['INPR 1000']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'AFCS': ['AFCS 1101'], 'EESH': ['EESH 2000'], 'POLS': ['POLS 2325']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_REMAINING_SUBJECT_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_REMAINING_SUBJECT_METADATA}

# Independently public offering-specific CS 2000/2001 resources.
from atlas.adapters.northeastern_course_resources import register_resources
_PUBLIC_CS_RESOURCES = register_resources(PROGRAM_ID)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_PUBLIC_CS_RESOURCES)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_PUBLIC_CS_RESOURCES}

# Explicit degree-plus-subject concurrency, not inferred prerequisites.
from atlas.adapters.northeastern_corequisites import register_cs1802
parse, SOURCE_PARSERS = register_cs1802(parse, SOURCE_PARSERS, PROGRAM_ID)
