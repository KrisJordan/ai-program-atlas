"""Reviewed source-specific observations; no automatic completeness promotion."""
from atlas.adapters.concentrations_2026 import parse_emory, parse_emory_faq

PROGRAM_ID = 'emory-university-cs-bs-ai-concentration-concentration-concentration'
SOURCES = ('https://computerscience.emory.edu/undergraduate/degrees-and-requirements/cs-bs-ai-concentration.html', 'https://computerscience.emory.edu/undergraduate/faqs.html')

def parse(html: str) -> dict:
    return parse_emory(html, PROGRAM_ID, 'emory-university-cs-bs-ai-concentration-concentration-concentration-official', SOURCES[0])

def parse_policy(html: str) -> dict:
    return parse_emory_faq(html, PROGRAM_ID, 'emory-cs-concentration-faq', SOURCES[1])

SOURCE_PARSERS = {SOURCES[1]: parse_policy}
