"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-biology-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-biology-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Biology, BS (Boston)', url=SOURCES[0],
        required_sections=['Artificial Intelligence Requirements', 'Biology Requirements', 'Integrative Requirements', 'Science GPA Requirement (Biology)', 'Program Requirement'],
        outcome_claims=[('organization and processes of life', 'Students study biological organization and processes from molecular to ecological scales.'), ('software development and algorithms', 'The program develops foundations in biological sciences, mathematics and computing.')])

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}
