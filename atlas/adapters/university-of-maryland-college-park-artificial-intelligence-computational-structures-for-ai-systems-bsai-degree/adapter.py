"""Identity-only observation; full curriculum extraction is pending."""
from atlas.adapters.discovery_common import parse_identity

PROGRAM_ID = 'university-of-maryland-college-park-artificial-intelligence-computational-structures-for-ai-systems-bsai-degree'
SOURCES = ('https://academiccatalog.umd.edu/undergraduate/colleges-schools/computer-mathematical-natural-sciences/computer-science/artificial-intelligence-computational-structures-ai-systems-major/',)

def parse(html: str) -> dict:
    return parse_identity(html, program_id=PROGRAM_ID, title='Artificial Intelligence: Computational Structures for AI Systems', award='BSAI', kind='degree', aliases=(), award_terms=())
