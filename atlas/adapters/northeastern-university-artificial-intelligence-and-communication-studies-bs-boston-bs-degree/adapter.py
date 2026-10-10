"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-communication-studies-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Communication Studies, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Courses', 'Communication Studies Requirements', 'Integrative Requirement Courses', 'Capstone Experience Course', 'Supporting Courses', 'Required General Electives', 'NUpath Requirements Satisfied', 'Communication Studies Grade Requirement', 'Program Requirement'], outcome_claims=[('major conceptual frameworks for human communication', 'Students develop conceptual knowledge of communication and apply it to social problems.')], **{})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420', 'DS 4440', 'DS 1300'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_comm_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='COMM', heading='Communication Studies (COMM)', codes=['COMM 1101', 'COMM 1112', 'COMM 2301', 'COMM 1210', 'COMM 1225', 'COMM 1231', 'COMM 1255', 'COMM 1131', 'COMM 2303', 'COMM 2304', 'COMM 2501', 'COMM 2551', 'COMM 3200', 'COMM 3201', 'COMM 3230', 'COMM 3304', 'COMM 3320', 'COMM 3415', 'COMM 3500', 'COMM 3501', 'COMM 3530', 'COMM 3532', 'COMM 4535', 'COMM 4605', 'COMM 4631', 'COMM 2625', 'COMM 2941', 'COMM 4608', 'COMM 4625', 'COMM 4901', 'COMM 1000', 'COMM 3409'], url='https://catalog.northeastern.edu/course-descriptions/comm/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-communication-studies-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/comm/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/comm/': parse_comm_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341'], 'CS': ['CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 4120', 'CS 1200', 'CS 1210'], 'CY': ['CY 4170', 'CY 5240']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}
