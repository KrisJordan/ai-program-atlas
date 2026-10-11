"""Reviewed source-specific identity observation; curriculum remains pending."""
from atlas.adapters.national_depth_discovery import parse_identity

PROGRAM_ID = 'rpi-cognitive-science-ai-minor'
SOURCES = ('https://hass.rpi.edu/cognitive-science/cognitive-science-artificial-intelligence',)

def parse(html):
    return parse_identity(html, 'rpi')
