"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-psychology-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-psychology-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Psychology, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Requirements', 'Writing Requirements', 'Psychology Requirements', 'Integrative Requirement', 'Required General Electives', 'Psychology GPA Requirement', 'NUpath Requirements Satisfied', 'Combined Major Credit Requirement', 'Program Requirement'],
        outcome_claims=[('study of mind, brain, and behavior', 'Students connect the study of mind and behavior with computational analysis.'), ('skills in machine learning and data analytics', 'Students can extend psychological study through machine learning and data analytics.')])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420'], url='https://catalog.northeastern.edu/course-descriptions/ds/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-psychology-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1365', 'MATH 1465', 'MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 2484']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'PSYC': ['PSYC 1101', 'PSYC 2320', 'PSYC 3450', 'PSYC 3466', 'PSYC 4540']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3307', 'ENGW 3315']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'PSYC': ['PSYC 1101', 'PSYC 2320', 'PSYC 3400', 'PSYC 3402', 'PSYC 3404', 'PSYC 3406', 'PSYC 3450', 'PSYC 3451', 'PSYC 3452', 'PSYC 3458', 'PSYC 3464', 'PSYC 3466', 'PSYC 4600', 'PSYC 4604', 'PSYC 4606', 'PSYC 4610', 'PSYC 4612', 'PSYC 4614', 'PSYC 4616', 'PSYC 4622', 'PSYC 4624', 'PSYC 4628', 'PSYC 4656', 'PSYC 4658', 'PSYC 4660', 'PSYC 4662', 'PSYC 4664', 'PSYC 4666', 'PSYC 4668', 'PSYC 4674', 'PSYC 4676', 'PSYC 4682', 'PSYC 4540']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}
