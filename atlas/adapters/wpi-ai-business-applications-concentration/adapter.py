from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-business-applications-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-business-applications',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Business Applications', SOURCES[0])
