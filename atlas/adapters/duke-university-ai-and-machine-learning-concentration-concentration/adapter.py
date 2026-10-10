"""Reviewed source-specific observations; no automatic completeness promotion."""
from atlas.adapters.concentrations_2026 import parse_duke_concentration, parse_duke_substitutions

PROGRAM_ID = 'duke-university-ai-and-machine-learning-concentration-concentration'
SOURCES = ('https://cs.duke.edu/undergraduate/degrees/BS/concentrations/ai-ml', 'https://cs.duke.edu/undergraduate/courses/substitutions')

def parse(html: str) -> dict:
    return parse_duke_concentration(html, PROGRAM_ID, 'duke-university-ai-and-machine-learning-concentration-concentration-official', SOURCES[0])

def parse_policy(html: str) -> dict:
    return parse_duke_substitutions(html, PROGRAM_ID, 'duke-ai-concentration-substitutions', SOURCES[1])

SOURCE_PARSERS = {SOURCES[1]: parse_policy}
