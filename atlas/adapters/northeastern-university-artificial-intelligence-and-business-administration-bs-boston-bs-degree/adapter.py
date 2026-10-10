"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
from atlas.adapters.northeastern_business_concentrations import SOURCE_PARSERS as CONCENTRATION_PARSERS, enrich_degree_observation

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-business-administration-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-business-admnistration-bs-bos/',)

def parse(html: str) -> dict:
    observed = parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Business Administration, BS (Boston)', url=SOURCES[0],
        required_sections=['Artificial Intelligence Courses', 'Business Courses', 'Supporting Courses', 'Business Concentration', 'Business Experiential Learning', 'Program Requirement'],
        outcome_claims=[('the theory and practice of management', 'The program combines technical study with management theory and practice.'), ('collection, manipulation, storage, retrieval, and computational analysis of data', 'Students study how to collect, manage and analyze varied forms of data.')])

    return enrich_degree_observation(observed, html)

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

SOURCES = tuple(SOURCES) + tuple(CONCENTRATION_PARSERS)
SOURCE_PARSERS = {**SOURCE_PARSERS, **CONCENTRATION_PARSERS}
