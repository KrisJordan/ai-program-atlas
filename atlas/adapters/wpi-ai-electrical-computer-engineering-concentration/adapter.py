from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-electrical-computer-engineering-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-electrical-and-computer',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Electrical and Computer Engineering', SOURCES[0])
