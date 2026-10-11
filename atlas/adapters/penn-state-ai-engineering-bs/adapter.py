from atlas.adapters.confirmed_depth3 import parse_psu
PROGRAM_ID='penn-state-ai-engineering-bs'
SOURCES=('https://bulletins.psu.edu/undergraduate/colleges/engineering/artificial-intelligence-engineering-bs/',)
def parse(html):
    return parse_psu(html, PROGRAM_ID, 'Artificial Intelligence Engineering, B.S.', 'AIE_BS')
