"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-international-affairs-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-international-affairs-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and International Affairs, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Courses', 'International Affairs Requirements', 'Global Dynamics Requirement', 'Regional Analysis Requirement', 'International Affairs Elective', 'English Requirement', 'Supporting Courses', 'Integrative Requirements', 'Required General Electives', 'Program Requirement'], outcome_claims=[('work across national cultures', 'The degree aims to prepare graduates to apply AI to regional and international issues across national cultures.')], **{'continued_choice_sections': {'Global Dynamics Requirement': ('pooled', 'have no bearing on major requirements'), 'Regional Analysis Requirement': ('one_group', 'both of which must be in one region'), 'International Affairs Elective': ('pooled', 'Complete one of the following:')}, 'instruction_notes': {'Complete at least one international semester via study abroad, international internship, international co-op, or two short-term programs.': 'Complete one international semester through study abroad, internship or co-op, or complete two short-term programs.', 'Complete the following with a thesis or project that integrates both international affairs and artificial intelligence:': 'The capstone thesis or project must integrate international affairs and AI.'}})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_intl_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='INTL', heading='International Affairs (INTL)', codes=['INTL 1000', 'INTL 1101', 'INTL 2718', 'INTL 3400', 'INTL 5100', 'INTL 5268', 'INTL 2480', 'INTL 2600', 'INTL 3520', 'INTL 5010', 'INTL 3430', 'INTL 3450', 'INTL 3300', 'INTL 3200', 'INTL 2500', 'INTL 4100', 'INTL 3150', 'INTL 3255', 'INTL 3455', 'INTL 4500', 'INTL 1160', 'INTL 2100', 'INTL 2200', 'INTL 3470', 'INTL 3350', 'INTL 3406', 'INTL 4700'], url='https://catalog.northeastern.edu/course-descriptions/intl/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-international-affairs-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/intl/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/intl/': parse_intl_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200'], 'CY': ['CY 4170']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 2350']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3308', 'ENGW 3315']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 3290', 'ECON 3635', 'ECON 3291', 'ECON 3404', 'ECON 3405', 'ECON 5650', 'ECON 1292', 'ECON 2350'], 'PHIL': ['PHIL 5001', 'PHIL 1111', 'PHIL 1271', 'PHIL 1275', 'PHIL 1290', 'PHIL 2395', 'PHIL 1280', 'PHIL 1285']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'COMM': ['COMM 2303'], 'CRIM': ['CRIM 3030', 'CRIM 3060', 'CRIM 5203', 'CRIM 1400'], 'EECE': ['EECE 2160', 'EECE 2322', 'EECE 2323'], 'ENVR': ['ENVR 1110', 'ENVR 2515', 'ENVR 3150'], 'INPR': ['INPR 1000'], 'INTL': ['INTL 1000', 'INTL 1101', 'INTL 2718', 'INTL 3400', 'INTL 5100', 'INTL 5268', 'INTL 2480', 'INTL 2600', 'INTL 3520', 'INTL 5010', 'INTL 3430', 'INTL 3450', 'INTL 3300', 'INTL 3200', 'INTL 2500', 'INTL 4100', 'INTL 3150', 'INTL 3255', 'INTL 3455', 'INTL 4500', 'INTL 1160', 'INTL 2100', 'INTL 2200', 'INTL 3470', 'INTL 3350', 'INTL 3406', 'INTL 4700'], 'JRNL': ['JRNL 3300', 'JRNL 5360'], 'PHTH': ['PHTH 1270', 'PHTH 5230'], 'SOCL': ['SOCL 1246']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'INNO': ['INNO 2206', 'INNO 3308'], 'INTB': ['INTB 3310', 'INTB 1203', 'INTB 1209'], 'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}
