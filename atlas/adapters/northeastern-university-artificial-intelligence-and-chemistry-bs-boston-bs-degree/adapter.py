"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-chemistry-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-chemistry-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Chemistry, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Requirements', 'Chemistry Requirements', 'Integrative Requirements', 'Writing Requirements', 'Required General Electives', 'Science GPA Requirement (Chemistry)', 'NUpath Requirements Satisfied', 'Program Requirement'],
        outcome_claims=[('qualitative and quantitative problem-solving skills', 'Students develop quantitative and qualitative problem-solving and communication skills.'), ('computational analysis of chemical and other scientific data', 'Students apply computational methods to chemical and other scientific data.')],
        pooled_subheaders=[],
        overview_rules=[])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400'], url='https://catalog.northeastern.edu/course-descriptions/ds/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-chemistry-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1365', 'MATH 1465', 'MATH 1341', 'MATH 1342'], 'CS': ['CS 1200', 'CS 1210', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'CHEM': ['CHEM 1161', 'CHEM 1162', 'CHEM 1163', 'CHEM 2311', 'CHEM 2312']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3307', 'ENGW 3315'], 'PHYS': ['PHYS 1151', 'PHYS 1152', 'PHYS 1153']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'CHEM': ['CHEM 1161', 'CHEM 1162', 'CHEM 1163', 'CHEM 2161', 'CHEM 2162', 'CHEM 2311', 'CHEM 2312', 'CHEM 2315', 'CHEM 2316', 'CHEM 2313', 'CHEM 2314', 'CHEM 2317', 'CHEM 2318', 'CHEM 2321', 'CHEM 2322', 'CHEM 3410', 'CHEM 3401', 'CHEM 3402', 'CHEM 4750']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EECE': ['EECE 2160', 'EECE 2322'], 'ENVR': ['ENVR 2500', 'ENVR 2501'], 'INPR': ['INPR 1000'], 'INSC': ['INSC 1000']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}
