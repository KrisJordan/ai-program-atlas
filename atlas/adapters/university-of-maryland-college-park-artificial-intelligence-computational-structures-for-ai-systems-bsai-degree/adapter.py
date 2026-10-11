"""Current Maryland major curriculum observation, not a degree-completeness audit."""
from atlas.adapters.maryland_ai_curricula import parse as parse_curriculum
from atlas.adapters import maryland_degree_policies, maryland_course_metadata

PROGRAM_ID = 'university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'
SOURCES = ('https://academiccatalog.umd.edu/undergraduate/colleges-schools/computer-mathematical-natural-sciences/computer-science/artificial-intelligence-computational-structures-ai-systems-major/', "https://today.umd.edu/umd-to-launch-2-bachelors-degrees-to-explore-technical-human-dimensions-of-ai")
SOURCE_PARSERS = maryland_degree_policies.parsers(PROGRAM_ID)
SOURCE_PARSERS.update(maryland_course_metadata.parsers(PROGRAM_ID))
SOURCES += tuple(SOURCE_PARSERS)

def parse(html):
    return parse_curriculum(html, pid=PROGRAM_ID, title='Artificial Intelligence: Computational Structures for AI Systems', award='BSAI', url=SOURCES[0])
