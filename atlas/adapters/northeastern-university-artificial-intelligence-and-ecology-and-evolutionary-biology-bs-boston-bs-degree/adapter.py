"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-ecology-and-evolutionary-biology-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-ecology-evolutionary-biology-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Ecology and Evolutionary Biology, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Coursework', 'Ecology and Evolutionary Biology Coursework', 'Ecology and Evolutionary Biology Topical Requirement', 'Supporting Courses', 'Writing Requirement', 'Integrative Requirement', 'Required General Electives', 'Science GPA Requirement (Ecology and Evolutionary Biology)', 'NUpath Requirements Satisfied', 'Program Requirement'],
        outcome_claims=[('critical thinking and creativity in scientific problem solving', 'The interdisciplinary program aims to develop critical and creative scientific reasoning.'), ('population, community, and ecosystem ecology', 'The program develops knowledge of ecology, evolution and their computational study.')],
        pooled_subheaders=[],
        overview_rules=[('cannot combine majors in biology', 'Program combination restrictions', 'This combined major cannot be combined with majors in biology, marine biology, or environmental and sustainability sciences, or with minors in biology, marine science, or environmental and sustainability sciences.')])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420'], url='https://catalog.northeastern.edu/course-descriptions/ds/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-ecology-evolutionary-biology-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}
