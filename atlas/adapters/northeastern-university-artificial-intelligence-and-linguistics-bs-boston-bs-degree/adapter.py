"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-linguistics-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-linguistics-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Linguistics, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Requirements', 'Linguistics Requirements', 'Supporting Courses', 'Integrative Requirement', 'Writing Requirement', 'Required General Electives', 'Science GPA Requirement (Linguistics)', 'NUpath Requirements Satisfied', 'Program Requirement'],
        outcome_claims=[('formal structures of natural (human) languages', 'Students develop knowledge of language structure alongside computational analysis.'), ('computational linguistics, natural language processing, machine learning', 'The catalog identifies computational linguistics, natural language processing and machine learning as preparation areas.')])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_ling_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='LING', heading='Linguistics (LING)', codes=['LING 1150', 'LING 2350', 'LING 3412', 'LING 3420', 'LING 3422', 'LING 3424', 'LING 3450', 'LING 3452', 'LING 4891', 'LING 4991', 'LING 4654'], url='https://catalog.northeastern.edu/course-descriptions/ling/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-linguistics-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/ling/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/ling/': parse_ling_metadata}
