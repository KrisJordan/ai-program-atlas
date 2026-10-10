"""Actual course/policy observations; completeness requires separate review."""
from atlas.adapters.reviewed_minors_2026 import parse_neu_ai, policy_observation

PROGRAM_ID = 'northeastern-university-artificial-intelligence-minor-minor-minor'
SOURCE_ID = 'neu-ai-minor-catalog'
SOURCES = ('https://catalog.northeastern.edu/undergraduate/computer-information-science/data-science/artificial-intelligence-minor/', 'https://catalog.northeastern.edu/undergraduate/academic-policies-procedures/degrees-majors-minors/')

def parse(html: str) -> dict:
    return parse_neu_ai(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

def parse_policy_0(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'neu-minor-policy', 'neu')

SOURCE_PARSERS = {'https://catalog.northeastern.edu/undergraduate/academic-policies-procedures/degrees-majors-minors/': parse_policy_0}
