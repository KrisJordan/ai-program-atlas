"""Actual local-minor observations; refresh never certifies completeness."""
from atlas.adapters.vt_duke_minors import parse_duke_ml, policy_observation

PROGRAM_ID = 'duke-university-machine-learning-artificial-intelligence-minor-minor'
SOURCE_ID = 'duke-ml-department'
SOURCES = ('https://ece.duke.edu/academics/undergrad/minors/', 'https://undergraduate.bulletins.duke.edu/programs/U-ECE-MLAI/requirements-IkDU1', 'https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate')

def parse(html: str) -> dict:
    return parse_duke_ml(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

def parse_policy_0(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'duke-ml-bulletin', 'bulletin')

def parse_policy_1(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'duke-trinity-minor-policy', 'trinity')

SOURCE_PARSERS = {'https://undergraduate.bulletins.duke.edu/programs/U-ECE-MLAI/requirements-IkDU1': parse_policy_0, 'https://trinity.duke.edu/undergraduate/academic-policies/change-major-minor-certificate': parse_policy_1}
