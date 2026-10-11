from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-social-science-policy-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-social-science-and',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Social Science and Policy Concentration', SOURCES[0])
