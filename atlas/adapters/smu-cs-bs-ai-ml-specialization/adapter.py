"""Reviewed source-specific identity observation; curriculum remains pending."""
from atlas.adapters.national_depth_discovery import parse_identity

PROGRAM_ID = 'smu-cs-bs-ai-ml-specialization'
SOURCES = ('https://www.smu.edu/lyle/undergraduate/bs-computer-science',)

def parse(html):
    return parse_identity(html, 'smu-bs')
