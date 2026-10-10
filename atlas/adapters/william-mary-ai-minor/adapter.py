"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import ai_minor, declaration

PROGRAM_ID = 'william-mary-ai-minor'
SOURCES = ('https://cdsp.wm.edu/academics/undergraduate/ai-minor/',)

def parse(html):
    return ai_minor(html)
