from atlas.adapters.confirmed_depth3 import parse_wpi
PROGRAM_ID='wpi-ai-optimization-decision-theory-concentration'
SOURCES=('https://wpi.cleancatalog.net/artificial-intelligence/artificial-intelligence-major-with-concentration-in-optimization-and',)
def parse(html):
    return parse_wpi(html, PROGRAM_ID, 'Artificial Intelligence Major with Concentration in Optimization and Decision Theory', SOURCES[0])
