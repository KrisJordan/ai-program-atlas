"""Observe published course choices; no automatic completeness certification."""
from atlas.adapters.business_society_minors import observe
PROGRAM_ID = 'notre-dame-ai-essentials-business-minor'
SOURCES = ('https://mendoza.nd.edu/undergraduate/ai-essentials-for-business-minor/',)
SOURCE_ID = 'notre-dame-ai-essentials-business-minor-curriculum'
def parse(html: str) -> dict:
    from atlas.adapters.notre_dame_followup import inspect_additional_electives
    result = observe(html, PROGRAM_ID, 'AI Essentials for Business', SOURCE_ID, SOURCES[0], 'nd')
    result['requirements'].append(inspect_additional_electives(html, PROGRAM_ID))
    return result

from atlas.adapters.notre_dame_followup import COLLEGE_URL, parse_college
SOURCES += (COLLEGE_URL,)
SOURCE_PARSERS = {COLLEGE_URL: lambda html: parse_college(html, PROGRAM_ID)}
