"""Current Maryland major curriculum observation, not a degree-completeness audit."""
from atlas.adapters.maryland_ai_curricula import parse as parse_curriculum
from functools import partial
from atlas.adapters import maryland_degree_policies, maryland_course_metadata, maryland_language_sequences

PROGRAM_ID = 'university-of-maryland-college-park-human-centered-ai-ba-degree'
SOURCES = ('https://academiccatalog.umd.edu/undergraduate/colleges-schools/arts-humanities/philosophy/human-centered-artificial-intelligence-major/', "https://today.umd.edu/umd-to-launch-2-bachelors-degrees-to-explore-technical-human-dimensions-of-ai")
SOURCE_PARSERS = maryland_degree_policies.parsers(PROGRAM_ID, arhu=True)
SOURCE_PARSERS.update(maryland_course_metadata.parsers(PROGRAM_ID))
# This source parser needs visible viewer text; a raw Drive HTML shell fails closed.
SOURCE_PARSERS[maryland_language_sequences.URL] = partial(maryland_language_sequences.parse, pid=PROGRAM_ID)
SOURCES += tuple(SOURCE_PARSERS)

def parse(html):
    return parse_curriculum(html, pid=PROGRAM_ID, title='Human-Centered Artificial Intelligence', award='BA', url=SOURCES[0])

# Full exact-code review supersedes the earlier bounded metadata selections.
from atlas.adapters.maryland_full_course_reviews import parsers as full_course_parsers
SOURCE_PARSERS.update(full_course_parsers(PROGRAM_ID))
SOURCES=tuple(dict.fromkeys(SOURCES+tuple(SOURCE_PARSERS)))

from atlas.adapters.maryland_policy_closure import register as register_closure_policies
SOURCE_PARSERS = register_closure_policies(SOURCE_PARSERS, PROGRAM_ID)
SOURCES=tuple(dict.fromkeys(SOURCES+tuple(SOURCE_PARSERS)))

# Limited exact-title candidates remain separate from full-description reviews.
from atlas.adapters.maryland_catalog_subjects import observe as observe_catalog_subjects
parse = observe_catalog_subjects(parse)
