"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-criminal-justice-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-criminal-justice-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Criminal Justice, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Courses', 'Criminal Justice Courses', 'Integrative Course Requirement', 'Supporting Courses', 'English Requirement', 'Required General Electives', 'NUpath Requirements Satisfied', 'Program Requirement'], outcome_claims=[('apply artificial intelligence skills to crime and justice topics', 'Students learn to apply AI methods to crime and justice questions.')], **{})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 1300'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_crim_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='CRIM', heading='Criminal Justice (CRIM)', codes=['CRIM 1000', 'CRIM 1100', 'CRIM 1110', 'CRIM 1120', 'CRIM 1300', 'CRIM 1400', 'CRIM 1500', 'CRIM 1700', 'CRIM 2310', 'CRIM 2320', 'CRIM 2330', 'CRIM 2350', 'CRIM 2370', 'CRIM 2380', 'CRIM 3010', 'CRIM 3030', 'CRIM 3040', 'CRIM 3050', 'CRIM 3060', 'CRIM 3070', 'CRIM 3100', 'CRIM 3540', 'CRIM 3110', 'CRIM 3120', 'CRIM 3600', 'CRIM 4949', 'CRIM 3700', 'CRIM 4040'], url='https://catalog.northeastern.edu/course-descriptions/crim/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-criminal-justice-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/crim/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/crim/': parse_crim_metadata}
