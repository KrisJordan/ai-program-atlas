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

# Writing, physics and philosophy metadata for reviewed existing courses.
_CONTEXT_METADATA = register_subject_sources(PROGRAM_ID, {'ENGW': ['ENGW 1111', 'ENGW 3302', 'ENGW 3304', 'ENGW 3315']})
SOURCES = tuple(SOURCES) + tuple(_CONTEXT_METADATA)
SOURCE_PARSERS = {**SOURCE_PARSERS, **_CONTEXT_METADATA}

# Observe remaining disciplinary course facts without inventing descriptions.
_DISCIPLINE_REMAINDER_METADATA = register_subject_sources(PROGRAM_ID, {'ECON': ['ECON 1115', 'ECON 1116', 'ECON 3413']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_DISCIPLINE_REMAINDER_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_DISCIPLINE_REMAINDER_METADATA}

# Official subject facts for reviewed engineering, health and social-science courses.
_ADDITIONAL_DISCIPLINES_METADATA = register_subject_sources(PROGRAM_ID, {'COMM': ['COMM 3201'], 'EECE': ['EECE 2160', 'EECE 2322', 'EECE 2323', 'EECE 2560'], 'INPR': ['INPR 1000'], 'PHTH': ['PHTH 2515', 'PHTH 4515'], 'SOCL': ['SOCL 3441']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_ADDITIONAL_DISCIPLINES_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_ADDITIONAL_DISCIPLINES_METADATA}

# Business and design course metadata.
_BUSINESS_DESIGN_METADATA = register_subject_sources(PROGRAM_ID, {'ACCT': ['ACCT 1201', 'ACCT 2301', 'ACCT 3401', 'ACCT 4501', 'ACCT 3403', 'ACCT 3416', 'ACCT 4412', 'ACCT 4414', 'ACCT 3402', 'ACCT 3220'], 'BUSN': ['BUSN 1102', 'BUSN 1103', 'BUSN 4945', 'BUSN 3110'], 'ENTR': ['ENTR 3330', 'ENTR 2303', 'ENTR 3217', 'ENTR 3304', 'ENTR 3305', 'ENTR 4983', 'ENTR 4501', 'ENTR 2215', 'ENTR 2225', 'ENTR 3401', 'ENTR 3945', 'ENTR 4414', 'ENTR 3220', 'ENTR 3306'], 'FINA': ['FINA 2201', 'FINA 4335', 'FINA 4610', 'FINA 3301', 'FINA 3303', 'FINA 2720', 'FINA 2730', 'FINA 3305', 'FINA 3401', 'FINA 4219', 'FINA 4220', 'FINA 4320', 'FINA 4340', 'FINA 4350', 'FINA 4370', 'FINA 4390', 'FINA 4410', 'FINA 4412', 'FINA 4420', 'FINA 4460', 'FINA 4512', 'FINA 4514', 'FINA 4516', 'FINA 4524', 'FINA 4526', 'FINA 4604', 'FINA 4983'], 'INNO': ['INNO 2301', 'INNO 3335', 'INNO 4504', 'INNO 2304', 'INNO 4225', 'INNO 2206', 'INNO 2414', 'INNO 3303', 'INNO 3309', 'INNO 4983', 'INNO 3520', 'INNO 4506'], 'INTB': ['INTB 1203', 'INTB 1209', 'INTB 2501', 'INTB 3310', 'INTB 3320', 'INTB 3330', 'INTB 4983', 'INTB 3205'], 'MGMT': ['MGMT 3530', 'MGMT 3340', 'MGMT 3302', 'MGMT 3315', 'MGMT 3420', 'MGMT 4410', 'MGMT 4550', 'MGMT 3380', 'MGMT 3305', 'MGMT 3350', 'MGMT 3435', 'MGMT 4310', 'MGMT 4983'], 'MGSC': ['MGSC 2301'], 'MISM': ['MISM 2301', 'MISM 2510', 'MISM 3501', 'MISM 3515'], 'MKTG': ['MKTG 4606', 'MKTG 2201', 'MKTG 4604', 'MKTG 3720', 'MKTG 2720', 'MKTG 2801', 'MKTG 3401', 'MKTG 3402', 'MKTG 4502', 'MKTG 4504', 'MKTG 4506', 'MKTG 4510', 'MKTG 4720', 'MKTG 4512', 'MKTG 2602', 'MKTG 2301', 'MKTG 3301', 'MKTG 3501', 'MKTG 3945', 'MKTG 4120', 'MKTG 4220', 'MKTG 4420', 'MKTG 4508', 'MKTG 4605', 'MKTG 4983', 'MKTG 2601'], 'ORGB': ['ORGB 3201', 'ORGB 3203'], 'SCHM': ['SCHM 2301', 'SCHM 3315', 'SCHM 3301', 'SCHM 3305', 'SCHM 3310', 'SCHM 3302', 'SCHM 3303', 'SCHM 3308', 'SCHM 3330', 'SCHM 4983'], 'STRT': ['STRT 4501', 'STRT 4301', 'STRT 3301']})
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(_BUSINESS_DESIGN_METADATA)))
SOURCE_PARSERS = {**SOURCE_PARSERS, **_BUSINESS_DESIGN_METADATA}

# Remaining humanities language and ancillary course metadata.
_REMAINING_SUBJECT_METADATA = register_subject_sources(PROGRAM_ID, {'ANTH': ['ANTH 3441'], 'COOP': ['COOP 3945', 'COOP 3946', 'COOP 3947', 'COOP 3948'], 'EEBA': ['EEBA 2945', 'EEBA 2948'], 'HUSV': ['HUSV 2970'], 'IE': ['IE 3500']})
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

# Exact communication review composes with, rather than discards, broader metadata.
from atlas.adapters.northeastern_communication_course_reviews import attach_reviewed_sources
SOURCE_PARSERS = attach_reviewed_sources(PROGRAM_ID, SOURCE_PARSERS)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(SOURCE_PARSERS)))

# Exact public-health review composes with, rather than discards, broader metadata.
from atlas.adapters.northeastern_public_health_course_reviews import attach_reviewed_sources
SOURCE_PARSERS = attach_reviewed_sources(PROGRAM_ID, SOURCE_PARSERS)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(SOURCE_PARSERS)))

# Exact Business Marketing/Innovation/Entrepreneurship evidence composes with broader subject observations.
from atlas.adapters.northeastern_business_marketing_reviews import attach_reviewed_sources
SOURCE_PARSERS = attach_reviewed_sources(PROGRAM_ID, SOURCE_PARSERS)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(SOURCE_PARSERS)))

# Exact remaining Business subjects evidence composes with broader subject observations.
from atlas.adapters.northeastern_business_remaining_reviews import attach_reviewed_sources
SOURCE_PARSERS = attach_reviewed_sources(PROGRAM_ID, SOURCE_PARSERS)
SOURCES = tuple(dict.fromkeys(tuple(SOURCES) + tuple(SOURCE_PARSERS)))
