"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-sociology-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-sociology-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Sociology, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Courses', 'Sociology Requirements', 'Supporting Courses', 'Writing Courses', 'Integrative Course', 'Required General Electives', 'NUpath Requirements Satisfied', 'Program Requirement'], outcome_claims=[('conceptual tools to understand how various features of society', 'Students use sociological concepts to analyze society and inequality alongside computational data skills.')], **{})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_socl_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='SOCL', heading='Sociology (SOCL)', codes=['SOCL 1101', 'SOCL 3300', 'SOCL 2321', 'SOCL 4600', 'SOCL 1000', 'SOCL 2320', 'SOCL 2485', 'SOCL 4528'], url='https://catalog.northeastern.edu/course-descriptions/socl/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-sociology-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/socl/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/socl/': parse_socl_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341'], 'CS': ['CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 1200', 'CS 1210']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 1114', 'ENGW 3302', 'ENGW 3308', 'ENGW 3315']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'EECE': ['EECE 2160', 'EECE 2322', 'EECE 2323'], 'INPR': ['INPR 1000'], 'SOCL': ['SOCL 1101', 'SOCL 3300', 'SOCL 2321', 'SOCL 4600', 'SOCL 1000', 'SOCL 2320', 'SOCL 2485', 'SOCL 4528']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'EESH': ['EESH 2000'], 'INSH': ['INSH 3101', 'INSH 3102']})
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

# Officially documented CSSH participation; transfer rules stay conditional.
from atlas.adapters.northeastern_college_policies import CSSH_TRANSFER_URL, parse_cssh_transfer
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + (CSSH_TRANSFER_URL,)))
SOURCE_PARSERS = {**SOURCE_PARSERS, CSSH_TRANSFER_URL: lambda html: parse_cssh_transfer(html, program_id=PROGRAM_ID)}

# Verified Khoury/CSSH participation; only conditional additional policies.
from atlas.adapters.northeastern_policy_closure import CSSH_CATALOG, CSSH_CHANGE, CSSH_PROGRESS, observe_cssh
from functools import partial
_CSSH_SUPPLEMENTS={url:partial(observe_cssh,program_id=PROGRAM_ID,source=url) for url in [CSSH_CATALOG,CSSH_CHANGE,CSSH_PROGRESS]}
SOURCES=tuple(dict.fromkeys(tuple(SOURCES)+tuple(_CSSH_SUPPLEMENTS)))
SOURCE_PARSERS={**SOURCE_PARSERS,**_CSSH_SUPPLEMENTS}
