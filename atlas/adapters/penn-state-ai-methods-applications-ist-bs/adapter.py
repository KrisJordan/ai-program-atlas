from atlas.adapters.confirmed_depth3 import parse_psu
PROGRAM_ID='penn-state-ai-methods-applications-ist-bs'
SOURCES=('https://bulletins.psu.edu/undergraduate/colleges/information-sciences-technology/artificial-intelligence-methods-applications-bs/',)
def parse(html):
    return parse_psu(html, PROGRAM_ID, 'Artificial Intelligence Methods and Applications, B.S. (Information Sciences and Technology)', 'AIMA_BS')
