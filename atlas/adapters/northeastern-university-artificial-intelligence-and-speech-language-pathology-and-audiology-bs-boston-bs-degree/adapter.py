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
