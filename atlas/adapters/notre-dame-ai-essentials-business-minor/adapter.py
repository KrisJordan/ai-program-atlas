"""Observe published course choices; no automatic completeness certification."""
from atlas.adapters.business_society_minors import observe
PROGRAM_ID = 'notre-dame-ai-essentials-business-minor'
SOURCES = ('https://mendoza.nd.edu/undergraduate/ai-essentials-for-business-minor/',)
SOURCE_ID = 'notre-dame-ai-essentials-business-minor-curriculum'
def parse(html: str) -> dict:
    return observe(html, PROGRAM_ID, 'AI Essentials for Business', SOURCE_ID, SOURCES[0], 'nd')
