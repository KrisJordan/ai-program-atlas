"""Observe published course choices; no automatic completeness certification."""
from atlas.adapters.business_society_minors import observe
PROGRAM_ID = 'rit-ai-society-minor'
SOURCES = ('https://academiccatalog.rit.edu/programs/ai-society-minor/',)
SOURCE_ID = 'rit-ai-society-minor-curriculum'
def parse(html: str) -> dict:
    return observe(html, PROGRAM_ID, 'AI in Society', SOURCE_ID, SOURCES[0], 'rit')
