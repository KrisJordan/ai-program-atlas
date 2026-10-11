"""Reviewed source-specific identity observation; curriculum remains pending."""
from atlas.adapters.national_depth_discovery import parse_identity

PROGRAM_ID = 'uic-cs-ai-concentration'
SOURCES = ('https://engineering.uic.edu/news-stories/uic-engineering-launches-ai-curriculum-initiatives/',)

def parse(html):
    return parse_identity(html, 'uic')
