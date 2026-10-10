"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-philosophy-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-philosophy-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Philosophy, BS (Boston)', url=SOURCES[0],
        required_sections=['Artificial Intelligence Requirements', 'Philosophy Requirements', 'Integrative Requirement', 'Supporting Courses', 'Writing Requirement', 'Program Requirement'],
        outcome_claims=[('ability to represent arguments clearly and evaluate them for cogency', 'Students develop formal reasoning and assess the validity of arguments.'), ('ethical and social issues related to data', 'Students examine ethical and social consequences of using data.')])
