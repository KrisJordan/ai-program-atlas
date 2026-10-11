"""Reviewed source-specific identity observation; curriculum remains pending."""
from atlas.adapters.national_depth_discovery import parse_identity

PROGRAM_ID = 'fsu-cs-ai-concentration'
SOURCES = ('https://www.cs.fsu.edu/academics/undergraduate-programs/artificial-intelligence-concentration/',)

def parse(html):
    return parse_identity(html, 'fsu')
