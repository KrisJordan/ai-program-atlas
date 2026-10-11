from atlas.adapters.confirmed_depth3 import parse_rit_immersion
PROGRAM_ID='rit-ai-society-immersion'
SOURCES=('https://www.rit.edu/study/ai-society-immersion', 'https://www.rit.edu/study/immersions-and-minors')
def parse(html):
    return parse_rit_immersion(html)
