"""Observe published course choices; no automatic completeness certification."""
from atlas.adapters.business_society_minors import observe
PROGRAM_ID = 'rochester-institute-of-technology-artificial-intelligence-minor-minor'
SOURCES = ('https://academiccatalog.rit.edu/programs/artificial-intelligence-minor/',)
SOURCE_ID = 'rochester-institute-of-technology-artificial-intelligence-minor-minor-curriculum'
def parse(html: str) -> dict:
    return observe(html, PROGRAM_ID, 'Artificial Intelligence', SOURCE_ID, SOURCES[0], 'rit')
