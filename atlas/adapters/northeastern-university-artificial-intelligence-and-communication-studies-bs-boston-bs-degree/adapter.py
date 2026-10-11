"""Observe the exact combined-degree catalog, preserving award and local rules."""
from atlas.adapters.northeastern_courseleaf import parse_catalog
PROGRAM_ID = 'northeastern-university-artificial-intelligence-and-communication-studies-bs-boston-bs-degree'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-communication-studies-bs-bos/',)

def parse(html: str) -> dict:
    return parse_catalog(html, program_id=PROGRAM_ID, title='Artificial Intelligence and Communication Studies, BS (Boston)', url=SOURCES[0],
        required_sections=['Universitywide Requirements', 'NUpath Requirements', 'Artificial Intelligence Courses', 'Communication Studies Requirements', 'Integrative Requirement Courses', 'Capstone Experience Course', 'Supporting Courses', 'Required General Electives', 'NUpath Requirements Satisfied', 'Communication Studies Grade Requirement', 'Program Requirement'], outcome_claims=[('major conceptual frameworks for human communication', 'Students develop conceptual knowledge of communication and apply it to social problems.')], **{})


def parse_ds_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='DS', heading='Data Science (DS)', codes=['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420', 'DS 4440', 'DS 1300'], url='https://catalog.northeastern.edu/course-descriptions/ds/')


def parse_comm_metadata(html: str) -> dict:
    from atlas.adapters.northeastern_course_metadata import parse_subject
    return parse_subject(html, program_id=PROGRAM_ID, subject='COMM', heading='Communication Studies (COMM)', codes=['COMM 1101', 'COMM 1112', 'COMM 2301', 'COMM 1210', 'COMM 1225', 'COMM 1231', 'COMM 1255', 'COMM 1131', 'COMM 2303', 'COMM 2304', 'COMM 2501', 'COMM 2551', 'COMM 3200', 'COMM 3201', 'COMM 3230', 'COMM 3304', 'COMM 3320', 'COMM 3415', 'COMM 3500', 'COMM 3501', 'COMM 3530', 'COMM 3532', 'COMM 4535', 'COMM 4605', 'COMM 4631', 'COMM 2625', 'COMM 2941', 'COMM 4608', 'COMM 4625', 'COMM 4901', 'COMM 1000', 'COMM 3409'], url='https://catalog.northeastern.edu/course-descriptions/comm/')

SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/computer-information-science-combined-majors/artificial-intelligence-communication-studies-bs-bos/', 'https://catalog.northeastern.edu/course-descriptions/ds/', 'https://catalog.northeastern.edu/course-descriptions/comm/')
SOURCE_PARSERS = {'https://catalog.northeastern.edu/course-descriptions/ds/': parse_ds_metadata, 'https://catalog.northeastern.edu/course-descriptions/comm/': parse_comm_metadata}

# Shared policy facts are observed independently for each concrete program.
from atlas.adapters.northeastern_policies import register_policy_sources
_POLICY_PARSERS = register_policy_sources(PROGRAM_ID)
SOURCES = tuple(SOURCES) + tuple(_POLICY_PARSERS)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_POLICY_PARSERS}

# Independently reviewed CS/MATH/CY subject-catalog observations.
from atlas.adapters.northeastern_course_metadata import register_subject_sources
_FOUNDATION_METADATA = register_subject_sources(PROGRAM_ID, {'MATH': ['MATH 1341'], 'CS': ['CS 1800', 'CS 2000', 'CS 2001', 'CS 2100', 'CS 2101', 'CS 3200', 'CS 4120', 'CS 1200', 'CS 1210'], 'CY': ['CY 4170', 'CY 5240']})
SOURCES = tuple(SOURCES) + tuple(_FOUNDATION_METADATA)
SOURCE_PARSERS = {**globals().get('SOURCE_PARSERS', {}), **_FOUNDATION_METADATA}

# Independently reviewed disciplinary subject-catalog observations.
_DISCIPLINE_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 2350']})
SOURCES = tuple(SOURCES) + tuple(_DISCIPLINE_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_METADATA}

# Complete the reviewed DS selections, preserving one fetch per source URL.
_DS_COMPLETION_METADATA = register_subject_sources(PROGRAM_ID, {'DS': ['DS 3500', 'DS 3000', 'DS 4200', 'DS 4300', 'DS 4400', 'DS 4420', 'DS 4440', 'DS 1300']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DS_COMPLETION_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DS_COMPLETION_METADATA}

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 1102', 'ENGW 1114', 'ENGW 3302', 'ENGW 3314', 'ENGW 3315'], 'PHIL': ['PHIL 1300', 'PHIL 1145']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'COMM': ['COMM 1101', 'COMM 1112', 'COMM 2301', 'COMM 1210', 'COMM 1225', 'COMM 1231', 'COMM 1255', 'COMM 1131', 'COMM 2303', 'COMM 2304', 'COMM 2501', 'COMM 2551', 'COMM 3200', 'COMM 3201', 'COMM 3230', 'COMM 3304', 'COMM 3320', 'COMM 3415', 'COMM 3500', 'COMM 3501', 'COMM 3530', 'COMM 3532', 'COMM 4535', 'COMM 4605', 'COMM 4631', 'COMM 2625', 'COMM 2941', 'COMM 4608', 'COMM 4625', 'COMM 4901', 'COMM 1000', 'COMM 3409'], 'EECE': ['EECE 2160', 'EECE 2322', 'EECE 2323'], 'INPR': ['INPR 1000'], 'JRNL': ['JRNL 2301'], 'SOCL': ['SOCL 1280', 'SOCL 2485', 'SOCL 4528']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'MKTG': ['MKTG 4606']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'AFCS': ['AFCS 2600'], 'EEAM': ['EEAM 2000'], 'HIST': ['HIST 2220'], 'INSH': ['INSH 2102'], 'MSCR': ['MSCR 1320'], 'PREL': ['PREL 1425', 'PREL 3625']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_REMAINING_SUBJECT_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_REMAINING_SUBJECT_METADATA}

# Independently public offering-specific CS 2000/2001 resources.
from atlas.adapters.northeastern_course_resources import register_resources
_PUBLIC_CS_RESOURCES = register_resources(PROGRAM_ID)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_PUBLIC_CS_RESOURCES)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_PUBLIC_CS_RESOURCES}
