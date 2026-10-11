from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-experience-design-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-experience-design',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Experience Design', SOURCES[0])
