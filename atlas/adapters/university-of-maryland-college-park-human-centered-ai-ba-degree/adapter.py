"""Current Maryland major curriculum observation, not a degree-completeness audit."""
from atlas.adapters.maryland_ai_curricula import parse as parse_curriculum

PROGRAM_ID = 'university-of-maryland-college-park-human-centered-ai-ba-degree'
SOURCES = ('https://academiccatalog.umd.edu/undergraduate/colleges-schools/arts-humanities/philosophy/human-centered-artificial-intelligence-major/', "https://today.umd.edu/umd-to-launch-2-bachelors-degrees-to-explore-technical-human-dimensions-of-ai")

def parse(html):
    return parse_curriculum(html, pid=PROGRAM_ID, title='Human-Centered Artificial Intelligence', award='BA', url=SOURCES[0])
