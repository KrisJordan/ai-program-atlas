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

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1365', 'MATH 1465', 'MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'BIOL': ['BIOL 1107', 'BIOL 1108', 'BIOL 2301', 'BIOL 2302', 'BIOL 2407', 'BIOL 4701'], 'CHEM': ['CHEM 1161', 'CHEM 1162', 'CHEM 2311', 'CHEM 2312']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Complete the reviewed DS selections, preserving one fetch per source URL.
_DS_COMPLETION_METADATA = register_subject_sources(PROGRAM_ID, {'DS': ['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DS_COMPLETION_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DS_COMPLETION_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3315', 'ENGW 3307'], 'PHYS': ['PHYS 1145', 'PHYS 1146', 'PHYS 1151', 'PHYS 1161']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'BIOL': ['BIOL 1000', 'BIOL 1107', 'BIOL 1108', 'BIOL 2299', 'BIOL 2301', 'BIOL 2302', 'BIOL 2309', 'BIOL 2407', 'BIOL 3611', 'BIOL 3612', 'BIOL 4991', 'BIOL 4970', 'BIOL 4971', 'BIOL 4994', 'BIOL 2327', 'BIOL 3401', 'BIOL 3413', 'BIOL 3427', 'BIOL 3451', 'BIOL 5585', 'BIOL 4707', 'BIOL 5581', 'BIOL 5591', 'BIOL 4701', 'BIOL 4900'], 'CHEM': ['CHEM 1161', 'CHEM 1162', 'CHEM 2311', 'CHEM 2312', 'CHEM 2313', 'CHEM 2314']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EECE': ['EECE 2160', 'EECE 2322'], 'EEMB': ['EEMB 2302', 'EEMB 2303', 'EEMB 2400', 'EEMB 2700', 'EEMB 2701', 'EEMB 3460', 'EEMB 3466', 'EEMB 3600'], 'ENVR': ['ENVR 2500', 'ENVR 2501'], 'INPR': ['INPR 1000'], 'INSC': ['INSC 1000']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}
