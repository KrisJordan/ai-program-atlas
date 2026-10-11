"""Official source observation; scoped completeness requires separate review."""
from atlas.adapters.confirmed_depth_batch2 import parse_tamu_catalog

PROGRAM_ID = 'texas-am-ai-arts-minor'
SOURCE_ID = 'texas-am-ai-arts-minor-catalog'
SOURCES = ('https://catalog.tamu.edu/undergraduate/performance-visualization-fine-arts/artificial-intelligence-arts-minor/',)

def parse(html: str) -> dict:
    return parse_tamu_catalog(html, PROGRAM_ID, SOURCE_ID, SOURCES[0])

from functools import partial
from atlas.adapters.confirmed_depth_batch2 import parse_tamu_department
SOURCE_PARSERS = {'https://pvfa.tamu.edu/academics/visualization-program/minor-in-ai-in-the-arts/': partial(parse_tamu_department, pid=PROGRAM_ID, sid='texas-am-ai-arts-minor-department', url='https://pvfa.tamu.edu/academics/visualization-program/minor-in-ai-in-the-arts/')}
SOURCES += tuple(SOURCE_PARSERS)
