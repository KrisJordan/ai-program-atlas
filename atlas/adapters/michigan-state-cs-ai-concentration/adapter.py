"""Official source observation; scoped completeness requires separate review."""
from atlas.adapters.confirmed_depth_batch2 import parse_msu

PROGRAM_ID = 'michigan-state-cs-ai-concentration'
SOURCE_ID = 'michigan-state-cs-ai-concentration-catalog'
SOURCES = ('https://reg.msu.edu/AcademicPrograms/ProgramDetail.aspx?PType=UGRD&Program=CMPS1_BS1',)

def parse(html: str) -> dict:
    return parse_msu(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])
