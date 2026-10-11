"""Source-specific local curriculum candidates; manual audit remains partial."""
from atlas.adapters import national_depth_curricula as curricula

PROGRAM_ID = 'umass-amherst-cs-ai-concentration'
SOURCES = ('https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/bs-ai-concentration-requirements', 'https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/bs-computer-science-degree-requirements', 'https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/credit-prior-coursework')

def parse(html):
    return curricula.parse_umass(html)

SOURCE_PARSERS = {'https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/bs-computer-science-degree-requirements': curricula.parse_umass_bs, 'https://www.cics.umass.edu/academics/academic-policies/undergraduate-programs-policies/credit-prior-coursework': curricula.parse_umass_transfer}
