"""Identity refresh plus reviewed public handbook and course-table observations."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-michigan-ann-arbor-human-centered-artificial-intelligence-minor-minor'
SOURCES = ('https://www.si.umich.edu/programs/undergraduate-minors/human-centered-artificial-intelligence',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Human-Centered Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())

from atlas.adapters.umich_hcai import HANDBOOK, TABLE, parse_handbook, parse_table
SOURCES = (*SOURCES, HANDBOOK, TABLE)
SOURCE_PARSERS = {HANDBOOK: parse_handbook, TABLE: parse_table}
