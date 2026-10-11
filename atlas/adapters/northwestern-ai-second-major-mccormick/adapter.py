"""Observed AI additional-major route; reviewer audit is separate."""
from atlas.adapters import northwestern_second_majors as sources
PROGRAM_ID = 'northwestern-ai-second-major-mccormick'
SOURCES = ('https://catalogs.northwestern.edu/undergraduate/engineering-applied-science/artificial-intelligence/artificial-intelligence-second-major-mccormick/', sources.COLLEGE)
def parse(html):
    return sources.parse(html, 'mccormick')
SOURCE_PARSERS = {SOURCES[0]: parse, sources.COLLEGE: lambda html: sources.parse_college(html, 'mccormick')}

POLICY_KEYS = ['credit', 'grades', 'urr', 'pn-public', 'transfer-public']
SOURCES += tuple(sources.POLICIES[key][0] for key in POLICY_KEYS) + (sources.DUPLICATES, sources.TRANSFER_AFTER)
SOURCE_PARSERS.update({sources.POLICIES[key][0]:(lambda html,key=key:sources.parse_policy(html, 'mccormick', key)) for key in POLICY_KEYS})
SOURCE_PARSERS[sources.DUPLICATES] = lambda html: sources.parse_existing_policy(html, 'mccormick', "duplicates")
SOURCE_PARSERS[sources.TRANSFER_AFTER] = lambda html: sources.parse_existing_policy(html, 'mccormick', "transfer-after")
PDF_TEXT_PARSERS = {sources.PN_PDF:lambda text:sources.parse_pdf_text(text, 'mccormick', "pn-table"), sources.OVERLAP_PDF:lambda text:sources.parse_pdf_text(text, 'mccormick', "overlap-table")}
