"""Observe this concrete Miami degree curriculum without certifying completeness."""
from atlas.adapters.miami_degree_curricula import observe
PROGRAM_ID='miami-ai-technologies-business-bsba'
SOURCES=('https://bulletin.miami.edu/undergraduate-academic-programs/business/business-technology/ai-tech-for-business-bsba/',)
SOURCE_ID='miami-ai-technologies-business-bsba-catalog'
def parse(html):
 return observe(html,PROGRAM_ID,'Artificial Intelligence Technologies for Business','other','B.S.B.A. in Artificial Intelligence Technologies for Business',SOURCE_ID,SOURCES[0])

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

from atlas.adapters.miami_fixed_course_reviews import register as register_fixed_courses
register_fixed_courses(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_named_option_reviews import register as register_named_options
register_named_options(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_context_course_reviews import register as register_context_courses
register_context_courses(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_transfer_scope import register as register_transfer_scope
register_transfer_scope(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_eng_context_reviews import register as register_english_context
register_english_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_his_context_reviews import register as register_history_context
register_history_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_enrollment_scope import register as register_enrollment_scope
register_enrollment_scope(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_pol_context_reviews import register as register_pol_context
register_pol_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_rel_context_reviews import register as register_rel_context
register_rel_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_phi_context_reviews import register as register_phi_context
register_phi_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_apy_context_reviews import register as register_apy_context
register_apy_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_ins_context_reviews import register as register_ins_context
register_ins_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_arh_context_reviews import register as register_arh_context
register_arh_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_soc_context_reviews import register as register_soc_context
register_soc_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_cla_context_reviews import register as register_cla_context
register_cla_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_arc_context_reviews import register as register_arc_context
register_arc_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_geg_context_reviews import register as register_geg_context
register_geg_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_area_studies_context_reviews import register as register_area_studies_context
register_area_studies_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_judaic_latin_urban_context_reviews import register as register_judaic_latin_urban_context
register_judaic_latin_urban_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)

from atlas.adapters.miami_gss_context_reviews import register as register_gss_context
register_gss_context(PROGRAM_ID,SOURCES,SOURCE_PARSERS)
