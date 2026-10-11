"""Observed AI additional-major route; reviewer audit is separate."""
from atlas.adapters import northwestern_second_majors as sources
PROGRAM_ID = 'northwestern-ai-second-major-mccormick'
SOURCES = ('https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-second-major-mccormick/', sources.COLLEGE)
def parse(html):
    return sources.parse(html, 'mccormick')
SOURCE_PARSERS = {SOURCES[0]: parse, sources.COLLEGE: lambda html: sources.parse_college(html, 'mccormick')}
