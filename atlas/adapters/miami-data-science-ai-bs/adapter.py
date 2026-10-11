"""Observe this concrete Miami degree curriculum without certifying completeness."""
from atlas.adapters.miami_degree_curricula import observe
PROGRAM_ID='miami-data-science-ai-bs'
SOURCES=('https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/computer-science/data-science-and-ai-bs/',)
SOURCE_ID='miami-data-science-ai-bs-catalog'
def parse(html):
 return observe(html,PROGRAM_ID,'Data Science and Artificial Intelligence','BS','B.S. in Data Science and Artificial Intelligence',SOURCE_ID,SOURCES[0])

from atlas.adapters.miami_policies import register
SOURCES=list(SOURCES)
SOURCE_PARSERS={SOURCES[0]:parse}
register(PROGRAM_ID,SOURCES,SOURCE_PARSERS,minor=False,business=False)

from atlas.adapters.miami_supplemental_policies import register as register_supplement
register_supplement(PROGRAM_ID,SOURCES,SOURCE_PARSERS,arts=True)

from atlas.adapters.miami_thematic_directory import register as register_cognate_pools
register_cognate_pools(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_fixed_course_reviews import register as register_fixed_courses
register_fixed_courses(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_named_option_reviews import register as register_named_options
register_named_options(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_csc_option_reviews import register as register_csc_options
register_csc_options(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_context_course_reviews import register as register_context_courses
register_context_courses(PROGRAM_ID,SOURCES,SOURCE_PARSERS)
