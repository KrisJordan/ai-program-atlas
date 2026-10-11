"""Observe this concrete Miami degree curriculum without certifying completeness."""
from atlas.adapters.miami_degree_curricula import observe
PROGRAM_ID='university-of-miami-artificial-intelligence-technologies-for-business-other-degree'
SOURCES=('https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-tech-for-business-bba/',)
SOURCE_ID='university-of-miami-artificial-intelligence-technologies-for-business-other-degree-catalog'
def parse(html):
 return observe(html,PROGRAM_ID,'Artificial Intelligence Technologies for Business','other','B.B.A. in Artificial Intelligence Technologies for Business',SOURCE_ID,SOURCES[0])

from atlas.adapters.miami_policies import register
SOURCES=list(SOURCES)
SOURCE_PARSERS={SOURCES[0]:parse}
register(PROGRAM_ID,SOURCES,SOURCE_PARSERS,minor=False,business=True)

from atlas.adapters.miami_supplemental_policies import register as register_supplement
register_supplement(PROGRAM_ID,SOURCES,SOURCE_PARSERS,arts=False)

from atlas.adapters.miami_thematic_directory import register as register_cognate_pools
register_cognate_pools(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_bte_degree_courses import register as register_bte_metadata
register_bte_metadata(PROGRAM_ID,SOURCES,SOURCE_PARSERS)
