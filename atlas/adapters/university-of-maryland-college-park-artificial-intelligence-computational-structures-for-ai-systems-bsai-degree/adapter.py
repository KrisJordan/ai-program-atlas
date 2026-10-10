"""Current Maryland major curriculum observation, not a degree-completeness audit."""
from atlas.adapters.maryland_ai_curricula import parse as parse_curriculum

PROGRAM_ID = 'university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'
SOURCES = ('https://academiccatalog.umd.edu/undergraduate/colleges-schools/computer-mathematical-natural-sciences/computer-science/artificial-intelligence-computational-structures-ai-systems-major/', "https://today.umd.edu/umd-to-launch-2-bachelors-degrees-to-explore-technical-human-dimensions-of-ai")

def parse(html):
    return parse_curriculum(html, pid=PROGRAM_ID, title='Artificial Intelligence: Computational Structures for AI Systems', award='BSAI', url=SOURCES[0])
