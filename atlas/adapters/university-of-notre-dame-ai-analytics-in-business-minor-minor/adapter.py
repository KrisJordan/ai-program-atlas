"""Observe published course choices; no automatic completeness certification."""
from atlas.adapters.business_society_minors import observe
PROGRAM_ID = 'university-of-notre-dame-ai-analytics-in-business-minor-minor'
SOURCES = ('https://mendoza.nd.edu/undergraduate/ai-analytics-in-business/',)
SOURCE_ID = 'university-of-notre-dame-ai-analytics-in-business-minor-minor-curriculum'
def parse(html: str) -> dict:
    return observe(html, PROGRAM_ID, 'AI Analytics in Business', SOURCE_ID, SOURCES[0], 'nd')
