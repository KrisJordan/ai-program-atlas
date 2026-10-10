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

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341', 'MATH 1231', 'MATH 1241', 'MATH 1245', 'MATH 1340'], 'CS': ['CS 1200', 'CS 1210', 'CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 4520']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 1115', 'ECON 1116']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Complete the reviewed DS selections, preserving one fetch per source URL.
_DS_COMPLETION_METADATA = register_subject_sources(PROGRAM_ID, {'DS': ['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DS_COMPLETION_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DS_COMPLETION_METADATA}
