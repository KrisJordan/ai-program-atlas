"""Observe this concrete Miami degree curriculum without certifying completeness."""
from atlas.adapters.miami_degree_curricula import observe
PROGRAM_ID='miami-data-science-ai-bs'
SOURCES=('https://bulletin.miami.edu/undergraduate-academic-programs/arts-sciences/computer-science/data-science-and-ai-bs/',)
SOURCE_ID='miami-data-science-ai-bs-catalog'
def parse(html):
 return observe(html,PROGRAM_ID,'Data Science and Artificial Intelligence','BS','B.S. in Data Science and Artificial Intelligence',SOURCE_ID,SOURCES[0])
