"""Observe this concrete Miami degree curriculum without certifying completeness."""
from atlas.adapters.miami_degree_curricula import observe
PROGRAM_ID='university-of-miami-data-science-and-artificial-intelligence-ba-degree'
SOURCES=('https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/computer-science/data-science-and-ai-ba/',)
SOURCE_ID='university-of-miami-data-science-and-artificial-intelligence-ba-degree-catalog'
def parse(html):
 return observe(html,PROGRAM_ID,'Data Science and Artificial Intelligence','BA','B.A. in Data Science and Artificial Intelligence',SOURCE_ID,SOURCES[0])

from atlas.adapters.miami_policies import register
SOURCES=list(SOURCES)
SOURCE_PARSERS={SOURCES[0]:parse}
register(PROGRAM_ID,SOURCES,SOURCE_PARSERS,minor=False,business=False)

from atlas.adapters.miami_supplemental_policies import register as register_supplement
register_supplement(PROGRAM_ID,SOURCES,SOURCE_PARSERS,arts=True)

from atlas.adapters.miami_cognate_pools import register as register_cognate_pools
register_cognate_pools(PROGRAM_ID,SOURCES,SOURCE_PARSERS)
