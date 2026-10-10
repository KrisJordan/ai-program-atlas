"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-business-admnistration-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Business Administration, BS (Boston)', url=SOURCES[0],
        required_sections=['Artificial Intelligence Courses', 'Business Courses', 'Supporting Courses', 'Business Concentration', 'Business Experiential Learning', 'Program Requirement'],
        outcome_claims=[('the theory and practice of management', 'The program combines technical study with management theory and practice.'), ('collection, manipulation, storage, retrieval, and computational analysis of data', 'Students study how to collect, manage and analyze varied forms of data.')])
