"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-public-health-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-public-health-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Public Health, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Requirements', 'Supporting Courses', 'Public Health Requirements', 'Writing Requirement', 'Integrative Requirement', 'General Electives', 'Public Health Major Requirement', 'NUpath Requirements Satisfied', 'Program Requirement'],
        outcome_claims=[('social determinants of health, biostatistics and epidemiology', 'The program develops foundations in public health determinants, statistics and epidemiology.'), ('health communication, and health education and program planning', 'Students study health communication, education and program planning alongside AI.')],
        pooled_subheaders=[],
        overview_rules=[])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420'], url='https://catalog.northeastern.edu/course-descriptions/ds/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-public-health-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341', 'MATH 1241', 'MATH 3081'], 'CS': ['CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 1200', 'CS 1210']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 2350', 'ECON 1115', 'ECON 1116'], 'PSYC': ['PSYC 2320', 'PSYC 1101', 'PSYC 3450']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3306', 'ENGW 3315']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'BIOL': ['BIOL 2329', 'BIOL 1141', 'BIOL 1143', 'BIOL 1147', 'BIOL 1111', 'BIOL 1112', 'BIOL 1113', 'BIOL 1114'], 'ECON': ['ECON 2350', 'ECON 1115', 'ECON 1116', 'ECON 3404', 'ECON 3423', 'ECON 3424', 'ECON 3413'], 'PSYC': ['PSYC 2320', 'PSYC 1101', 'PSYC 3402', 'PSYC 3404', 'PSYC 3450'], 'PHIL': ['PHIL 1165', 'PHIL 1101', 'PHIL 5001', 'PHIL 5002']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'COMM': ['COMM 1225', 'COMM 3201', 'COMM 4102', 'COMM 3500'], 'CRIM': ['CRIM 3040'], 'ENVR': ['ENVR 2500', 'ENVR 2501', 'ENVR 2502'], 'INPR': ['INPR 1000'], 'INTL': ['INTL 1101', 'INTL 3200', 'INTL 3201', 'INTL 3400', 'INTL 5100'], 'PHTH': ['PHTH 2210', 'PHTH 1260', 'PHTH 1261', 'PHTH 2300', 'PHTH 2301', 'PHTH 2350', 'PHTH 2351', 'PHTH 2515', 'PHTH 4120', 'PHTH 4202', 'PHTH 4540', 'PHTH 5222', 'PHTH 3717', 'PHTH 5230', 'PHTH 5214', 'PHTH 4511', 'PHTH 5232', 'PHTH 5234'], 'SOCL': ['SOCL 1101', 'SOCL 3241', 'SOCL 3441', 'SOCL 4520']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'MGMT': ['MGMT 3340'], 'ORGB': ['ORGB 3201']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'AFCS': ['AFCS 3424'], 'ANTH': ['ANTH 1101', 'ANTH 3441'], 'ENGL': ['ENGL 1300'], 'HLTH': ['HLTH 5280'], 'HSCI': ['HSCI 1000', 'HSCI 2000'], 'HUSV': ['HUSV 1101'], 'POLS': ['POLS 1160', 'POLS 3487', 'POLS 3307'], 'PPUA': ['PPUA 5100', 'PPUA 5238']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_REMAINING_SUBJECT_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_REMAINING_SUBJECT_METADATA}

# Independently public offering-specific CS 2000/2001 resources.
from atlas.adapters.northeastern_course_resources import register_resources
_PUBLIC_CS_RESOURCES = register_resources(PROGRAM_ID)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_PUBLIC_CS_RESOURCES)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_PUBLIC_CS_RESOURCES}

# Explicit degree-plus-subject concurrency, not inferred prerequisites.
from atlas.adapters.northeastern_corequisites import register_cs1802
parse, SOURCE_PARSERS = register_cs1802(parse, SOURCE_PARSERS, PROGRAM_ID)

# Conditional Khoury rules do not infer the student's home college.
from atlas.adapters.northeastern_college_policies import KHOURY_URL, parse_khoury_policy
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + (KHOURY_URL,)))
SOURCE_PARSERS = {**SOURCE_PARSERS, KHOURY_URL: lambda html: parse_khoury_policy(html, program_id=PROGRAM_ID)}

# Verified Bouvé participation; rules remain conditional on actual applicability.
from atlas.adapters.northeastern_college_policies import BOUVE_URL, parse_bouve_policy
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + (BOUVE_URL,)))
SOURCE_PARSERS = {**SOURCE_PARSERS, BOUVE_URL: lambda html: parse_bouve_policy(html, program_id=PROGRAM_ID)}

# Exact communication review composes with, rather than discards, broader metadata.
from atlas.adapters.northeastern_communication_course_reviews import attach_reviewed_sources
SOURCE_PARSERS = attach_reviewed_sources(PROGRAM_ID, SOURCE_PARSERS)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(SOURCE_PARSERS)))
