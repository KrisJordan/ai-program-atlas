"""Official source observation; scoped completeness requires separate review."""
from atlas.adapters.confirmed_depth_batch2 import parse_ncsu

PROGRAM_ID = 'ncsu-electrical-engineering-ai-ml-concentration'
SOURCE_ID = 'ncsu-electrical-engineering-ai-ml-concentration-catalog'
SOURCES = ('https://catalog.ncsu.edu/undergraduate/engineering/electrical-computer/electrical-engineering-bs-ai-machine-learning-concentration/',)

def parse(html: str) -> dict:
    return parse_ncsu(html, PROGRAM_ID, SOURCE_ID, SOURCES[0], 'Electrical')
