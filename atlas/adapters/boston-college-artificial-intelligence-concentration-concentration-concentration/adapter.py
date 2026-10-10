"""Reviewed source-specific observations; no automatic completeness promotion."""
from atlas.adapters.concentrations_2026 import parse_bc, parse_bc_courses

PROGRAM_ID = 'boston-college-artificial-intelligence-concentration-concentration-concentration'
SOURCES = ('https://www.bc.edu/bc-web/schools/morrissey/departments/computer-science/academics/programs.html', 'https://bcweb.bc.edu/aem/coursesfall.json')

def parse(html: str) -> dict:
    return parse_bc(html, PROGRAM_ID, 'boston-college-artificial-intelligence-concentration-concentration-concentration-official', SOURCES[0])

def parse_policy(html: str) -> dict:
    return parse_bc_courses(html, PROGRAM_ID, 'bc-fall-2026-course-feed', SOURCES[1])

SOURCE_PARSERS = {SOURCES[1]: parse_policy}
