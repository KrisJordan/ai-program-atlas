"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-behavioral-neuroscience-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-behavioral-neuroscience-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Behavioral Neuroscience, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Requirements', 'Writing Requirements', 'Behavioral Neuroscience Requirements', 'Integrative Requirements', 'Required General Electives', 'Science GPA Requirement (Behavioral Neuroscience)', 'NUpath Requirements Satisfied', 'Program Requirement'],
        outcome_claims=[('anatomy and physiology of neural circuits', 'Students investigate neural circuits and their relationships with behavior.'), ('large-scale data manipulation and storage, machine learning', 'The program develops computational skills for analyzing large brain datasets.')],
        pooled_subheaders=[],
        overview_rules=[])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400'], url='https://catalog.northeastern.edu/course-descriptions/ds/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-behavioral-neuroscience-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1365', 'MATH 1465', 'MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 4100']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'BIOL': ['BIOL 1107', 'BIOL 1108', 'BIOL 2301', 'BIOL 2302'], 'CHEM': ['CHEM 1161', 'CHEM 1162', 'CHEM 1163', 'CHEM 2311', 'CHEM 2312'], 'PSYC': ['PSYC 2320', 'PSYC 1101', 'PSYC 3450', 'PSYC 3466', 'PSYC 4540']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3307', 'ENGW 3315']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'BIOL': ['BIOL 1107', 'BIOL 1108', 'BIOL 2299', 'BIOL 2301', 'BIOL 2302', 'BIOL 3405', 'BIOL 5595', 'BIOL 3415', 'BIOL 3425', 'BIOL 3601', 'BIOL 3605', 'BIOL 4705', 'BIOL 4709', 'BIOL 5601'], 'PSYC': ['PSYC 2320', 'PSYC 1101', 'PSYC 3200', 'PSYC 3404', 'PSYC 3406', 'PSYC 3450', 'PSYC 3451', 'PSYC 3452', 'PSYC 3464', 'PSYC 3466', 'PSYC 3506', 'PSYC 3508', 'PSYC 3510', 'PSYC 4510', 'PSYC 4512', 'PSYC 4514', 'PSYC 4570', 'PSYC 4540']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}
