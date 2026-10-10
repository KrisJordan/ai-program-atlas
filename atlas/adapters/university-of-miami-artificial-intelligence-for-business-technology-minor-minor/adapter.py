"""Observe published course choices; no automatic completeness certification."""
from atlas.adapters.business_society_minors import observe
PROGRAM_ID = 'university-of-miami-artificial-intelligence-for-business-technology-minor-minor'
SOURCES = ('https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-for-business-technology-minor/',)
SOURCE_ID = 'university-of-miami-artificial-intelligence-for-business-technology-minor-minor-curriculum'
def parse(html: str) -> dict:
    return observe(html, PROGRAM_ID, 'Artificial Intelligence for Business Technology', SOURCE_ID, SOURCES[0], 'miami')
