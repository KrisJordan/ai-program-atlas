"""Extract department curriculum observations; catalog review remains partial."""
from atlas.adapters.william_mary_curricula import cs_concentration, declaration

PROGRAM_ID = 'william-mary-cs-ai-ml-concentration'
SOURCES = ('https://cdsp.wm.edu/computerscience/undergraduate/bachelor-of-science-b.s-in-computer-science.php?mapstat=1',)

def parse(html):
    return cs_concentration(html)
