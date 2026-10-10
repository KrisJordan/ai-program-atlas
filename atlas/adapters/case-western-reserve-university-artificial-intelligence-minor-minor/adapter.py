"""Actual course/policy observations; completeness requires separate review."""
from atlas.adapters.reviewed_minors_2026 import parse_case, policy_observation

PROGRAM_ID = 'case-western-reserve-university-artificial-intelligence-minor-minor'
SOURCE_ID = 'case-minor-catalog'
SOURCES = ('https://bulletin.case.edu/engineering/computer-data-sciences/artificial-intelligence-minor/', 'https://bulletin.case.edu/undergraduate-academics/academic-policies-procedures/', 'https://bulletin.case.edu/undergraduate-academics/grades/')

def parse(html: str) -> dict:
    return parse_case(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

def parse_policy_0(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'case-policy-minor-policy', 'case-policy')

def parse_policy_1(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'case-grades-minor-policy', 'case-grades')

SOURCE_PARSERS = {'https://bulletin.case.edu/undergraduate-academics/academic-policies-procedures/': parse_policy_0, 'https://bulletin.case.edu/undergraduate-academics/grades/': parse_policy_1}

from atlas.adapters.case_minor_courses import register
SOURCES = list(SOURCES)
register(PROGRAM_ID, SOURCES, SOURCE_PARSERS)
