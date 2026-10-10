"""Actual local-minor observations; refresh never certifies completeness."""
from atlas.adapters.vt_duke_minors import parse_vt, policy_observation

PROGRAM_ID = 'virginia-tech-artificial-intelligence-ai-minor-minor'
SOURCE_ID = 'vt-ai-department'
SOURCES = ('https://website.cs.vt.edu/academic/undergraduate/ai-minor.html', 'https://eng.vt.edu/undergraduate/minors.html')

def parse(html: str) -> dict:
    return parse_vt(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

def parse_policy_0(html: str) -> dict:
    return policy_observation(html, PROGRAM_ID, 'vt-engineering-minors', 'vt')

SOURCE_PARSERS = {'https://eng.vt.edu/undergraduate/minors.html': parse_policy_0}
