"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-speech-language-pathology-and-audiology-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-speech-language-pathology-audiology-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Speech-Language Pathology and Audiology, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Requirements', 'Speech-Language Pathology and Audiology Requirements', 'Math and Statistics Courses', 'Supporting Science Courses', 'Ethics Requirement', 'Integrative Requirement', 'Writing Requirements', 'Required General Electives', 'NUpath Requirements Satisfied', 'Program Requirement'], outcome_claims=[('critical thinking, information literacy, and oral and written communication skills', 'The curriculum aims to develop critical reasoning, information literacy and communication skills.')], **{})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_slpa_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='SLPA', heading='Speech-Language Pathology and Audiology (SLPA)', codes=['SLPA 2000', 'SLPA 1101', 'SLPA 1102', 'SLPA 1103', 'SLPA 1200', 'SLPA 1203', 'SLPA 1205', 'SLPA 4219', 'SLPA 4500', 'SLPA 4651', 'SLPA 5107'], url='https://catalog.northeastern.edu/course-descriptions/slpa/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-speech-language-pathology-audiology-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/slpa/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/slpa/': parse_slpa_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 4120']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3306', 'ENGW 3315'], 'PHYS': ['PHYS 1145', 'PHYS 1146'], 'PHIL': ['PHIL 1145']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'BIOL': ['BIOL 2217', 'BIOL 2218']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EECE': ['EECE 2160', 'EECE 2322', 'EECE 2323'], 'INPR': ['INPR 1000'], 'PHTH': ['PHTH 2210']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'HLTH': ['HLTH 1000']})
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
