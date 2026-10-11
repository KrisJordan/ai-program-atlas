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

from atlas.adapters.miami_transfer_scope import register as register_transfer_scope
register_transfer_scope(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_bs_policy_scope import apply as apply_bs_requirement_scope
_parse_bs_table=parse
def parse(html):
    return apply_bs_requirement_scope(_parse_bs_table(html))
SOURCE_PARSERS[SOURCES[0]]=parse

from atlas.adapters.miami_eng_context_reviews import register as register_english_context
register_english_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_his_context_reviews import register as register_history_context
register_history_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_enrollment_scope import register as register_enrollment_scope
register_enrollment_scope(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_pol_context_reviews import register as register_pol_context
register_pol_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)
