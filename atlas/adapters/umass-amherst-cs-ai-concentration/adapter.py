"""Reviewed source-specific identity observation; curriculum remains pending."""
from atlas.adapters.national_depth_discovery import parse_identity

PROGRAM_ID = 'umass-amherst-cs-ai-concentration'
SOURCES = ('https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/bs-ai-concentration-requirements',)

def parse(html):
    return parse_identity(html, 'umass')
