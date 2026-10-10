"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-journalism-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-journalism-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Journalism, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Courses', 'Journalism Major Requirements', 'Supporting Courses', 'Writing Requirement', 'Integrative Requirement', 'Required General Electives', 'NUpath Requirements Satisfied', 'Journalism GPA Requirement', 'Program Requirement'], outcome_claims=[('utilize it in effective investigative reporting', 'Students learn to interpret large information flows for investigative journalism.')], **{'conditional_tables': {('Journalism Major Requirements', 1): ('Students transferring from outside institutions', ('JRNL 2201', 'JRNL 2301', 'JRNL 4650'), 'Transfer students need at least five four-semester-hour JRNL courses at Northeastern, including JRNL 2201, JRNL 2301 and JRNL 4650.')}})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420', 'DS 1300'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_jrnl_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='JRNL', heading='Journalism (JRNL)', codes=['JRNL 1000', 'JRNL 1101', 'JRNL 1102', 'JRNL 2201', 'JRNL 2301', 'JRNL 3610', 'JRNL 1150', 'JRNL 3550', 'JRNL 4650', 'JRNL 3700', 'JRNL 5500'], url='https://catalog.northeastern.edu/course-descriptions/jrnl/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-journalism-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/jrnl/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/jrnl/': parse_jrnl_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}
