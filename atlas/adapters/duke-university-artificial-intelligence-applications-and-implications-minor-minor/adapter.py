"""Actual local-minor observations; refresh never certifies completeness."""
from atlas.adapters.vt_duke_minors import parse_duke_apps, policy_observation

PROGRAM_ID = 'duke-university-artificial-intelligence-applications-and-implications-minor-minor'
SOURCE_ID = 'duke-apps-department'
SOURCES = ('https://cs.duke.edu/undergraduate/degrees/minors', 'https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml', 'https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate')

def parse(html: str) -> dict:
    return parse_duke_apps(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

def parse_policy_0(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'duke-apps-linked-concentration', 'concentration')

def parse_policy_1(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'duke-trinity-minor-policy', 'trinity')

SOURCE_PARSERS = {'https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml': parse_policy_0, 'https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate': parse_policy_1}
