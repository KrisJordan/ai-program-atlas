"""Observe the named Northeastern combined-BS catalog curriculum."""
from atlas.adapters.northeastern_courseleaf import parse_catalog

PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-environmental-and-sustainability-sciences-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-environmental-sustainability-sciences-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Environmental and Sustainability Sciences, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Courses', 'Environmental Science and Sustainability Courses', 'Supporting Courses', 'English Requirement', 'Integrative Requirement', 'Required General Electives', 'Science GPA Requirement (Environmental and Sustainability Sciences)', 'NUpath Requirements Satisfied', 'Program Requirement'],
        outcome_claims=[('major environmental challenges facing our planet', 'Students study environmental challenges and how AI-supported analysis can help address them.')],
        pooled_subheaders=['Environmental and Sustainability Sciences Electives'],
        overview_rules=[])


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420'], url='https://catalog.northeastern.edu/course-descriptions/ds/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-environmental-sustainability-sciences-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1365', 'MATH 1465', 'MATH 1341'], 'CS': ['CS 1200', 'CS 1210', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 4991']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'CHEM': ['CHEM 1161', 'CHEM 1162', 'CHEM 1163']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 3302', 'ENGW 3303', 'ENGW 3307', 'ENGW 3315']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EECE': ['EECE 2160', 'EECE 2322', 'EECE 2323'], 'EEMB': ['EEMB 2302', 'EEMB 2303', 'EEMB 2400', 'EEMB 3460', 'EEMB 3465', 'EEMB 4001'], 'ENVR': ['ENVR 1400', 'ENVR 1401', 'ENVR 1200', 'ENVR 1201', 'ENVR 2200', 'ENVR 2515', 'ENVR 3300', 'ENVR 3301', 'ENVR 5260', 'ENVR 4970', 'ENVR 2310', 'ENVR 2311', 'ENVR 2340', 'ENVR 2341', 'ENVR 3125', 'ENVR 3600', 'ENVR 4500', 'ENVR 4501', 'ENVR 5150', 'ENVR 5190', 'ENVR 5600', 'ENVR 5670', 'ENVR 4505', 'ENVR 5700', 'ENVR 5750', 'ENVR 3150', 'ENVR 3200', 'ENVR 5000', 'ENVR 5210', 'ENVR 5350', 'ENVR 5563', 'ENVR 5800', 'ENVR 5220', 'ENVR 5450', 'ENVR 2500', 'ENVR 2501', 'ENVR 4050', 'ENVR 4971', 'ENVR 4997'], 'INPR': ['INPR 1000'], 'INSC': ['INSC 1000'], 'SOCL': ['SOCL 2485']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'EESC': ['EESC 2000'], 'POLS': ['POLS 2395'], 'PPUA': ['PPUA 5260', 'PPUA 5268']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_REMAINING_SUBJECT_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_REMAINING_SUBJECT_METADATA}

# Independently public offering-specific CS 2000/2001 resources.
from atlas.adapters.northeastern_course_resources import register_resources
_PUBLIC_CS_RESOURCES = register_resources(PROGRAM_ID)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_PUBLIC_CS_RESOURCES)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_PUBLIC_CS_RESOURCES}

# Conditional Khoury rules do not infer the student's home college.
from atlas.adapters.northeastern_college_policies import KHOURY_URL, parse_khoury_policy
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + (KHOURY_URL,)))
SOURCE_PARSERS = {**SOURCE_PARSERS, KHOURY_URL: lambda html: parse_khoury_policy(html, program_id=PROGRAM_ID)}

# Verified COS participation; rules remain conditional on actual applicability.
from atlas.adapters.northeastern_college_policies import SCIENCE_URL, parse_science_policy
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + (SCIENCE_URL,)))
SOURCE_PARSERS = {**SOURCE_PARSERS, SCIENCE_URL: lambda html: parse_science_policy(html, program_id=PROGRAM_ID)}
