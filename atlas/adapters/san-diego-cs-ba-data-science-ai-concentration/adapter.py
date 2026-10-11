"""Visible official concentration requirements; no automatic completeness claim."""
from atlas.adapters.american_sandiego_concentrations import parse_sandiego

PROGRAM_ID = 'san-diego-cs-ba-data-science-ai-concentration'
SOURCE_ID = 'san-diego-cs-ba-data-science-ai-concentration-catalog'
SOURCES = ('https://undergraduate.catalog.sandiego.edu/programs/major-BAEN-UG-M-EN-BA-COMP/program-requirements-ZEsvA',)

def parse(html: str) -> dict:
    return parse_sandiego(html, PROGRAM_ID, SOURCE_ID, SOURCES[0], 'BA')

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
