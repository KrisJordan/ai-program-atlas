from atlas.adapters.confirmed_depth3 import parse_delaware
PROGRAM_ID='delaware-cs-ai-robotics-concentration'
SOURCES=('https://www.cis.udel.edu/academics/undergraduate-programs/bscs/',)
def parse(html):
    return parse_delaware(html)
