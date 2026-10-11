"""Visible official concentration requirements; no automatic completeness claim."""
from atlas.adapters.american_sandiego_concentrations import parse_sandiego

PROGRAM_ID = 'san-diego-cs-bs-data-science-ai-concentration'
SOURCE_ID = 'san-diego-cs-bs-data-science-ai-concentration-catalog'
SOURCES = ('https://undergraduate.catalog.sandiego.edu/programs/major-BS_ENGR-UG-M-EN-BS-COMS/program-requirements-ZEsvA',)

def parse(html: str) -> dict:
    return parse_sandiego(html, PROGRAM_ID, SOURCE_ID, SOURCES[0], 'BS')

from functools import partial
from atlas.adapters.american_sandiego_policies import parse_usd_policy

POLICY_PATHS = {
    'credit': 'academics/academicregulations#credit-hour-policy1',
    'grading': 'academics/academicregulations#credit-and-grading-system1',
    'declaration': 'academics/academicregulations#declaring-the-major',
    'residence': 'academics/academicregulations#residence-requirement1',
    'major-grades': 'academics/academicprograms#general-requirements-for-bachelor-s-degree1',
    'overlap': 'academics/academicprograms#requirements-for-major-and-minor',
    'school': 'academics/collegeandschools/shileymarcos#requirements',
}
SOURCE_PARSERS = {
    'https://undergraduate.catalog.sandiego.edu/'+path: partial(
        parse_usd_policy, pid=PROGRAM_ID, source='sandiego-policy-'+kind, kind=kind)
    for kind, path in POLICY_PATHS.items()
}
SOURCES += tuple(SOURCE_PARSERS)
