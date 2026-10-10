"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'michigan-state-university-artificial-intelligence-minor-minor'
SOURCES = ('https://reg.msu.edu/ACADEMICPROGRAMS/ProgramDetail.aspx?PType=MNUN&Program=AINTL_MNUN',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence', award='minor', kind='minor', aliases=(), award_terms=())
