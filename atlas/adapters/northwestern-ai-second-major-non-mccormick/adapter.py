"""Observed AI additional-major route; reviewer audit is separate."""
from atlas.adapters import northwestern_second_majors as sources
PROGRAM_ID = 'northwestern-ai-second-major-non-mccormick'
SOURCES = ('https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-second-major-non-mccormick/', sources.COLLEGE)
def parse(html):
    return sources.parse(html, 'non-mccormick')
SOURCE_PARSERS = {SOURCES[0]: parse, sources.COLLEGE: lambda html: sources.parse_college(html, 'non-mccormick')}
