"""Source-specific local curriculum candidates; manual audit remains partial."""
from atlas.adapters import national_depth_curricula as curricula

PROGRAM_ID = 'rpi-cognitive-science-ai-minor'
SOURCES = ('https://hass.rpi.edu/cognitive-science/cognitive-science-artificial-intelligence',)

def parse(html):
    return curricula.parse_rpi(html)
