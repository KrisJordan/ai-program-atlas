"""Official source observation; scoped completeness requires separate review."""
from atlas.adapters.confirmed_depth_batch2 import parse_ncsu

PROGRAM_ID = 'ncsu-computer-engineering-ai-ml-concentration'
SOURCE_ID = 'ncsu-computer-engineering-ai-ml-concentration-catalog'
SOURCES = ('https://catalog.ncsu.edu/undergraduate/engineering/electrical-computer/computer-engineering-ai-machine-learning-concentration-bs/',)

def parse(html: str) -> dict:
    return parse_ncsu(html, PROGRAM_ID, SOURCE_ID, SOURCES[0], 'Computer')
